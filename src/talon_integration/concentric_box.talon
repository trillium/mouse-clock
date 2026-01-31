tag: user.use_mouse_clock
-
# Concentric box overlay commands
boxes: user.box_overlay_show()
boxes hide: user.box_overlay_hide()
boxes center: user.box_overlay_recenter()
box toggle: user.box_overlay_toggle()

# Guided mode with directional rays
boxes guided: user.box_overlay_show_guided()
box guides: user.box_overlay_toggle_guides()

# Targeting: color + direction
box <user.color> <number_small>: user.box_overlay_target(color, number_small)
box <user.color> <user.letter>: user.box_overlay_target_letter(color, letter)
