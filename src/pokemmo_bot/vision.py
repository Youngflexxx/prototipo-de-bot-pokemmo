"""Screen vision and UI element detection."""

from __future__ import annotations

import logging
import random

import pyautogui

from pokemmo_bot.config import ASSETS_DIR

logger = logging.getLogger(__name__)

# Cache the reference image path
_BATTLE_BUTTON_IMAGE = ASSETS_DIR / "boton_luchar.png"


def detect_battle_menu(confidence: float = 0.8, jitter: float = 0.05) -> bool:
    """Detect if the battle menu (Fight button) is visible on screen.

    Args:
        confidence: Base confidence threshold for template matching (0.0 - 1.0).
        jitter: Random jitter applied to confidence to vary detection sensitivity.

    Returns:
        True if the fight button is found on screen, False otherwise.
    """
    if not _BATTLE_BUTTON_IMAGE.exists():
        logger.error("Reference image not found: %s", _BATTLE_BUTTON_IMAGE)
        return False

    # Apply slight confidence jitter for anti-detection
    effective_confidence = max(0.5, min(1.0, confidence + random.uniform(-jitter, jitter)))

    try:
        location = pyautogui.locateOnScreen(
            str(_BATTLE_BUTTON_IMAGE),
            confidence=effective_confidence,
        )
        if location is not None:
            logger.debug("Battle menu detected at %s (conf=%.2f)", location, effective_confidence)
            return True
        return False
    except pyautogui.ImageNotFoundException:
        return False
    except Exception:
        logger.warning("Vision detection failed unexpectedly", exc_info=True)
        return False
