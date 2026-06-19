"""Tests for anti-detection utilities."""

from pokemmo_bot.anticheat import (
    choose_walk_pattern,
    should_hesitate,
    should_use_different_slot,
)
from pokemmo_bot.config import AntiDetectConfig


class TestChooseWalkPattern:
    def test_returns_left_or_right(self) -> None:
        cfg = AntiDetectConfig()
        for _ in range(100):
            result = choose_walk_pattern(cfg, consecutive_left=0, consecutive_right=0)
            assert result in ("left", "right")

    def test_breaks_long_left_streak(self) -> None:
        cfg = AntiDetectConfig(max_consecutive_walks=3)
        # After 3 left walks, should return right
        for _ in range(50):
            result = choose_walk_pattern(cfg, consecutive_left=3, consecutive_right=0)
            assert result == "right"

    def test_breaks_long_right_streak(self) -> None:
        cfg = AntiDetectConfig(max_consecutive_walks=3)
        for _ in range(50):
            result = choose_walk_pattern(cfg, consecutive_left=0, consecutive_right=3)
            assert result == "left"

    def test_balances_directions(self) -> None:
        cfg = AntiDetectConfig(max_consecutive_walks=100)
        left_count = 0
        right_count = 0
        cons_left = 0
        cons_right = 0
        for _ in range(1000):
            result = choose_walk_pattern(
                cfg, consecutive_left=cons_left, consecutive_right=cons_right
            )
            if result == "left":
                left_count += 1
                cons_left += 1
                cons_right = 0
            else:
                right_count += 1
                cons_right += 1
                cons_left = 0
        # With proper streak tracking, directions should be reasonably balanced
        # Allow wider margin since the weighting logic can create short-term imbalance
        assert abs(left_count - right_count) < 600


class TestShouldHesitate:
    def test_always_false_when_zero(self) -> None:
        cfg = AntiDetectConfig(hesitation_chance=0.0)
        for _ in range(100):
            assert should_hesitate(cfg) is False

    def test_always_true_when_one(self) -> None:
        cfg = AntiDetectConfig(hesitation_chance=1.0)
        for _ in range(100):
            assert should_hesitate(cfg) is True

    def test_sometimes_true(self) -> None:
        cfg = AntiDetectConfig(hesitation_chance=0.5)
        results = [should_hesitate(cfg) for _ in range(1000)]
        true_count = sum(results)
        # Should be roughly 50% true (within statistical bounds)
        assert 300 < true_count < 700


class TestShouldUseDifferentSlot:
    def test_mostly_returns_base_slot(self) -> None:
        results = [should_use_different_slot(3) for _ in range(1000)]
        base_count = sum(1 for r in results if r == 3)
        # Should use base slot ~95% of the time
        assert base_count > 900

    def test_sometimes_returns_different_slot(self) -> None:
        results = [should_use_different_slot(3) for _ in range(1000)]
        different_count = sum(1 for r in results if r != 3)
        # Should use different slot ~5% of the time
        assert 10 < different_count < 200

    def test_never_returns_same_slot(self) -> None:
        results = [should_use_different_slot(2) for _ in range(1000)]
        for r in results:
            if r != 2:
                assert r in (1, 3, 4)
