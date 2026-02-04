"""Tests for info panel data integrity."""

import re

from features.info.data import (
    BG_COLOR,
    CLOCK_FACE_LETTERS,
    COLORS,
    HEADER_COLOR,
    LINE_STYLES,
    MUTED_COLOR,
    TEXT_COLOR,
)


class TestClockFaceLetters:
    def test_clock_face_has_12_letters(self):
        assert len(CLOCK_FACE_LETTERS) == 12

    def test_clock_face_letters_a_through_l(self):
        letters = [entry[0] for entry in CLOCK_FACE_LETTERS]
        assert letters == list("abcdefghijkl")

    def test_clock_positions_1_through_12(self):
        positions = [entry[2] for entry in CLOCK_FACE_LETTERS]
        assert positions == [str(i) for i in range(1, 13)]


class TestColors:
    def test_colors_have_valid_hex(self):
        hex_re = re.compile(r"^[0-9a-fA-F]{8}$")
        for name, hex_str in COLORS:
            assert hex_re.match(hex_str), f"Color '{name}' has invalid hex: {hex_str}"


class TestLineStyles:
    def test_line_styles_reference_known_styles(self):
        known_styles = {
            "dash", "dot", "tick",
            "blip", "long", "morse",
            "twin", "chain", "wave",
            "zig", "barb", "rail",
            "cross", "link", "bead",
            "spike", "hash", "saw",
        }
        for style in LINE_STYLES:
            assert style in known_styles, f"Unknown style '{style}'"


class TestStyleConstants:
    def test_color_hex_strings_valid(self):
        hex_re = re.compile(r"^[0-9a-fA-F]{8}$")
        for name, value in [
            ("HEADER_COLOR", HEADER_COLOR),
            ("TEXT_COLOR", TEXT_COLOR),
            ("MUTED_COLOR", MUTED_COLOR),
            ("BG_COLOR", BG_COLOR),
        ]:
            assert hex_re.match(value), f"{name} has invalid hex: {value}"
