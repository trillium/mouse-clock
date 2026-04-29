tag: user.clock_settings_active
-
^clock settings close$: user.clock_settings_hide()
^increase <number_small>$: user.clock_settings_increase(number_small)
^decrease <number_small>$: user.clock_settings_decrease(number_small)
^reset <number_small>$: user.clock_settings_reset(number_small)
^refresh$: user.clock_settings_refresh()
