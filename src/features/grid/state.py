_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Grid overlay state management.

Tracks column offsets, hiss/shush direction toggles, and session state.
"""

# Grid state - horizontal offset for columns (current and target for animation)
_column_offset_x: float = 0.0
_target_offset_x: float = 0.0

# Grid mode toggle states
_hiss_direction: int = 1      # 1 = right, -1 = left
_shush_mode: int = 1          # 1 = widen, -1 = narrow
_hiss_session_active: bool = False  # Track if we're in a continuous hiss
_shush_session_active: bool = False  # Track if we're in a continuous shush


def get_column_offset() -> float:
    """Get current horizontal offset for columns."""
    return _column_offset_x


def get_target_offset() -> float:
    """Get target horizontal offset for columns."""
    return _target_offset_x


def set_column_offset(offset: float):
    """Set horizontal offset for columns (immediate, no animation)."""
    global _column_offset_x, _target_offset_x
    _column_offset_x = offset
    _target_offset_x = offset


def shift_columns_left(amount: float = 10):
    """Shift columns left by amount pixels (sets target for animation)."""
    global _target_offset_x
    _target_offset_x -= amount


def shift_columns_right(amount: float = 10):
    """Shift columns right by amount pixels (sets target for animation)."""
    global _target_offset_x
    _target_offset_x += amount


def reset_column_offset():
    """Reset column offset to center."""
    global _column_offset_x, _target_offset_x
    _column_offset_x = 0.0
    _target_offset_x = 0.0


def reset_grid_state():
    """Reset all grid state including toggles."""
    global _column_offset_x, _target_offset_x, _hiss_direction, _shush_mode
    global _hiss_session_active, _shush_session_active
    _column_offset_x = 0.0
    _target_offset_x = 0.0
    _hiss_direction = 1
    _shush_mode = 1
    _hiss_session_active = False
    _shush_session_active = False


def end_hiss_session():
    """Call when hiss stops (gap detected) to toggle direction for next session."""
    global _hiss_direction, _hiss_session_active
    if _hiss_session_active:
        old_dir = "right" if _hiss_direction == 1 else "left"
        _hiss_direction *= -1
        new_dir = "right" if _hiss_direction == 1 else "left"
        print(f"🕐 hiss session ended: {old_dir} -> {new_dir}")
        _hiss_session_active = False


def end_shush_session():
    """Call when shush stops (gap detected) to toggle mode for next session."""
    global _shush_mode, _shush_session_active
    if _shush_session_active:
        old_mode = "widen" if _shush_mode == 1 else "narrow"
        _shush_mode *= -1
        new_mode = "widen" if _shush_mode == 1 else "narrow"
        print(f"🕐 shush session ended: {old_mode} -> {new_mode}")
        _shush_session_active = False


def grid_hiss(increment: float):
    """
    Handle hiss in grid mode - shifts columns in current direction.
    Direction toggles only when session ends (gap detected).

    Args:
        increment: Amount to shift (from animator)
    """
    global _hiss_session_active, _target_offset_x

    _hiss_session_active = True
    # Apply shift in current direction
    _target_offset_x += increment * _hiss_direction


def grid_shush(increment: float):
    """
    Handle shush in grid mode - widens or narrows spacing.
    Mode toggles only when session ends (gap detected).

    Args:
        increment: Amount to change (from animator)

    Returns:
        "widen" or "narrow" indicating what action was taken
    """
    global _shush_session_active

    _shush_session_active = True
    # Determine action based on current mode
    if _shush_mode == 1:
        return "widen"
    else:
        return "narrow"


def get_hiss_direction() -> str:
    """Get current hiss direction as string."""
    return "right" if _hiss_direction == 1 else "left"


def get_shush_mode() -> str:
    """Get current shush mode as string."""
    return "widen" if _shush_mode == 1 else "narrow"


def update_offset_animation(lerp_factor: float = 0.2) -> bool:
    """
    Interpolate offset toward target.

    Args:
        lerp_factor: Interpolation factor (0-1)

    Returns:
        True if still animating, False if complete
    """
    global _column_offset_x

    if abs(_column_offset_x - _target_offset_x) < 0.5:
        _column_offset_x = _target_offset_x
        return False

    _column_offset_x += (_target_offset_x - _column_offset_x) * lerp_factor
    return True
