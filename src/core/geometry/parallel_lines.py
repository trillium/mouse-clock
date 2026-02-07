_V = "0.0.5"; print(f"[v{_V}] {__name__}")
"""Build fan lines for 'this' mode targeting."""

import math
from typing import List, Tuple, Optional

# (start, end, color_name_or_label)
Line = Tuple[Tuple[float, float], Tuple[float, float], str]


def build_parallel_lines(
    start: Tuple[float, float],
    target: Tuple[float, float],
    colors: List[str],
    spacing: float = 15.0,
) -> Optional[List[Line]]:
    """Build fan lines from shared start to spread-out endpoints.

    All lines share the same start point. Endpoints are offset
    perpendicular to the direction, creating a fan shape.

    Colors are in fixed positions centered around gray.

    Returns a list of (start, end, color_name) tuples:
      - lines[0] is always the gray center indicator
      - lines[1:] are the color lines in fixed order

    Returns None if the line has zero length.
    """
    start_x, start_y = start
    target_x, target_y = target

    dx = target_x - start_x
    dy = target_y - start_y
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return None

    # Normalize direction
    dx /= length
    dy /= length

    # Perpendicular vector for offsets (applied only at endpoints)
    perp_x, perp_y = -dy, dx

    n = len(colors)

    lines: List[Line] = []

    # Gray line FIRST (center indicator, drawn underneath)
    lines.append((start, target, "gray"))

    # Color lines: different start points, all converge to same endpoint
    center = (n - 1) / 2.0
    for i, color_name in enumerate(colors):
        slot = i - center
        if n % 2 == 1:
            if slot >= 0:
                slot += 0.5
            else:
                slot -= 0.5
        offset = slot * spacing
        s_x = start_x + perp_x * offset
        s_y = start_y + perp_y * offset
        lines.append(((s_x, s_y), target, color_name))

    return lines
