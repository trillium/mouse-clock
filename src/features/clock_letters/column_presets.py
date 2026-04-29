"""
Column layout presets for clock_letters display mode.

Each preset is a function: (n: int) -> List[str]
where n = number of color columns, returns list of column types.
"""

from typing import Callable, Dict, List


def _reference(n: int) -> List[str]:
    """Edge columns = 'letters', middle columns = 'line'."""
    if n <= 2:
        return ["letters"] * n
    return ["letters"] + ["line"] * (n - 2) + ["letters"]


def _full(n: int) -> List[str]:
    """All columns = 'letters' (original clock_letters look)."""
    return ["letters"] * n


PRESETS: Dict[str, Callable[[int], List[str]]] = {
    "reference": _reference,
    "full": _full,
}

PRESET_NAMES: List[str] = list(PRESETS.keys())


def get_preset_column_types(preset_name: str, n: int) -> List[str]:
    """Compute column types from a named preset."""
    fn = PRESETS.get(preset_name)
    if fn is None:
        raise ValueError(f"Unknown column preset: {preset_name!r}. "
                         f"Available: {PRESET_NAMES}")
    return fn(n)
