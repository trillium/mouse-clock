"""Configure Talon mocks for rendering tests.

Rendering modules use deep relative imports (e.g., `from ...core import config`)
that only work in Talon's package loader. To test without Talon, we:
1. Mock the talon.* modules
2. Set up src/ as a namespace package so relative imports resolve
"""

import sys
import types
from pathlib import Path

# Paths
_tests_dir = Path(__file__).parent.parent
_src_dir = _tests_dir.parent / "src"

# Ensure .tests/ on path for mocks
if str(_tests_dir) not in sys.path:
    sys.path.insert(0, str(_tests_dir))

from mocks.canvas import MockPaint, MockStyle, MockRect


def _install_talon_mocks():
    """Install mock talon modules so rendering code can import."""
    if "talon" in sys.modules:
        return

    talon_mod = types.ModuleType("talon")
    talon_ui = types.ModuleType("talon.ui")
    talon_ui.screens = lambda: []
    talon_mod.ui = talon_ui

    talon_skia = types.ModuleType("talon.skia")
    talon_skia.Paint = MockPaint
    talon_skia.Rect = MockRect

    talon_types = types.ModuleType("talon.types")
    talon_types_point = types.ModuleType("talon.types.point")

    class Point2d:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    talon_types_point.Point2d = Point2d

    talon_canvas = types.ModuleType("talon.canvas")
    talon_mod.cron = types.ModuleType("talon.cron")
    talon_mod.cron.interval = lambda *a, **kw: None
    talon_mod.cron.cancel = lambda *a, **kw: None
    talon_mod.cron.after = lambda *a, **kw: None

    sys.modules["talon"] = talon_mod
    sys.modules["talon.ui"] = talon_ui
    sys.modules["talon.skia"] = talon_skia
    sys.modules["talon.types"] = talon_types
    sys.modules["talon.types.point"] = talon_types_point
    sys.modules["talon.canvas"] = talon_canvas


def _setup_src_as_package():
    """Make src/ work as an implicit namespace so relative imports resolve.

    The trick: add the PARENT of src/ to sys.path and make src a package.
    Then rendering.canvas.utils can do `from ...core import config` because
    the chain is src.rendering.canvas.utils → src.rendering.canvas → src.rendering → src → core.
    """
    src_parent = str(_src_dir.parent)
    if src_parent not in sys.path:
        sys.path.insert(0, src_parent)

    # Create src as a proper package in sys.modules
    if "src" not in sys.modules:
        import importlib
        # Create __init__ for src
        init_path = _src_dir / "__init__.py"
        needs_cleanup = not init_path.exists()
        if needs_cleanup:
            init_path.write_text("")
        try:
            # Import src as a package
            spec = importlib.util.spec_from_file_location(
                "src", str(init_path),
                submodule_search_locations=[str(_src_dir)]
            )
            src_mod = importlib.util.module_from_spec(spec)
            sys.modules["src"] = src_mod
            spec.loader.exec_module(src_mod)
        finally:
            if needs_cleanup:
                init_path.unlink(missing_ok=True)


_install_talon_mocks()
_setup_src_as_package()
