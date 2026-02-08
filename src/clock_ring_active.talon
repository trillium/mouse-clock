tag: user.clock_ring_showing
mode: command
-
widen [{user.number_small}]: user.clock_ring_widen(number_small or 1)
narrow [{user.number_small}]: user.clock_ring_narrow(number_small or 1)
<user.circle_answer>: user.circle_game_answer(circle_answer)

clock off: user.clock_ring_hide()

touch:
    mouse_click(0)
    user.mouse_clock_close()

reverse:
    user.mouse_clock_move_opposite()

# Back command - undo last move, hide ring, reopen clock at previous position
back:
    user.clock_ring_hide()
    user.mouse_clock_go_back()
    user.mouse_clock_activate()
