tag: user.use_mouse_clock
and tag: user.mouse_clock_this_mode
-
# Step 1/8 toward target (bare "this")
this:
    user.mouse_clock_this_step()

# Repeated "this <target>" - step if same, new line if different
this <user.letters_colors>+:
    user.mouse_clock_this_repeat(letters_colors)

# Step 1/8 away from target
reverse:
    user.mouse_clock_this_reverse()

# Shift ray center to color position(s)
<user.letters_colors>+:
    user.mouse_clock_this_shift(letters_colors)

# Clear the ray and close
clear line:
    user.mouse_clock_clear_this_line()

# Close fully on clock off (not just step back one mode)
clock off:
    user.mouse_clock_close()
