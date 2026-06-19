"""Configuration management with dataclass and YAML support."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
CONFIG_DIR = Path(__file__).parent.parent.parent


@dataclass(frozen=True)
class KeyBindings:
    """Keyboard key mappings for game controls."""

    action: str = "z"
    cancel: str = "x"
    up: str = "up"
    down: str = "down"
    left: str = "left"
    right: str = "right"


@dataclass(frozen=True)
class AntiDetectConfig:
    """Timing configuration to avoid detection."""

    # Base pause ranges in seconds
    min_pause: float = 0.3
    max_pause: float = 1.2

    # Gaussian timing parameters
    timing_stddev: float = 0.15
    timing_mean: float = 0.0

    # Movement timing
    move_min: float = 0.4
    move_max: float = 0.9

    # Micro-movement probability (0.0 - 1.0)
    micro_move_chance: float = 0.15

    # AFK pause probability per combat round
    afk_chance: float = 0.08
    afk_min: float = 2.0
    afk_max: float = 6.0

    # Hesitation before attack (presses action, then small delay)
    hesitation_chance: float = 0.12
    hesitation_min: float = 0.3
    hesitation_max: float = 0.8

    # Extra cancel presses after battle
    extra_cancels_min: int = 1
    extra_cancels_max: int = 4

    # Confidence jitter for vision detection
    confidence_jitter: float = 0.05

    # Max consecutive same-direction walks
    max_consecutive_walks: int = 5


@dataclass(frozen=True)
class BotConfig:
    """Main bot configuration."""

    attack_slot: int = 3
    pp_max: int = 25
    vision_confidence: float = 0.8
    combat_timeout: int = 15
    keys: KeyBindings = field(default_factory=KeyBindings)
    anti_detect: AntiDetectConfig = field(default_factory=AntiDetectConfig)


def _merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge override into base dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _dict_to_config(data: dict[str, Any]) -> BotConfig:
    """Convert a flat/nested dict to BotConfig dataclass."""
    keys_data = data.pop("keys", {})
    anti_data = data.pop("anti_detect", {})

    keys = KeyBindings(**keys_data) if keys_data else KeyBindings()
    anti = AntiDetectConfig(**anti_data) if anti_data else AntiDetectConfig()

    return BotConfig(keys=keys, anti_detect=anti, **data)


def load_config(config_path: Path | str | None = None) -> BotConfig:
    """Load configuration from YAML file, falling back to defaults.

    Args:
        config_path: Path to YAML config file. If None, uses config.yaml in project root.

    Returns:
        Merged BotConfig with defaults applied.
    """
    config_path = CONFIG_DIR / "config.yaml" if config_path is None else Path(config_path)

    defaults: dict[str, Any] = {
        "attack_slot": BotConfig.attack_slot,
        "pp_max": BotConfig.pp_max,
        "vision_confidence": BotConfig.vision_confidence,
        "combat_timeout": BotConfig.combat_timeout,
    }

    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            merged = _merge_dict(defaults, user_config)
            logger.info("Config loaded from %s", config_path)
            return _dict_to_config(merged)
        except Exception:
            logger.warning(
                "Failed to load config from %s, using defaults",
                config_path,
                exc_info=True,
            )
    else:
        logger.info("No config file found at %s, using defaults", config_path)

    return BotConfig()
