tag: user.use_mouse_clock
-
# Clock (circles) — colors only
clock add <user.color>: user.mouse_clock_config_add("circles", "colors", color)
clock remove <user.color>: user.mouse_clock_config_remove("circles", "colors", color)
clock only <user.color>: user.mouse_clock_config_only("circles", "colors", color)
clock reset colors: user.mouse_clock_config_reset("circles", "colors")

# All — applies to all modes
all add <user.color>: user.mouse_clock_config_add_all("colors", color)
all remove <user.color>: user.mouse_clock_config_remove_all("colors", color)
all reset colors: user.mouse_clock_config_reset_all("colors")
