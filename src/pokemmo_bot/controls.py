"""Input simulation with anti-detection timing patterns."""

from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

import pydirectinput

if TYPE_CHECKING:
    from pokemmo_bot.config import AntiDetectConfig, KeyBindings

logger = logging.getLogger(__name__)


def human_pause(
    min_sec: float = 0.3,
    max_sec: float = 1.2,
    std_dev: float = 0.15,
) -> None:
    """Sleep for a human-like duration using gaussian distribution.

    Most humans have consistent timing with occasional variation.
    Gaussian distribution better mimics this than uniform.

    Args:
        min_sec: Minimum pause duration.
        max_sec: Maximum pause duration.
        std_dev: Standard deviation for gaussian timing.
    """
    mean = (min_sec + max_sec) / 2.0
    duration = random.gauss(mean, std_dev)
    # Clamp to min/max bounds
    duration = max(min_sec, min(max_sec, duration))
    time.sleep(duration)


def micro_move(chance: float = 0.15) -> None:
    """Occasionally perform a tiny random movement to seem more human.

    Real players sometimes shift slightly or fidget. This adds realism.

    Args:
        chance: Probability (0.0-1.0) of performing a micro-movement.
    """
    if random.random() > chance:
        return

    key = random.choice(["up", "down", "left", "right"])
    pydirectinput.keyDown(key)
    human_pause(0.05, 0.12, std_dev=0.02)
    pydirectinput.keyUp(key)
    logger.debug("Micro-movement: %s", key)


def press_key(key: str, hold_time: float | None = None) -> None:
    """Press a key with optional hold duration.

    Args:
        key: Key name to press.
        hold_time: How long to hold the key. If None, just a quick press.
    """
    if hold_time is not None:
        pydirectinput.keyDown(key)
        human_pause(hold_time * 0.8, hold_time * 1.2, std_dev=hold_time * 0.1)
        pydirectinput.keyUp(key)
    else:
        pydirectinput.press(key)


def navigate_attack_menu(slot: int, keys: KeyBindings) -> None:
    """Navigate the 2x2 attack grid to select the desired move.

    Args:
        slot: Attack slot (1=TopLeft, 2=TopRight, 3=BottomLeft, 4=BottomRight).
        keys: Key bindings configuration.
    """
    logger.info("Selecting attack slot %d", slot)

    # Open the fight menu
    press_key(keys.action)
    human_pause(0.4, 0.7, std_dev=0.08)

    # Navigate to the correct slot
    if slot == 2:
        press_key(keys.right)
    elif slot == 3:
        press_key(keys.down)
    elif slot == 4:
        press_key(keys.right)
        human_pause(0.08, 0.15, std_dev=0.02)
        press_key(keys.down)

    # Small pause before confirming (mimics human reading)
    human_pause(0.15, 0.35, std_dev=0.05)

    # Confirm selection
    press_key(keys.action)


def walk_direction(direction: str, keys: KeyBindings, config: AntiDetectConfig) -> None:
    """Walk in a direction with human-like timing.

    Args:
        direction: "left" or "right".
        keys: Key bindings.
        config: Anti-detection configuration.
    """
    key = keys.left if direction == "left" else keys.right
    duration = random.uniform(config.move_min, config.move_max)

    logger.debug("Walking %s for %.2fs", direction, duration)
    pydirectinput.keyDown(key)
    human_pause(
        duration * 0.85,
        duration * 1.15,
        std_dev=duration * 0.08,
    )
    pydirectinput.keyUp(key)

    # Occasional micro-movement after walking
    micro_move(config.micro_move_chance)


def skip_dialogs(
    cancel_key: str,
    count: int | None = None,
    config: AntiDetectConfig | None = None,
) -> None:
    """Press cancel repeatedly to skip post-battle text/dialog.

    Args:
        cancel_key: The cancel key to press.
        count: Number of times to press. If None, uses config range.
        config: Anti-detection config for random count.
    """
    if count is None and config is not None:
        count = random.randint(config.extra_cancels_min, config.extra_cancels_max)
    elif count is None:
        count = 3

    for _ in range(count):
        press_key(cancel_key)
        human_pause(0.2, 0.5, std_dev=0.08)
