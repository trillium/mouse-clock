tag: user.use_mouse_clock
and tag: user.mouse_clock_info_mode
-
# Panel navigation
next panel: user.mouse_clock_info_panel_next()
previous panel: user.mouse_clock_info_panel_previous()

# Set edit focus - then use "add/remove <item>" without specifying type
set colors: user.mouse_clock_info_set_focus("colors")
set horizontal: user.mouse_clock_info_set_focus("horizontal")
set vertical: user.mouse_clock_info_set_focus("vertical")

# Contextual add/remove - uses current edit focus
# For colors (when focus is "colors")
add <user.color>: user.mouse_clock_info_add_color(color)
remove <user.color>: user.mouse_clock_info_remove_color(color)

# For styles (when focus is "horizontal" or "vertical")
add <user.line_style>: user.mouse_clock_info_add_item(line_style)
remove <user.line_style>: user.mouse_clock_info_remove_item(line_style)

# Batch add/remove for styles (2+ items)
batch add <user.line_style>+: user.mouse_clock_info_add_items(line_style_list)
batch remove <user.line_style>+: user.mouse_clock_info_remove_items(line_style_list)

# Explicit horizontal/vertical (still works without setting focus)
add <user.line_style> horizontal: user.mouse_clock_info_add_horizontal_style(line_style)
remove <user.line_style> horizontal: user.mouse_clock_info_remove_horizontal_style(line_style)
add <user.line_style> vertical: user.mouse_clock_info_add_vertical_style(line_style)
remove <user.line_style> vertical: user.mouse_clock_info_remove_vertical_style(line_style)
