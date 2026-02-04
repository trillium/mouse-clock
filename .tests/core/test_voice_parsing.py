"""Tests for voice input parsing."""

import pytest

from core.voice_parsing import parse_voice_inputs, flip_letter_to_opposite


class TestParseVoiceInputs:
    def test_single_letter(self):
        result = parse_voice_inputs(["a"])
        assert result["letters"] == ["a"]
        assert result["colors"] == []
        assert result["unknowns"] == []

    def test_single_color(self):
        result = parse_voice_inputs(["red"])
        assert result["letters"] == []
        assert result["colors"] == ["red"]

    def test_letter_and_color(self):
        result = parse_voice_inputs(["c", "red"])
        assert result["letters"] == ["c"]
        assert result["colors"] == ["red"]

    def test_multiple_letters(self):
        result = parse_voice_inputs(["a", "b", "c"])
        assert result["letters"] == ["a", "b", "c"]

    def test_ordinal_multiplier_on_color(self):
        result = parse_voice_inputs(["red", "3"])
        assert result["colors"] == ["red", "red", "red"]

    def test_ordinal_multiplier_on_letter(self):
        result = parse_voice_inputs(["a", "3"])
        assert result["letters"] == ["a", "a", "a"]

    def test_mouse_becomes_center(self):
        result = parse_voice_inputs(["mouse"])
        assert result["colors"] == ["center"]

    def test_half_keyword(self):
        result = parse_voice_inputs(["half"])
        assert result["colors"] == ["half"]

    def test_unknown_words(self):
        result = parse_voice_inputs(["xyzzy"])
        assert result["unknowns"] == ["xyzzy"]

    def test_complex_input(self):
        result = parse_voice_inputs(["red", "3", "a", "pink"])
        assert result["letters"] == ["a"]
        assert result["colors"] == ["red", "red", "red", "pink"]

    def test_empty_input(self):
        result = parse_voice_inputs([])
        assert result["letters"] == []
        assert result["colors"] == []
        assert result["unknowns"] == []

    def test_all_clock_letters(self):
        letters = list("abcdefghijkl")
        result = parse_voice_inputs(letters)
        assert result["letters"] == letters

    def test_ordinal_at_start_no_crash(self):
        """Ordinal with no preceding item should not crash."""
        result = parse_voice_inputs(["3"])
        # No letters or colors to multiply, so ordinal is consumed silently
        assert result["letters"] == []
        assert result["colors"] == []


class TestFlipLetterToOpposite:
    def test_a_to_g(self):
        assert flip_letter_to_opposite("a") == "g"

    def test_g_to_a(self):
        assert flip_letter_to_opposite("g") == "a"

    def test_b_to_h(self):
        assert flip_letter_to_opposite("b") == "h"

    def test_f_to_l(self):
        assert flip_letter_to_opposite("f") == "l"

    def test_l_to_f(self):
        assert flip_letter_to_opposite("l") == "f"

    def test_all_pairs(self):
        pairs = [("a", "g"), ("b", "h"), ("c", "i"), ("d", "j"), ("e", "k"), ("f", "l")]
        for a, b in pairs:
            assert flip_letter_to_opposite(a) == b
            assert flip_letter_to_opposite(b) == a
