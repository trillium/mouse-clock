"""Tests for configuration and settings management."""

import json
import pytest

from core import config


class TestConstants:
    def test_clock_letters(self):
        assert config.CLOCK_LETTERS == "abcdefghijkl"
        assert len(config.CLOCK_LETTERS) == 12

    def test_default_radius(self):
        assert config.DEFAULT_RADIUS == 300

    def test_min_radius(self):
        assert config.MIN_RADIUS == 20

    def test_color_map_has_all_colors(self):
        expected = {"center", "red", "blue", "green", "yellow", "purple", "pink", "black", "white", "teal"}
        assert set(config.COLOR_MAP.keys()) == expected

    def test_color_pos_ordering(self):
        assert config.COLOR_POS["center"] == 0
        assert config.COLOR_POS["red"] == 1


class TestSettings:
    def setup_method(self):
        """Reset settings before each test."""
        config.reset_all_settings()

    def test_get_default(self):
        assert config.get_setting("default_radius") == 300

    def test_get_missing_returns_none(self):
        assert config.get_setting("nonexistent") is None

    def test_get_missing_with_fallback(self):
        assert config.get_setting("nonexistent", 42) == 42

    def test_set_and_get(self):
        config.set_setting("custom_key", "hello")
        assert config.get_setting("custom_key") == "hello"

    def test_reset_setting(self):
        config.set_setting("default_radius", 999)
        config.reset_setting("default_radius")
        assert config.get_setting("default_radius") == 300

    def test_reset_unknown_setting(self):
        config.set_setting("temp", "val")
        config.reset_setting("temp")
        assert config.get_setting("temp") is None

    def test_reset_all(self):
        config.set_setting("default_radius", 999)
        config.set_setting("extra", "stuff")
        config.reset_all_settings()
        assert config.get_setting("default_radius") == 300
        assert config.get_setting("extra") is None

    def test_get_all_settings(self):
        settings = config.get_all_settings()
        assert isinstance(settings, dict)
        assert "default_radius" in settings

    def test_save_and_load(self, tmp_path):
        settings_file = str(tmp_path / "settings.json")
        config.set_setting("test_val", 123)
        assert config.save_settings(settings_file) is True

        config.reset_all_settings()
        assert config.get_setting("test_val") is None

        assert config.load_settings(settings_file) is True
        assert config.get_setting("test_val") == 123

    def test_load_nonexistent_file(self):
        assert config.load_settings("/nonexistent/path.json") is False
