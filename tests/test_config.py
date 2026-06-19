"""Tests for configuration loading."""

from pathlib import Path

import pytest

from pokemmo_bot.config import (
    AntiDetectConfig,
    BotConfig,
    KeyBindings,
    load_config,
)


class TestKeyBindings:
    def test_default_values(self) -> None:
        kb = KeyBindings()
        assert kb.action == "z"
        assert kb.cancel == "x"
        assert kb.up == "up"
        assert kb.down == "down"
        assert kb.left == "left"
        assert kb.right == "right"

    def test_custom_values(self) -> None:
        kb = KeyBindings(action="a", cancel="b")
        assert kb.action == "a"
        assert kb.cancel == "b"

    def test_immutable(self) -> None:
        kb = KeyBindings()
        with pytest.raises(AttributeError):
            kb.action = "x"  # type: ignore[misc]


class TestAntiDetectConfig:
    def test_default_values(self) -> None:
        cfg = AntiDetectConfig()
        assert cfg.min_pause == 0.3
        assert cfg.max_pause == 1.2
        assert cfg.afk_chance == 0.08
        assert cfg.hesitation_chance == 0.12
        assert cfg.max_consecutive_walks == 5

    def test_custom_values(self) -> None:
        cfg = AntiDetectConfig(afk_chance=0.5, afk_min=10.0, afk_max=20.0)
        assert cfg.afk_chance == 0.5
        assert cfg.afk_min == 10.0
        assert cfg.afk_max == 20.0


class TestBotConfig:
    def test_default_values(self) -> None:
        cfg = BotConfig()
        assert cfg.attack_slot == 3
        assert cfg.pp_max == 25
        assert cfg.vision_confidence == 0.8
        assert cfg.combat_timeout == 15
        assert isinstance(cfg.keys, KeyBindings)
        assert isinstance(cfg.anti_detect, AntiDetectConfig)

    def test_immutable(self) -> None:
        cfg = BotConfig()
        with pytest.raises(AttributeError):
            cfg.attack_slot = 1  # type: ignore[misc]


class TestLoadConfig:
    def test_load_with_no_file(self, tmp_path: Path) -> None:
        cfg = load_config(tmp_path / "nonexistent.yaml")
        assert cfg.attack_slot == 3
        assert cfg.pp_max == 25

    def test_load_from_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "attack_slot: 2\n"
            "pp_max: 50\n"
            "keys:\n"
            "  action: a\n"
            "  cancel: b\n"
        )
        cfg = load_config(config_file)
        assert cfg.attack_slot == 2
        assert cfg.pp_max == 50
        assert cfg.keys.action == "a"
        assert cfg.keys.cancel == "b"

    def test_load_with_anti_detect(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "anti_detect:\n"
            "  afk_chance: 0.99\n"
            "  afk_min: 5.0\n"
        )
        cfg = load_config(config_file)
        assert cfg.anti_detect.afk_chance == 0.99
        assert cfg.anti_detect.afk_min == 5.0

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")
        cfg = load_config(config_file)
        assert cfg.attack_slot == 3

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(": invalid: yaml: {{{}}}:")
        cfg = load_config(config_file)
        # Falls back to defaults
        assert cfg.attack_slot == 3
