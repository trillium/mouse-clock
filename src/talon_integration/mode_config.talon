tag: user.use_mouse_clock
-
# Clock (circles) — colors only
clock add <user.color>: user.mouse_clock_config_add("circles", "colors", color)
clock remove <user.color>: user.mouse_clock_config_remove("circles", "colors", color)
clock only <user.color>: user.mouse_clock_config_only("circles", "colors", color)
clock reset colors: user.mouse_clock_config_reset("circles", "colors")

# Squares (boxes) — colors only
squares add <user.color>: user.mouse_clock_config_add("boxes", "colors", color)
squares remove <user.color>: user.mouse_clock_config_remove("boxes", "colors", color)
squares only <user.color>: user.mouse_clock_config_only("boxes", "colors", color)
squares reset colors: user.mouse_clock_config_reset("boxes", "colors")

# Grid — colors, horizontal/vertical styles, letters
grid add <user.color>: user.mouse_clock_config_add("grid", "colors", color)
grid remove <user.color>: user.mouse_clock_config_remove("grid", "colors", color)
grid only <user.color>: user.mouse_clock_config_only("grid", "colors", color)
grid add <user.line_style> horizontal: user.mouse_clock_config_add("grid", "horizontal_styles", line_style)
grid remove <user.line_style> horizontal: user.mouse_clock_config_remove("grid", "horizontal_styles", line_style)
grid add <user.line_style> vertical: user.mouse_clock_config_add("grid", "vertical_styles", line_style)
grid remove <user.line_style> vertical: user.mouse_clock_config_remove("grid", "vertical_styles", line_style)
grid add <user.clock_face>: user.mouse_clock_config_add("grid", "letters", clock_face)
grid remove <user.clock_face>: user.mouse_clock_config_remove("grid", "letters", clock_face)
grid reset colors: user.mouse_clock_config_reset("grid", "colors")
grid reset horizontal styles: user.mouse_clock_config_reset("grid", "horizontal_styles")
grid reset vertical styles: user.mouse_clock_config_reset("grid", "vertical_styles")
grid reset letters: user.mouse_clock_config_reset("grid", "letters")

# All — applies to all modes
all add <user.color>: user.mouse_clock_config_add_all("colors", color)
all remove <user.color>: user.mouse_clock_config_remove_all("colors", color)
all reset colors: user.mouse_clock_config_reset_all("colors")
