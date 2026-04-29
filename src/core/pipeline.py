"""
View pipeline — configurable sequence of views for targeting refinement.

Tracks the current stage and advances to the next view after each targeting action.
"""

from .config import get_setting
from .constants import DEFAULT_VIEW_PIPELINE


def get_pipeline():
    """Get the active view pipeline."""
    custom = get_setting("view_pipeline")
    if custom:
        return list(custom)
    return list(DEFAULT_VIEW_PIPELINE)


def get_start_mode():
    """Get the first display mode in the pipeline."""
    pipeline = get_pipeline()
    return pipeline[0] if pipeline else "clock_letters"


def get_next_stage(current_mode: str):
    """Get the next stage after the current mode.

    Returns:
        The next mode string, or "clock_ring" if at end, or None if current mode
        is not in the pipeline (freeform mode switching).
    """
    pipeline = get_pipeline()
    try:
        idx = pipeline.index(current_mode)
        if idx + 1 < len(pipeline):
            return pipeline[idx + 1]
        return None  # Already at the end
    except ValueError:
        return None  # Current mode not in pipeline, no auto-advance
