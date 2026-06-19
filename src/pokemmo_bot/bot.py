"""Main bot state machine with anti-detection logic."""

from __future__ import annotations

import logging
import sys
from enum import Enum, auto

import keyboard
import pydirectinput

from pokemmo_bot.anticheat import (
    choose_walk_pattern,
    random_extra_pause,
    should_hesitate,
    should_use_different_slot,
)
from pokemmo_bot.config import BotConfig, load_config
from pokemmo_bot.controls import (
    human_pause,
    navigate_attack_menu,
    press_key,
    skip_dialogs,
    walk_direction,
)
from pokemmo_bot.vision import detect_battle_menu

logger = logging.getLogger(__name__)


class BotState(Enum):
    """Bot operational states."""

    PATROL = auto()
    COMBAT = auto()
    LOW_PP = auto()
    STOPPED = auto()


class PokeBot:
    """Main bot controller with state machine and anti-detection."""

    def __init__(self, config: BotConfig | None = None) -> None:
        self.config = config or load_config()
        self.state = BotState.PATROL
        self.pp_remaining = self.config.pp_max
        self._consecutive_left = 0
        self._consecutive_right = 0
        self._combat_count = 0

        logger.info(
            "Bot initialized: PP=%d, attack_slot=%d",
            self.pp_remaining,
            self.config.attack_slot,
        )

    def _check_kill_switch(self) -> bool:
        """Check if user pressed Q to stop the bot."""
        if keyboard.is_pressed("q"):
            logger.info("Kill switch activated by user")
            self.state = BotState.STOPPED
            return True
        return False

    def _detect_battle(self) -> bool:
        """Detect battle menu with anti-detection jitter."""
        cfg = self.config.anti_detect
        return detect_battle_menu(
            confidence=self.config.vision_confidence,
            jitter=cfg.confidence_jitter,
        )

    def _handle_patrol(self) -> None:
        """Patrol state: walk around to trigger encounters."""
        if self._check_kill_switch():
            return

        if self._detect_battle():
            self.state = BotState.COMBAT
            return

        # Choose direction with anti-detect pattern
        direction = choose_walk_pattern(
            self.config.anti_detect,
            self._consecutive_left,
            self._consecutive_right,
        )

        walk_direction(direction, self.config.keys, self.config.anti_detect)

        if direction == "left":
            self._consecutive_left += 1
            self._consecutive_right = 0
        else:
            self._consecutive_right += 1
            self._consecutive_left = 0

    def _handle_combat(self) -> None:
        """Combat state: fight the encountered Pokémon."""
        self._combat_count += 1
        logger.info("=== Combat #%d started ===", self._combat_count)

        while True:
            if self._check_kill_switch():
                return

            if self.pp_remaining <= 0:
                logger.warning("PP depleted! Entering LOW_PP state")
                self.state = BotState.LOW_PP
                return

            # Wait for the battle menu to be visible (with timeout)
            menu_visible = self._wait_for_battle_menu(max_attempts=20)
            if not menu_visible:
                logger.info("No battle menu found after waiting, combat likely ended")
                break

            # Anti-detect: occasionally use different attack slot
            slot = should_use_different_slot(self.config.attack_slot)

            # Anti-detect: hesitate before attacking sometimes
            if should_hesitate(self.config.anti_detect):
                logger.debug("Hesitating before attack...")
                human_pause(
                    self.config.anti_detect.hesitation_min,
                    self.config.anti_detect.hesitation_max,
                )

            # Execute attack
            navigate_attack_menu(slot, self.config.keys)
            self.pp_remaining -= 1
            logger.info(
                "Attack executed. PP remaining: %d/%d",
                self.pp_remaining,
                self.config.pp_max,
            )

            # Wait for attack animation and turn to resolve
            human_pause(2.5, 3.5, std_dev=0.3)

            # Press cancel to advance text/dialogs
            self._wait_for_next_turn()

            # Anti-detect: random AFK pause
            random_extra_pause(self.config.anti_detect)

            # Small stabilization pause
            human_pause(0.4, 0.8, std_dev=0.1)

        # Skip post-battle dialogs
        skip_dialogs(self.config.keys.cancel, config=self.config.anti_detect)

        logger.info("Combat #%d finished", self._combat_count)
        self.state = BotState.PATROL

    def _wait_for_next_turn(self) -> None:
        """Wait for next turn by pressing cancel and checking for menu return."""
        timeout = self.config.combat_timeout

        for i in range(timeout):
            if self._check_kill_switch():
                return

            if self._detect_battle():
                logger.debug("Menu returned after %d iterations", i)
                return

            # Press cancel to advance text
            press_key(self.config.keys.cancel)
            human_pause(0.7, 1.1, std_dev=0.12)

        logger.debug("Combat timeout reached, assuming victory")

    def _wait_for_battle_menu(self, max_attempts: int = 20) -> bool:
        """Wait for the battle menu to appear on screen.

        Args:
            max_attempts: Maximum number of detection attempts.

        Returns:
            True if battle menu detected, False if timed out.
        """
        for i in range(max_attempts):
            if self._detect_battle():
                logger.debug("Battle menu detected on attempt %d", i)
                return True
            human_pause(0.3, 0.6, std_dev=0.05)
        return False

    def _handle_low_pp(self) -> None:
        """Low PP state: bot is out of resources."""
        logger.warning(
            "Bot stopped: PP depleted (%d/%d used)",
            self.config.pp_max - self.pp_remaining,
            self.config.pp_max,
        )
        self.state = BotState.STOPPED

    def run(self) -> None:
        """Main bot loop."""
        logger.info("Bot starting in 3 seconds... Press Q to stop.")
        human_pause(3.0, 3.0, std_dev=0.0)

        state_handlers = {
            BotState.PATROL: self._handle_patrol,
            BotState.COMBAT: self._handle_combat,
            BotState.LOW_PP: self._handle_low_pp,
        }

        try:
            while self.state != BotState.STOPPED:
                handler = state_handlers.get(self.state)
                if handler is None:
                    logger.error("Unknown state: %s", self.state)
                    break
                handler()

            logger.info("Bot stopped. Total combats: %d", self._combat_count)

        except KeyboardInterrupt:
            logger.info("Interrupted by user (Ctrl+C)")
        except Exception:
            logger.critical("Unexpected error", exc_info=True)
            raise
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Release any held keys."""
        try:
            pydirectinput.keyUp("left")
            pydirectinput.keyUp("right")
            pydirectinput.keyUp("up")
            pydirectinput.keyUp("down")
        except Exception:
            pass


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the bot."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main(config_path: str | None = None) -> None:
    """Entry point for the bot.

    Args:
        config_path: Optional path to YAML config file.
    """
    pydirectinput.FAILSAFE = False
    setup_logging()
    config = load_config(config_path)
    bot = PokeBot(config)
    bot.run()


if __name__ == "__main__":
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(cfg_path)
