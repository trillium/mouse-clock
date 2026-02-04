"""Tests for clock notation conversions."""

import pytest

from core.geometry.clock import (
    number_to_angle,
    letter_to_angle,
    angle_to_letter,
    letter_to_position,
    letter_to_clock_angle,
)


class TestNumberToAngle:
    def test_hour_1(self):
        assert number_to_angle(1) == 30

    def test_hour_3(self):
        assert number_to_angle(3) == 90

    def test_hour_6(self):
        assert number_to_angle(6) == 180

    def test_hour_12(self):
        assert number_to_angle(12) == 0

    def test_hour_9(self):
        assert number_to_angle(9) == 270


class TestLetterToAngle:
    def test_a(self):
        assert letter_to_angle("A") == 30

    def test_c(self):
        assert letter_to_angle("C") == 90

    def test_f(self):
        assert letter_to_angle("F") == 180

    def test_l(self):
        assert letter_to_angle("L") == 0

    def test_case_insensitive(self):
        assert letter_to_angle("a") == letter_to_angle("A")

    def test_all_letters_unique(self):
        angles = [letter_to_angle(chr(ord("A") + i)) for i in range(12)]
        assert len(set(angles)) == 12


class TestAngleToLetter:
    def test_exact_30(self):
        assert angle_to_letter(30) == "A"

    def test_exact_90(self):
        assert angle_to_letter(90) == "C"

    def test_zero_is_L(self):
        assert angle_to_letter(0) == "L"

    def test_350_rounds_to_L(self):
        assert angle_to_letter(350) == "L"

    def test_45_rounds_to_B(self):
        # 45 is between A(30) and B(60), closer to B
        assert angle_to_letter(45) == "B"

    def test_roundtrip_all_letters(self):
        for i in range(12):
            letter = chr(ord("A") + i)
            angle = letter_to_angle(letter)
            assert angle_to_letter(angle) == letter


class TestLetterToPosition:
    def test_a(self):
        assert letter_to_position("A") == 1

    def test_l(self):
        assert letter_to_position("L") == 12

    def test_z(self):
        assert letter_to_position("Z") == 26

    def test_case_insensitive(self):
        assert letter_to_position("a") == letter_to_position("A")


class TestLetterToClockAngle:
    def test_position_1(self):
        assert letter_to_clock_angle(1) == 30

    def test_position_12(self):
        assert letter_to_clock_angle(12) == 0

    def test_position_6(self):
        assert letter_to_clock_angle(6) == 180
