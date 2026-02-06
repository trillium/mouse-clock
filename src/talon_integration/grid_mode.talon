tag: user.use_mouse_clock
and tag: user.mouse_clock_showing
-
# Grid targeting: color + letter + style
# Example: "red air solid" moves to letter A row, red column
<user.color> <user.letter> <user.line_style>:
    user.grid_move_to(letter, color, line_style)

# Simple targeting without style (defaults to solid)
# Example: "red air" moves to A row, red column
<user.color> <user.letter>:
    print("grid_mode.talon: {letter} {color}")
    user.grid_move_simple(letter, color)
