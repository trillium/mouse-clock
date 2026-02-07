tag: user.clock_ring_showing
-
widen [{user.number_small}]: user.clock_ring_widen(number_small or 1)
narrow [{user.number_small}]: user.clock_ring_narrow(number_small or 1)
<user.color> <user.hat_shape>: user.clock_ring_select(color, hat_shape)
<user.color>: user.circle_info_highlight_color(color)
<user.hat_shape>: user.circle_info_highlight_shape(hat_shape)

clock off: user.clock_ring_hide()
