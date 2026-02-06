_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""Diagnostic tool: report load status of all mouse-clock modules.

Call check() from Talon REPL or from another module to get a summary
of which modules are loaded, their versions, and whether they have
Talon registrations (Module, Context) that would break if [ ] unloaded.
"""

import sys
import os


def check():
    """Print load status of all mouse-clock .py files."""
    base = os.path.expanduser("~/.talon/user/trillium/mouse-clock/src")
    results = []

    for root, dirs, files in os.walk(base):
        dirs.sort()
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, os.path.dirname(base))

            # Build module name as Talon uses it
            mod_path = rel.replace("/", ".").replace(".py", "")
            talon_mod = "user.trillium.mouse-clock." + mod_path

            mod_obj = sys.modules.get(talon_mod)
            in_sys = mod_obj is not None

            version = "?"
            has_talon_reg = False
            reg_types = []

            if mod_obj:
                version = getattr(mod_obj, "_V", "?")
                for attr_name in dir(mod_obj):
                    try:
                        obj = getattr(mod_obj, attr_name, None)
                    except Exception:
                        continue
                    t = type(obj).__name__
                    if t == "Module" and attr_name == "mod":
                        reg_types.append("Module")
                        has_talon_reg = True
                    elif t == "Context" and attr_name in ("ctx", "ctx_tags", "parrot_ctx"):
                        reg_types.append("Ctx:" + attr_name)
                        has_talon_reg = True

            results.append((rel, version, in_sys, reg_types, has_talon_reg))

    # Print summary
    critical = [r for r in results if r[4]]
    utility_loaded = [r for r in results if not r[4] and r[2]]
    utility_missing = [r for r in results if not r[4] and not r[2]]

    print("=== Mouse Clock Module Status ===")
    print()
    print("CRITICAL (have Talon registrations):")
    for rel, ver, loaded, regs, _ in critical:
        flag = "OK" if loaded else "MISSING"
        print(f"  [{flag}] v{ver} {rel}  ({', '.join(regs)})")

    print()
    print(f"Utility: {len(utility_loaded)} loaded, {len(utility_missing)} not in sys.modules")
    if utility_missing:
        for rel, ver, _, _, _ in utility_missing:
            print(f"  [--] {rel}")
    print()
    print(f"Total: {len(results)} files, {sum(1 for r in results if r[2])} loaded")


def ver(short_name=""):
    """Check version of a specific module (fuzzy match on filename).

    Usage: ver("parallel")  → shows parallel_lines.py version
           ver()            → shows all versions
    """
    prefix = "user.trillium.mouse-clock."
    matches = []
    for name, mod in sys.modules.items():
        if not name.startswith(prefix):
            continue
        if short_name and short_name not in name:
            continue
        v = getattr(mod, "_V", None)
        if v is not None:
            short = name[len(prefix):]
            matches.append((short, v))

    matches.sort()
    for name, v in matches:
        print(f"  v{v}  {name}")
    if not matches:
        print(f"  No modules matching '{short_name}'")
