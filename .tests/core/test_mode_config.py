"""Tests for per-display-mode configuration API."""

import pytest

from core import config


class TestGetModeConfig:
    def setup_method(self):
        config.reset_all_settings()

    def test_falls_back_to_global_colors(self):
        """When no per-mode key exists, returns global active_colors."""
        result = config.get_mode_config("grid", "colors")
        assert result == config.get_active_colors()

    def test_falls_back_to_global_styles(self):
        result = config.get_mode_config("grid", "styles")
        assert result == config.get_active_styles()

    def test_falls_back_to_global_letters(self):
        result = config.get_mode_config("grid", "letters")
        assert result == config.get_active_letters()

    def test_returns_per_mode_when_set(self):
        config.set_mode_config("grid", "colors", ["red", "blue"])
        assert config.get_mode_config("grid", "colors") == ["red", "blue"]

    def test_per_mode_does_not_affect_other_modes(self):
        config.set_mode_config("grid", "colors", ["red"])
        # circles should still return global
        assert config.get_mode_config("circles", "colors") == config.get_active_colors()

    def test_returns_copy(self):
        """Returned list should be a copy, not a reference."""
        config.set_mode_config("grid", "colors", ["red", "blue"])
        result = config.get_mode_config("grid", "colors")
        result.append("green")
        assert config.get_mode_config("grid", "colors") == ["red", "blue"]


class TestAddModeItem:
    def setup_method(self):
        config.reset_all_settings()

    def test_copies_global_on_first_write(self):
        """First add should copy global list and append."""
        global_colors = config.get_active_colors()
        # Remove an item from global first so we can add it
        config.set_setting("active_colors", ["red", "blue"])
        config.add_mode_item("grid", "colors", "green")
        result = config.get_mode_config("grid", "colors")
        assert "green" in result
        assert "red" in result
        assert "blue" in result

    def test_rejects_invalid_item(self):
        assert config.add_mode_item("grid", "colors", "neon") is False

    def test_rejects_duplicate(self):
        # All colors are active by default, so adding any should fail
        assert config.add_mode_item("grid", "colors", "red") is False

    def test_returns_true_on_success(self):
        config.set_mode_config("grid", "colors", ["red"])
        assert config.add_mode_item("grid", "colors", "blue") is True
        assert config.get_mode_config("grid", "colors") == ["red", "blue"]

    def test_add_style(self):
        config.set_mode_config("grid", "styles", ["dash"])
        assert config.add_mode_item("grid", "styles", "dot") is True
        assert "dot" in config.get_mode_config("grid", "styles")

    def test_add_letter(self):
        config.set_mode_config("grid", "letters", ["a", "b"])
        assert config.add_mode_item("grid", "letters", "c") is True
        assert "c" in config.get_mode_config("grid", "letters")


class TestRemoveModeItem:
    def setup_method(self):
        config.reset_all_settings()

    def test_remove_existing_item(self):
        """Removing from global-fallback should copy-on-write then remove."""
        result = config.remove_mode_item("grid", "colors", "red")
        assert result is True
        assert "red" not in config.get_mode_config("grid", "colors")

    def test_remove_nonexistent_returns_false(self):
        config.set_mode_config("grid", "colors", ["red"])
        assert config.remove_mode_item("grid", "colors", "blue") is False

    def test_remove_does_not_affect_global(self):
        config.remove_mode_item("grid", "colors", "red")
        assert "red" in config.get_active_colors()

    def test_remove_does_not_affect_other_modes(self):
        config.remove_mode_item("grid", "colors", "red")
        assert "red" in config.get_mode_config("circles", "colors")


class TestResetModeConfig:
    def setup_method(self):
        config.reset_all_settings()

    def test_restores_fallback(self):
        config.set_mode_config("grid", "colors", ["red"])
        config.reset_mode_config("grid", "colors")
        # Should fall back to global again
        assert config.get_mode_config("grid", "colors") == config.get_active_colors()

    def test_reset_when_no_override_is_noop(self):
        # Should not raise
        config.reset_mode_config("grid", "colors")
        assert config.get_mode_config("grid", "colors") == config.get_active_colors()


class TestSetModeConfig:
    def setup_method(self):
        config.reset_all_settings()

    def test_set_full_list(self):
        config.set_mode_config("boxes", "colors", ["red", "green"])
        assert config.get_mode_config("boxes", "colors") == ["red", "green"]

    def test_set_empty_list(self):
        config.set_mode_config("circles", "colors", [])
        assert config.get_mode_config("circles", "colors") == []


class TestAllModesOperations:
    def setup_method(self):
        config.reset_all_settings()

    def test_add_to_all_modes(self):
        """Adding to all modes should initialize per-mode overrides for each."""
        # First set each mode to just ["red"]
        for mode in config.CONFIGURABLE_MODES:
            config.set_mode_config(mode, "colors", ["red"])
        # Add blue to all
        for mode in config.CONFIGURABLE_MODES:
            config.add_mode_item(mode, "colors", "blue")
        for mode in config.CONFIGURABLE_MODES:
            colors = config.get_mode_config(mode, "colors")
            assert "blue" in colors

    def test_remove_from_all_modes(self):
        for mode in config.CONFIGURABLE_MODES:
            config.remove_mode_item(mode, "colors", "red")
        for mode in config.CONFIGURABLE_MODES:
            assert "red" not in config.get_mode_config(mode, "colors")

    def test_reset_all_modes(self):
        for mode in config.CONFIGURABLE_MODES:
            config.set_mode_config(mode, "colors", ["red"])
        for mode in config.CONFIGURABLE_MODES:
            config.reset_mode_config(mode, "colors")
        for mode in config.CONFIGURABLE_MODES:
            assert config.get_mode_config(mode, "colors") == config.get_active_colors()
