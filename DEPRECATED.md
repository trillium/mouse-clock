# Deprecated Code - To Remove When Ready

This file tracks code sections that are disabled or should be removed once the feature is stable.

## adapter.py

### Debug overlay (removed)
```python
# Line ~268 - was:
draw_debug_info(canvas_obj, self.core)
```
- **Status:** Commented out / removed
- **Reason:** Visual debug text at cursor position was getting in the way
- **File:** `src/talon_integration/adapter.py`

### Debug print in draw() (removed)
```python
# Line ~262 - was:
print(f"[DEBUG draw] mode={self._display_mode}, this_lines={len(self._this_lines)}, this_only={self._this_lines_only}")
```
- **Status:** Removed
- **Reason:** Console spam during draw loop
- **File:** `src/talon_integration/adapter.py`

## actions_move.py

### Debug prints in _build_this_lines (to remove)
```python
print(f"[DEBUG _build_this_lines] called with start=({start_x}, {start_y})")
print(f"[DEBUG _build_this_lines] target={main_target}, colors={len(all_colors)}, current={current_color}")
print(f"[DEBUG _build_this_lines] dx={dx}, dy={dy}, length={length}")
print("[DEBUG _build_this_lines] no data, returning")
print("[DEBUG _build_this_lines] length=0, returning")
```
- **Status:** Still in code (for debugging)
- **Reason:** Useful for troubleshooting "this" feature
- **File:** `src/talon_integration/actions_move.py`
- **Action:** Remove when "this" feature is stable

### Debug print in mouse_clock_this_shift
```python
print(f"[this shift] called with: {letters_colors}")
print(f"[this shift] looking for {colors} in {list(color_targets.keys())}")
```
- **Status:** Still in code
- **File:** `src/talon_integration/actions_move.py`
- **Action:** Remove when shift feature is stable

## debug_overlay.py

### Entire file may be removable
- **File:** `src/talon_integration/debug_overlay.py`
- **Status:** Import removed from adapter.py
- **Action:** Consider deleting entire file if no longer used
