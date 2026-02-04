"""Shared fixtures for mouse-clock tests."""

import sys
from pathlib import Path

import pytest

# Add src/ to path so core modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def screen_rect():
    """Standard 1920x1080 screen rect (left, top, right, bottom)."""
    return (0, 0, 1920, 1080)


@pytest.fixture
def center_position():
    """Center of a 1920x1080 screen."""
    return (960.0, 540.0)
