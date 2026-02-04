"""Tests for position history stack."""

import pytest

from input.history import PositionHistory


class TestPositionHistory:
    def test_push_and_pop(self):
        h = PositionHistory()
        h.push_position((10, 20))
        h.push_position((30, 40))
        assert h.pop_position() == (30, 40)
        assert h.pop_position() == (10, 20)

    def test_pop_empty(self):
        h = PositionHistory()
        assert h.pop_position() is None

    def test_peek(self):
        h = PositionHistory()
        h.push_position((10, 20))
        assert h.peek_position() == (10, 20)
        # Should still be there after peek
        assert h.peek_position() == (10, 20)

    def test_peek_empty(self):
        h = PositionHistory()
        assert h.peek_position() is None

    def test_origin_set_on_first_push(self):
        h = PositionHistory()
        h.push_position((100, 200))
        h.push_position((300, 400))
        assert h.get_origin() == (100, 200)

    def test_explicit_origin(self):
        h = PositionHistory()
        h.set_origin((50, 60))
        assert h.get_origin() == (50, 60)

    def test_clear(self):
        h = PositionHistory()
        h.push_position((1, 2))
        h.push_position((3, 4))
        h.clear_history()
        assert h.is_empty()
        assert h.get_origin() is None

    def test_len(self):
        h = PositionHistory()
        assert len(h) == 0
        h.push_position((1, 2))
        assert len(h) == 1
        h.push_position((3, 4))
        assert len(h) == 2

    def test_is_empty(self):
        h = PositionHistory()
        assert h.is_empty()
        h.push_position((1, 2))
        assert not h.is_empty()

    def test_max_size_trim(self):
        h = PositionHistory(max_size=3)
        for i in range(5):
            h.push_position((i, i))
        assert len(h) == 3
        # Oldest should be dropped
        assert h.pop_position() == (4, 4)
        assert h.pop_position() == (3, 3)
        assert h.pop_position() == (2, 2)

    def test_origin_preserved_after_trim(self):
        h = PositionHistory(max_size=2)
        h.push_position((0, 0))
        h.push_position((1, 1))
        h.push_position((2, 2))
        # Origin is set on first push and not cleared by trim
        assert h.get_origin() == (0, 0)
