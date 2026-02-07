"""
Event capture utility for debugging mouse clock.

Usage:
    # In Talon REPL or voice command:
    actions.user.mouse_clock_start_event_capture()

    # ... do stuff with mouse clock ...

    actions.user.mouse_clock_stop_event_capture()

    # Check /tmp/mouse_clock_events.log
"""

from talon import Module, events, cron
from pathlib import Path

mod = Module()

# State
_reader = None
_log_file = None
_cron_job = None
_event_count = 0

# Filter for mouse clock related events
FILTERS = [
    "mouse_clock",
    "clock_letters",
    "display_mode",
    "canvas",
]

def _matches_filter(event) -> bool:
    """Check if event is related to mouse clock."""
    text = f"{event.topic} {event.desc} {event.attrs}"
    return any(f in text.lower() for f in FILTERS)


def _poll_events():
    """Poll for new events and write matching ones to log."""
    global _reader, _log_file, _event_count
    if not _reader or not _log_file:
        return

    for event in _reader:
        # Write all events or just filtered ones
        if _matches_filter(event):
            line = f"[{event.ts:.3f}] {event.topic:12} | {event.desc[:60]:60} | {event.attrs}\n"
            _log_file.write(line)
            _log_file.flush()
            _event_count += 1


@mod.action_class
class EventCaptureActions:
    def mouse_clock_start_event_capture(path: str = "/tmp/mouse_clock_events.log"):
        """Start capturing mouse clock related events to a file."""
        global _reader, _log_file, _cron_job, _event_count

        if _log_file:
            print("[event_capture] Already capturing, stop first")
            return

        _reader = events.reader()
        _log_file = open(path, "w")
        _event_count = 0

        # Write header
        _log_file.write("# Mouse Clock Event Capture\n")
        _log_file.write(f"# Filters: {FILTERS}\n")
        _log_file.write("#" + "=" * 100 + "\n\n")
        _log_file.flush()

        # Poll every 50ms
        _cron_job = cron.interval("50ms", _poll_events)
        print(f"[event_capture] Started capturing to {path}")

    def mouse_clock_stop_event_capture():
        """Stop capturing events and close the log file."""
        global _reader, _log_file, _cron_job, _event_count

        if _cron_job:
            cron.cancel(_cron_job)
            _cron_job = None

        if _log_file:
            _log_file.write(f"\n# Captured {_event_count} events\n")
            _log_file.close()
            _log_file = None
            print(f"[event_capture] Stopped. Captured {_event_count} events.")

        _reader = None

    def mouse_clock_event_capture_status():
        """Check if event capture is running."""
        if _log_file:
            print(f"[event_capture] Running. {_event_count} events captured so far.")
        else:
            print("[event_capture] Not running.")
