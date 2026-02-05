tag: user.use_mouse_clock
-
# Line overlay commands
line <user.letter>: user.line_overlay_move(letter)
line show: user.line_overlay_show_all()
line hide: user.line_overlay_hide()
lines: user.line_overlay_show_all()
lines off: user.line_overlay_clear()
clear lines: user.line_overlay_clear()
grid: user.line_overlay_show_grid()
grid off: user.line_overlay_clear()
grid hide: user.line_overlay_hide()

# Toggle specific line
line <user.letter> off: user.line_overlay_remove_line(letter)
line <user.letter> on: user.line_overlay_add_line(letter)

# Vertical controls
verticals: user.line_overlay_toggle_verticals()
verticals on: user.line_overlay_verticals_on()
verticals off: user.line_overlay_verticals_off()

# Intersection targeting (letter + color)
line <user.letter> <user.color>: user.line_overlay_move_intersection(letter, color)
