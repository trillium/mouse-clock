"""Tests for WCAG contrast ratio compliance of info panel colors."""

import pytest

from features.info.contrast import (
    blend_alpha,
    contrast_ratio,
    parse_hex_color,
    relative_luminance,
)
from features.info.data import BG_COLOR, HEADER_COLOR, MUTED_COLOR, TEXT_COLOR


# --- Utility function unit tests ---


class TestParseHexColor:
    def test_black_opaque(self):
        assert parse_hex_color("000000ff") == (0.0, 0.0, 0.0, 1.0)

    def test_white_opaque(self):
        assert parse_hex_color("ffffffff") == (1.0, 1.0, 1.0, 1.0)

    def test_half_alpha(self):
        r, g, b, a = parse_hex_color("ff000080")
        assert r == 1.0
        assert g == 0.0
        assert b == 0.0
        assert abs(a - 128 / 255) < 0.001

    def test_invalid_length_raises(self):
        with pytest.raises(ValueError):
            parse_hex_color("fff")


class TestBlendAlpha:
    def test_opaque_fg_ignores_bg(self):
        result = blend_alpha((1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0))
        assert result == (1.0, 0.0, 0.0)

    def test_transparent_fg_shows_bg(self):
        result = blend_alpha((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 1.0))
        assert result == (0.0, 1.0, 0.0)

    def test_half_alpha_blend(self):
        r, g, b = blend_alpha((1.0, 0.0, 0.0, 0.5), (0.0, 0.0, 1.0, 1.0))
        # fg alpha=0.5, bg alpha=1.0: out_a = 0.5 + 1.0*0.5 = 1.0
        # out_r = (1.0*0.5 + 0.0*1.0*0.5) / 1.0 = 0.5
        assert abs(r - 0.5) < 0.01
        assert abs(b - 0.5) < 0.01


class TestRelativeLuminance:
    def test_black(self):
        assert relative_luminance(0, 0, 0) == 0.0

    def test_white(self):
        assert abs(relative_luminance(1, 1, 1) - 1.0) < 0.001


class TestContrastRatio:
    def test_black_on_white(self):
        ratio = contrast_ratio((0, 0, 0), (1, 1, 1))
        assert abs(ratio - 21.0) < 0.1

    def test_same_color(self):
        ratio = contrast_ratio((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        assert abs(ratio - 1.0) < 0.001

    def test_symmetric(self):
        r1 = contrast_ratio((1, 0, 0), (0, 0, 1))
        r2 = contrast_ratio((0, 0, 1), (1, 0, 0))
        assert abs(r1 - r2) < 0.001


# --- Info panel color compliance tests ---

def _effective_bg(behind_hex: str) -> tuple:
    """Blend BG_COLOR over a behind color to get effective opaque bg."""
    bg_rgba = parse_hex_color(BG_COLOR)
    behind_rgba = parse_hex_color(behind_hex)
    return blend_alpha(bg_rgba, behind_rgba)


def _text_rgb(hex_str: str) -> tuple:
    """Get opaque RGB for a fully-opaque text color."""
    r, g, b, a = parse_hex_color(hex_str)
    return (r, g, b)


class TestHeaderContrast:
    def test_header_contrast_on_black(self):
        bg = _effective_bg("000000ff")
        fg = _text_rgb(HEADER_COLOR)
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 3.0, f"Header on black: {ratio:.2f}:1 (need >=3:1 for large text)"

    def test_header_contrast_on_white_behind(self):
        bg = _effective_bg("ffffffff")
        fg = _text_rgb(HEADER_COLOR)
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 3.0, f"Header on white-behind: {ratio:.2f}:1 (need >=3:1 for large text)"


class TestTextContrast:
    def test_text_contrast_on_black(self):
        bg = _effective_bg("000000ff")
        fg = _text_rgb(TEXT_COLOR)
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 4.5, f"Text on black: {ratio:.2f}:1 (need >=4.5:1)"

    def test_text_contrast_on_white_behind(self):
        bg = _effective_bg("ffffffff")
        fg = _text_rgb(TEXT_COLOR)
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 4.5, f"Text on white-behind: {ratio:.2f}:1 (need >=4.5:1)"


class TestMutedContrast:
    def test_muted_contrast_on_black(self):
        bg = _effective_bg("000000ff")
        fg = _text_rgb(MUTED_COLOR)
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 4.5, f"Muted on black: {ratio:.2f}:1 (need >=4.5:1)"

    def test_muted_contrast_on_white_behind(self):
        bg = _effective_bg("ffffffff")
        fg = _text_rgb(MUTED_COLOR)
        ratio = contrast_ratio(fg, bg)
        assert ratio >= 4.5, f"Muted on white-behind: {ratio:.2f}:1 (need >=4.5:1)"


# Parametrized test covering all text/bg pairs used in the overlay
_ALL_PAIRS = [
    ("HEADER_COLOR", HEADER_COLOR, 18, "000000ff"),
    ("HEADER_COLOR", HEADER_COLOR, 24, "000000ff"),
    ("HEADER_COLOR", HEADER_COLOR, 18, "ffffffff"),
    ("HEADER_COLOR", HEADER_COLOR, 24, "ffffffff"),
    ("TEXT_COLOR", TEXT_COLOR, 16, "000000ff"),
    ("TEXT_COLOR", TEXT_COLOR, 14, "000000ff"),
    ("TEXT_COLOR", TEXT_COLOR, 16, "ffffffff"),
    ("TEXT_COLOR", TEXT_COLOR, 14, "ffffffff"),
    ("MUTED_COLOR", MUTED_COLOR, 14, "000000ff"),
    ("MUTED_COLOR", MUTED_COLOR, 14, "ffffffff"),
]


@pytest.mark.parametrize(
    "name,fg_hex,font_size,behind_hex",
    _ALL_PAIRS,
    ids=[f"{name}-{size}pt-{'black' if bh[0] == '0' else 'white'}" for name, _, size, bh in _ALL_PAIRS],
)
def test_all_section_colors_pass_aa(name, fg_hex, font_size, behind_hex):
    bg = _effective_bg(behind_hex)
    fg = _text_rgb(fg_hex)
    ratio = contrast_ratio(fg, bg)
    threshold = 3.0 if font_size >= 18 else 4.5
    assert ratio >= threshold, (
        f"{name} at {font_size}pt on {'black' if behind_hex[0] == '0' else 'white'}-behind: "
        f"{ratio:.2f}:1 (need >={threshold}:1)"
    )
