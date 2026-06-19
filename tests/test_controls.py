"""Tests for controls module."""

import time
from unittest.mock import patch

from pokemmo_bot.config import AntiDetectConfig, KeyBindings
from pokemmo_bot.controls import human_pause, micro_move, navigate_attack_menu, skip_dialogs


class TestHumanPause:
    def test_sleeps_within_bounds(self) -> None:
        start = time.monotonic()
        human_pause(0.01, 0.02, std_dev=0.005)
        elapsed = time.monotonic() - start
        assert 0.005 < elapsed < 0.05

    def test_gaussian_distribution(self) -> None:
        """Test that pauses cluster around the mean."""
        durations = []
        for _ in range(100):
            start = time.monotonic()
            human_pause(0.01, 0.03, std_dev=0.003)
            durations.append(time.monotonic() - start)
        avg = sum(durations) / len(durations)
        # Average should be close to midpoint (0.02)
        assert 0.01 < avg < 0.04


class TestMicroMove:
    @patch("pokemmo_bot.controls.pydirectinput")
    def test_no_move_when_chance_fails(self, mock_input) -> None:
        """When random > chance, no key should be pressed."""
        import random
        random.seed(42)  # Deterministic seed that won't trigger
        micro_move(chance=0.0)
        mock_input.keyDown.assert_not_called()
        mock_input.keyUp.assert_not_called()

    @patch("pokemmo_bot.controls.pydirectinput")
    @patch("pokemmo_bot.controls.human_pause")
    def test_move_when_chance_triggers(self, mock_pause, mock_input) -> None:
        """When random < chance, a key should be pressed."""
        import random
        random.seed(0)  # This should trigger with chance=1.0
        micro_move(chance=1.0)
        mock_input.keyDown.assert_called_once()
        mock_input.keyUp.assert_called_once()


class TestNavigateAttackMenu:
    @patch("pokemmo_bot.controls.pydirectinput")
    @patch("pokemmo_bot.controls.human_pause")
    def test_slot_1_no_movement(self, mock_pause, mock_input) -> None:
        """Slot 1 (top-left) should only press action twice."""
        keys = KeyBindings()
        navigate_attack_menu(1, keys)
        # Should press action to open menu, then action to confirm
        assert mock_input.press.call_count == 2

    @patch("pokemmo_bot.controls.pydirectinput")
    @patch("pokemmo_bot.controls.human_pause")
    def test_slot_2_moves_right(self, mock_pause, mock_input) -> None:
        """Slot 2 (top-right) should press right."""
        keys = KeyBindings()
        navigate_attack_menu(2, keys)
        calls = [str(c) for c in mock_input.press.call_args_list]
        assert any("right" in c for c in calls)

    @patch("pokemmo_bot.controls.pydirectinput")
    @patch("pokemmo_bot.controls.human_pause")
    def test_slot_3_moves_down(self, mock_pause, mock_input) -> None:
        """Slot 3 (bottom-left) should press down."""
        keys = KeyBindings()
        navigate_attack_menu(3, keys)
        calls = [str(c) for c in mock_input.press.call_args_list]
        assert any("down" in c for c in calls)

    @patch("pokemmo_bot.controls.pydirectinput")
    @patch("pokemmo_bot.controls.human_pause")
    def test_slot_4_moves_right_and_down(self, mock_pause, mock_input) -> None:
        """Slot 4 (bottom-right) should press right and down."""
        keys = KeyBindings()
        navigate_attack_menu(4, keys)
        calls = [str(c) for c in mock_input.press.call_args_list]
        assert any("right" in c for c in calls)
        assert any("down" in c for c in calls)


class TestSkipDialogs:
    @patch("pokemmo_bot.controls.pydirectinput")
    @patch("pokemmo_bot.controls.human_pause")
    def test_specific_count(self, mock_pause, mock_input) -> None:
        skip_dialogs("x", count=3)
        assert mock_input.press.call_count == 3

    @patch("pokemmo_bot.controls.pydirectinput")
    @patch("pokemmo_bot.controls.human_pause")
    def test_config_based_count(self, mock_pause, mock_input) -> None:
        cfg = AntiDetectConfig(extra_cancels_min=2, extra_cancels_max=2)
        skip_dialogs("x", config=cfg)
        assert mock_input.press.call_count == 2
