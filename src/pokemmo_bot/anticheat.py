"""Anti-detection utilities and human behavior simulation."""

from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pokemmo_bot.config import AntiDetectConfig

logger = logging.getLogger(__name__)


def should_afk(config: AntiDetectConfig) -> bool:
    """Decide if the bot should take an AFK pause this round.

    Args:
        config: Anti-detection configuration.

    Returns:
        True if an AFK pause should occur.
    """
    return random.random() < config.afk_chance


def should_hesitate(config: AntiDetectConfig) -> bool:
    """Decide if the bot should hesitate before attacking.

    Args:
        config: Anti-detection configuration.

    Returns:
        True if a hesitation pause should occur.
    """
    return random.random() < config.hesitation_chance


def choose_walk_pattern(
    config: AntiDetectConfig,
    consecutive_left: int,
    consecutive_right: int,
) -> str:
    """Choose walking direction with pattern variance.

    Avoids simple left-right alternation which is easily detectable.
    Uses weighted randomness that favors breaking long streaks.

    Args:
        config: Anti-detection configuration.
        consecutive_left: Current consecutive left walks.
        consecutive_right: Current consecutive right walks.

    Returns:
        "left" or "right"
    """
    max_streak = config.max_consecutive_walks

    # If streak is getting long, heavily favor the other direction
    if consecutive_left >= max_streak:
        return "right"
    if consecutive_right >= max_streak:
        return "left"

    # Weighted random: slightly favor breaking streaks
    left_weight = 1.0
    right_weight = 1.0

    if consecutive_left > consecutive_right:
        right_weight = 1.0 + (consecutive_left - consecutive_right) * 0.3
    elif consecutive_right > consecutive_left:
        left_weight = 1.0 + (consecutive_right - consecutive_left) * 0.3

    # Add some pure randomness (20% chance of random choice)
    if random.random() < 0.2:
        return random.choice(["left", "right"])

    return random.choices(["left", "right"], weights=[left_weight, right_weight])[0]


def should_use_different_slot(base_slot: int) -> int:
    """Occasionally use a different attack slot to appear less robotic.

    Real players sometimes misclick or choose different moves.

    Args:
        base_slot: The configured attack slot.

    Returns:
        The slot to actually use (base_slot most of the time).
    """
    # 5% chance to "accidentally" pick a different slot
    if random.random() < 0.05:
        alternatives = [s for s in [1, 2, 3, 4] if s != base_slot]
        chosen = random.choice(alternatives)
        logger.debug("Anti-detect: using alternate slot %d instead of %d", chosen, base_slot)
        return chosen
    return base_slot


def random_extra_pause(config: AntiDetectConfig) -> None:
    """Add occasional extra-long pauses to simulate AFK moments.

    Args:
        config: Anti-detection configuration.
    """
    if should_afk(config):
        duration = random.uniform(config.afk_min, config.afk_max)
        logger.debug("Anti-detect: AFK pause for %.1fs", duration)
        time.sleep(duration)
