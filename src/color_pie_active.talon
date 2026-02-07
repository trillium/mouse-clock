tag: user.color_pie_showing
-
widen [{user.number_small}]: user.color_pie_widen(number_small or 1)
narrow [{user.number_small}]: user.color_pie_narrow(number_small or 1)
<user.color> <user.hat_shape>: user.color_pie_select(color, hat_shape)

clock off: user.color_pie_hide()

touch:
    mouse_click(0)
    user.color_pie_hide()

righty:
    mouse_click(1)
    user.color_pie_hide()

mid click:
    mouse_click(2)
    user.color_pie_hide()

<user.modifiers> touch:
    key("{modifiers}:down")
    mouse_click(0)
    key("{modifiers}:up")
    user.color_pie_hide()

<user.modifiers> righty:
    key("{modifiers}:down")
    mouse_click(1)
    key("{modifiers}:up")
    user.color_pie_hide()

(dub click | duke):
    mouse_click()
    mouse_click()
    user.color_pie_hide()

(trip click | trip lick):
    mouse_click()
    mouse_click()
    mouse_click()
    user.color_pie_hide()

left drag | drag | drag start:
    user.mouse_drag(0)
    user.color_pie_hide()

right drag | righty drag:
    user.mouse_drag(1)
    user.color_pie_hide()
