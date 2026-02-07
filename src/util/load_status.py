"""Diagnostic tool: report load status of all mouse-clock modules.

Call check() from Talon REPL to get a summary of which modules are
loaded and whether they have Talon registrations (Module, Context)
that would break if [ ] unloaded.
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

            has_talon_reg = False
            reg_types = []

            if mod_obj:
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

            results.append((rel, in_sys, reg_types, has_talon_reg))

    # Print summary
    critical = [r for r in results if r[3]]
    utility_loaded = [r for r in results if not r[3] and r[1]]
    utility_missing = [r for r in results if not r[3] and not r[1]]

    print("=== Mouse Clock Module Status ===")
    print()
    print("CRITICAL (have Talon registrations):")
    for rel, loaded, regs, _ in critical:
        flag = "OK" if loaded else "MISSING"
        print(f"  [{flag}] {rel}  ({', '.join(regs)})")

    print()
    print(f"Utility: {len(utility_loaded)} loaded, {len(utility_missing)} not in sys.modules")
    if utility_missing:
        for rel, _, _, _ in utility_missing:
            print(f"  [--] {rel}")
    print()
    print(f"Total: {len(results)} files, {sum(1 for r in results if r[1])} loaded")
