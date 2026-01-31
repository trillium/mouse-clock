tag: user.use_mouse_clock
-
# Line overlay commands
line <user.letter>: user.line_overlay_move(letter)
line show: user.line_overlay_show_all()
line hide: user.line_overlay_hide()
lines: user.line_overlay_show_all()
grid: user.line_overlay_show_grid()
verticals: user.line_overlay_toggle_verticals()

# Intersection targeting (letter + color)
line <user.letter> <user.color>: user.line_overlay_move_intersection(letter, color)
