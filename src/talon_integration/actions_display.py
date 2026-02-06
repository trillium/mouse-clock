_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Mouse clock display mode actions.
"""

from talon import Module
from .actions_core import set_mouse_clock_tags, ctx_tags
from ..core.config import (
    cycle_info_panel_next,
    cycle_info_panel_previous,
    get_info_panel_mode,
    get_info_edit_focus,
    set_info_edit_focus,
    add_mode_item,
    remove_mode_item,
)

mod = Module()

# Display mode constants (inlined to avoid importing adapter.py at module level)
DISPLAY_MODE_CIRCLES = "circles"
DISPLAY_MODE_BOXES = "boxes"
DISPLAY_MODE_GRID = "grid"
DISPLAY_MODE_INFO = "info"
DISPLAY_MODE_CLOCK_LETTERS = "clock_letters"

# Display modes in rotation order
DISPLAY_MODES = [DISPLAY_MODE_CIRCLES, DISPLAY_MODE_BOXES, DISPLAY_MODE_GRID, DISPLAY_MODE_CLOCK_LETTERS, DISPLAY_MODE_INFO]


def _get_instance():
    from .instance import get_mouse_clock_instance
    return get_mouse_clock_instance()


def _set_mode_and_refresh(mode: str):
    """Set display mode using unified mode system."""
    mouse_clock = _get_instance()

    # Activate clock if not already showing
    if not mouse_clock.active:
        if not mouse_clock.active_canvas:
            mouse_clock.setup()
        mouse_clock.show()

    # Use unified mode setter - handles both display mode and tags
    mouse_clock.set_mode(mode, set_mouse_clock_tags)


@mod.action_class
class DisplayActions:
    def mouse_clock_mode_circles():
        """Switch to circles display mode."""
        _set_mode_and_refresh(DISPLAY_MODE_CIRCLES)

    def mouse_clock_mode_boxes():
        """Switch to boxes display mode."""
        _set_mode_and_refresh(DISPLAY_MODE_BOXES)

    def mouse_clock_mode_grid():
        """Switch to grid display mode (letters + colors)."""
        _set_mode_and_refresh(DISPLAY_MODE_GRID)

    def mouse_clock_mode_info():
        """Switch to info/help display mode."""
        _set_mode_and_refresh(DISPLAY_MODE_INFO)

    def mouse_clock_mode_clock_letters():
        """Switch to clock letters display mode (letters in colors)."""
        _set_mode_and_refresh(DISPLAY_MODE_CLOCK_LETTERS)

    def mouse_clock_get_mode() -> str:
        """Get current display mode."""
        mouse_clock = _get_instance()
        return mouse_clock.get_display_mode()

    def mouse_clock_cycle_mode():
        """Cycle to next display mode."""
        mouse_clock = _get_instance()
        print(f"[DEBUG cycle_mode] active={mouse_clock.active}, canvases={len(mouse_clock.canvases)}")
        current = mouse_clock.get_display_mode()
        try:
            idx = DISPLAY_MODES.index(current)
            next_idx = (idx + 1) % len(DISPLAY_MODES)
        except ValueError:
            next_idx = 0
        next_mode = DISPLAY_MODES[next_idx]
        _set_mode_and_refresh(next_mode)
        print(f"[DEBUG cycle_mode] {current} -> {next_mode}")

    def mouse_clock_cycle_mode_previous():
        """Cycle to previous display mode."""
        mouse_clock = _get_instance()
        current = mouse_clock.get_display_mode()
        try:
            idx = DISPLAY_MODES.index(current)
            prev_idx = (idx - 1) % len(DISPLAY_MODES)
        except ValueError:
            prev_idx = 0
        prev_mode = DISPLAY_MODES[prev_idx]
        _set_mode_and_refresh(prev_mode)
        print(f"Display mode: {prev_mode}")

    def mouse_clock_info_panel_next():
        """Cycle to next info panel (grid -> boxes -> circles)."""
        new_mode = cycle_info_panel_next()
        mouse_clock = _get_instance()
        if mouse_clock.active:
            for canvas_obj in mouse_clock.canvases:
                canvas_obj.freeze()
        print(f"Info panel: {new_mode}")

    def mouse_clock_info_panel_previous():
        """Cycle to previous info panel."""
        new_mode = cycle_info_panel_previous()
        mouse_clock = _get_instance()
        if mouse_clock.active:
            for canvas_obj in mouse_clock.canvases:
                canvas_obj.freeze()
        print(f"Info panel: {new_mode}")

    def mouse_clock_info_add_color(color: str):
        """Add a color to the currently viewed info panel's mode."""
        mode = get_info_panel_mode()
        if add_mode_item(mode, "colors", color):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Added {color} to {mode} colors")

    def mouse_clock_info_remove_color(color: str):
        """Remove a color from the currently viewed info panel's mode."""
        mode = get_info_panel_mode()
        if remove_mode_item(mode, "colors", color):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Removed {color} from {mode} colors")

    def mouse_clock_info_add_horizontal_style(style: str):
        """Add a style to horizontal lines (only works when viewing grid panel)."""
        mode = get_info_panel_mode()
        if mode == "grid" and add_mode_item(mode, "horizontal_styles", style):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Added {style} to horizontal styles")

    def mouse_clock_info_remove_horizontal_style(style: str):
        """Remove a style from horizontal lines (only works when viewing grid panel)."""
        mode = get_info_panel_mode()
        if mode == "grid" and remove_mode_item(mode, "horizontal_styles", style):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Removed {style} from horizontal styles")

    def mouse_clock_info_add_vertical_style(style: str):
        """Add a style to vertical lines (only works when viewing grid panel)."""
        mode = get_info_panel_mode()
        if mode == "grid" and add_mode_item(mode, "vertical_styles", style):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Added {style} to vertical styles")

    def mouse_clock_info_remove_vertical_style(style: str):
        """Remove a style from vertical lines (only works when viewing grid panel)."""
        mode = get_info_panel_mode()
        if mode == "grid" and remove_mode_item(mode, "vertical_styles", style):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Removed {style} from vertical styles")

    def mouse_clock_info_set_focus(focus: str):
        """Set the edit focus (colors, horizontal, or vertical)."""
        set_info_edit_focus(focus)
        mouse_clock = _get_instance()
        if mouse_clock.active:
            for canvas_obj in mouse_clock.canvases:
                canvas_obj.freeze()
        print(f"Edit focus: {focus}")

    def mouse_clock_info_add_item(item: str):
        """Add item based on current edit focus."""
        mode = get_info_panel_mode()
        focus = get_info_edit_focus()

        if focus == "colors":
            dimension = "colors"
        elif focus == "horizontal":
            if mode != "grid":
                print("Horizontal styles only available on grid panel")
                return
            dimension = "horizontal_styles"
        elif focus == "vertical":
            if mode != "grid":
                print("Vertical styles only available on grid panel")
                return
            dimension = "vertical_styles"
        else:
            return

        if add_mode_item(mode, dimension, item):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Added {item} to {mode} {dimension}")

    def mouse_clock_info_remove_item(item: str):
        """Remove item based on current edit focus."""
        mode = get_info_panel_mode()
        focus = get_info_edit_focus()

        if focus == "colors":
            dimension = "colors"
        elif focus == "horizontal":
            if mode != "grid":
                print("Horizontal styles only available on grid panel")
                return
            dimension = "horizontal_styles"
        elif focus == "vertical":
            if mode != "grid":
                print("Vertical styles only available on grid panel")
                return
            dimension = "vertical_styles"
        else:
            return

        if remove_mode_item(mode, dimension, item):
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Removed {item} from {mode} {dimension}")

    def mouse_clock_info_add_items(items: list[str]):
        """Add multiple items based on current edit focus."""
        mode = get_info_panel_mode()
        focus = get_info_edit_focus()

        if focus == "colors":
            dimension = "colors"
        elif focus == "horizontal":
            if mode != "grid":
                print("Horizontal styles only available on grid panel")
                return
            dimension = "horizontal_styles"
        elif focus == "vertical":
            if mode != "grid":
                print("Vertical styles only available on grid panel")
                return
            dimension = "vertical_styles"
        else:
            return

        added = []
        for item in items:
            if add_mode_item(mode, dimension, item):
                added.append(item)

        if added:
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Added {', '.join(added)} to {mode} {dimension}")

    def mouse_clock_info_remove_items(items: list[str]):
        """Remove multiple items based on current edit focus."""
        mode = get_info_panel_mode()
        focus = get_info_edit_focus()

        if focus == "colors":
            dimension = "colors"
        elif focus == "horizontal":
            if mode != "grid":
                print("Horizontal styles only available on grid panel")
                return
            dimension = "horizontal_styles"
        elif focus == "vertical":
            if mode != "grid":
                print("Vertical styles only available on grid panel")
                return
            dimension = "vertical_styles"
        else:
            return

        removed = []
        for item in items:
            if remove_mode_item(mode, dimension, item):
                removed.append(item)

        if removed:
            mouse_clock = _get_instance()
            if mouse_clock.active:
                for canvas_obj in mouse_clock.canvases:
                    canvas_obj.freeze()
            print(f"Removed {', '.join(removed)} from {mode} {dimension}")
