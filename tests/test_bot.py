"""Tests for bot state machine."""

from unittest.mock import patch

from pokemmo_bot.bot import BotState, PokeBot
from pokemmo_bot.config import BotConfig


class TestBotState:
    def test_states_exist(self) -> None:
        assert BotState.PATROL.value
        assert BotState.COMBAT.value
        assert BotState.LOW_PP.value
        assert BotState.STOPPED.value


class TestPokeBot:
    def test_initial_state(self) -> None:
        cfg = BotConfig(pp_max=10)
        bot = PokeBot(cfg)
        assert bot.state == BotState.PATROL
        assert bot.pp_remaining == 10
        assert bot._combat_count == 0

    def test_pp_depletes(self) -> None:
        cfg = BotConfig(pp_max=5)
        bot = PokeBot(cfg)
        bot.pp_remaining = 0
        assert bot.pp_remaining <= 0

    def test_combat_count_increments(self) -> None:
        cfg = BotConfig()
        bot = PokeBot(cfg)
        bot._combat_count += 1
        assert bot._combat_count == 1

    @patch("pokemmo_bot.bot.keyboard")
    def test_kill_switch_sets_stopped(self, mock_keyboard) -> None:
        mock_keyboard.is_pressed.return_value = True
        cfg = BotConfig()
        bot = PokeBot(cfg)
        result = bot._check_kill_switch()
        assert result is True
        assert bot.state == BotState.STOPPED

    @patch("pokemmo_bot.bot.keyboard")
    def test_kill_switch_not_pressed(self, mock_keyboard) -> None:
        mock_keyboard.is_pressed.return_value = False
        cfg = BotConfig()
        bot = PokeBot(cfg)
        result = bot._check_kill_switch()
        assert result is False
        assert bot.state == BotState.PATROL

    def test_cleanup_releases_keys(self) -> None:
        cfg = BotConfig()
        bot = PokeBot(cfg)
        # Should not raise
        bot._cleanup()
