tag: user.use_centroid_mouse_grid
-
^mouse clock$:
    # user.mouse_clock_select_screen(1)
    user.mouse_clock_close()
    sleep(50ms)
    user.mouse_clock_activate()
key(cmd-ctrl-alt-shift-a):
    user.mouse_clock_close()
    sleep(100ms)
    user.mouse_clock_activate()
    sleep(200ms)
    user.mouse_clock_move("A", "red")
    sleep(100ms)
    user.mouse_clock_move("B", "red")
    sleep(100ms)
    user.mouse_clock_move("C", "red")
    sleep(100ms)
    user.mouse_clock_move("D", "red")
    sleep(100ms)
    user.mouse_clock_move("E", "red")
    sleep(100ms)
    user.mouse_clock_move("F", "red")
    sleep(100ms)
    user.mouse_clock_move("G", "red")
    sleep(100ms)
    user.mouse_clock_move("H", "red")
    sleep(100ms)
    user.mouse_clock_move("I", "red")
    sleep(100ms)
    user.mouse_clock_move("J", "red")
    sleep(100ms)
    user.mouse_clock_move("K", "red")
    sleep(100ms)
    user.mouse_clock_move("L", "red")
    sleep(100ms)
    user.mouse_clock_move("A", "red")
    sleep(100ms)

key(cmd-ctrl-alt-shift-q):
    user.mouse_clock_close()

clock win:
    user.mouse_clock_place_window()
    user.mouse_clock_activate()

# reset <user.letter>+:
#     user.mouse_clock_reset()
#     user.mouse_clock_narrow_list(letter_list)

# clock <user.letter>+:
#     user.mouse_clock_activate()
#     user.mouse_clock_narrow_list(letter_list)

clock screen [<number>]:
    user.mouse_clock_select_screen(number or 1)
    user.mouse_clock_activate()

clock off:
    user.mouse_clock_close()

^<user.letter>+ clock off$:
    # mouse_clock_narrow_list(letter_list)
    # sleep(200ms)
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
