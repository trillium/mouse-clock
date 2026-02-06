_V = "0.0.2"; print(f"[v{_V}] {__name__}")
"""
Talon integration layer for the mouse clock.

Talon loads each .py file individually; no eager imports needed here.
Action registration happens when Talon loads each action module file.
Settings are auto-loaded in core/config.py.
"""
