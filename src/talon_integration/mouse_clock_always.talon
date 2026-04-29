tag: user.use_mouse_clock
-
^mouse clock$:
    # user.mouse_clock_select_screen(1)
    user.mouse_clock_close()
    sleep(50ms)
    user.mouse_clock_activate()

^mouse dense$:
    user.mouse_clock_close()
    sleep(50ms)
    user.mouse_clock_activate()
    user.mouse_clock_mode_dense_grid()

key(cmd-ctrl-alt-shift-q):
    user.mouse_clock_toggle()

clock win:
    user.mouse_clock_place_window()
    user.mouse_clock_activate()

clock screen [<number>]:
    user.mouse_clock_select_screen(number or 1)
    user.mouse_clock_activate()

clock off:
    user.mouse_clock_close()

^<user.letter>+ clock off$:
    user.mouse_clock_close()

clock debug:
    user.mouse_clock_debug_position()

clock log:
    user.mouse_clock_show_log_location()

clock position:
    user.mouse_clock_log_position()

clock mark <user.text>:
    user.mouse_clock_log_marker(text)

# Activate clock and move in one command (when clock is currently off)
# Note: Excludes "mouse clock" which is handled above
^clock <user.letters_colors>+$:
    user.mouse_clock_move_and_activate(letters_colors)

^<user.letters_colors> <user.letters_colors>+ clock$:
    user.mouse_clock_move_and_activate(letters_colors)

# mouse update screenshot:
#     user.centroid_update_screenshot()
