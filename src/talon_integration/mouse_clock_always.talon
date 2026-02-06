tag: user.use_mouse_clock
-
^mouse clock$:
    # user.mouse_clock_select_screen(1)
    user.mouse_clock_close()
    sleep(50ms)
    user.mouse_clock_activate()

key(cmd-ctrl-alt-shift-q):
    user.mouse_clock_toggle()

key(cmd-ctrl-alt-shift-b:down):
    user.boolean_print("Hiss (keyboard)", "start")
    user.mouse_clock_keyboard_hiss_start()

key(cmd-ctrl-alt-shift-b:up):
    user.boolean_print("Hiss (keyboard)", "stop")
    user.mouse_clock_keyboard_hiss_stop()

key(cmd-ctrl-alt-shift-n:down):
    user.boolean_print("Shush (keyboard)", "start")
    user.mouse_clock_keyboard_shush_start()

key(cmd-ctrl-alt-shift-n:up):
    user.boolean_print("Shush (keyboard)", "stop")
    user.mouse_clock_keyboard_shush_stop()

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

# Activate clock in a specific display mode
show clock circles:
    user.mouse_clock_mode_circles()
    user.mouse_clock_activate()
show clock boxes:
    user.mouse_clock_mode_boxes()
    user.mouse_clock_activate()
show clock grid:
    user.mouse_clock_mode_grid()
    user.mouse_clock_activate()
show clock letters:
    user.mouse_clock_mode_clock_letters()
    user.mouse_clock_activate()
show clock info:
    user.mouse_clock_mode_info()
    user.mouse_clock_activate()

# Activate clock and move in one command (when clock is currently off)
# Note: Excludes "mouse clock" which is handled above
^clock <user.letters_colors>+$:
    user.mouse_clock_move_and_activate(letters_colors)

^<user.letters_colors> <user.letters_colors>+ clock$:
    user.mouse_clock_move_and_activate(letters_colors)

# mouse update screenshot:
#     user.centroid_update_screenshot()
