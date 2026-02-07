tag: user.use_mouse_clock
and tag: user.mouse_clock_showing
and not tag: user.mouse_grid_showing
-
key(cmd-ctrl-alt-shift-e):
    print("enter mimice SUPER-e")
    mimic('widen')

[clock] widen [clock]:
    user.mouse_clock_widen()

[clock] narrow [clock]:
    user.mouse_clock_narrow()

reset:
    user.mouse_clock_set_radius(300)

radius <number>:
    user.mouse_clock_set_radius(number)

recenter:
    user.mouse_clock_recenter()

clock it <user.letters_colors>+:
    user.mouse_clock_recenter_and_move(letters_colors)

^<user.letters_colors>+$:
    user.mouse_clock_move_multiple(letters_colors)
    user.mouse_clock_close()
    user.color_pie_show()

^clock <user.letters_colors>+$:
    user.mouse_clock_move_multiple(letters_colors)
    user.mouse_clock_close()
    user.mouse_clock_activate()

^<user.letters_colors>+ clock$:
    user.mouse_clock_move_multiple(letters_colors)
    user.mouse_clock_close()
    user.mouse_clock_activate()

# Reverse command - moves opposite direction of last command
reverse:
    user.mouse_clock_move_opposite()

# Touch commands
^touch <user.letters_colors>+$:
    user.mouse_clock_move_multiple(letters_colors)
    user.mouse_clock_close()
    mouse_click(0)

^<user.letters_colors>+ touch$:
    user.mouse_clock_move_multiple(letters_colors)
    user.mouse_clock_close()
    mouse_click(0)

touch:
    mouse_click(0)
    # Close the mouse clock if active
    user.mouse_clock_close()
    # End dragging if on
    user.mouse_drag_end()

righty:
    mouse_click(1)
    # Close the mouse clock if active
    user.mouse_clock_close()

mid click:
    mouse_click(2)
    # Close the mouse clock if active
    user.mouse_clock_close()

<user.modifiers> touch:
    key("{modifiers}:down")
    mouse_click(0)
    key("{modifiers}:up")
    # Close the mouse clock if active
    user.mouse_clock_close()

<user.modifiers> righty:
    key("{modifiers}:down")
    mouse_click(1)
    key("{modifiers}:up")
    # Close the mouse clock if active
    user.mouse_clock_close()

(dub click | duke):
    mouse_click()
    mouse_click()
    # Close the mouse clock if active
    user.mouse_clock_close()

(trip click | trip lick):
    mouse_click()
    mouse_click()
    mouse_click()
    # Close the mouse clock if active
    user.mouse_clock_close()

left drag | drag | drag start:
    user.mouse_drag(0)
    # Close the mouse clock if active
    user.mouse_clock_close()

right drag | righty drag:
    user.mouse_drag(1)
    # Close the mouse clock if active
    user.mouse_clock_close()

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

# Display mode switching (only when clock is showing)
clock circles: user.mouse_clock_mode_circles()
clock boxes: user.mouse_clock_mode_boxes()
clock grid: user.mouse_clock_mode_grid()
clock letters: user.mouse_clock_mode_clock_letters()
key(cmd-ctrl-alt-shift-e):
    user.mouse_clock_mode_clock_letters()

clock display next: user.mouse_clock_cycle_mode()
clock display (previous | last): user.mouse_clock_cycle_mode_previous()
