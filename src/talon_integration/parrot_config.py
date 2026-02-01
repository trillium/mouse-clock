"""
Parrot sound configuration for MouseClock.

Manages sound-to-action mappings and configuration.
"""

from ..core.config import get_setting, set_setting

# Default sound configuration
DEFAULT_SOUND_CONFIG = {
    "hiss": {
        "action": "widen",
        "amount": 20,
        "enabled": True,
    },
    "shush": {
        "action": "narrow",
        "amount": 20,
        "enabled": True,
    },
    "pop": {
        "action": "click",
        "enabled": True,
    },
    "cluck": {
        "action": "toggle",
        "enabled": True,
    },
    "tut": {
        "action": "recenter",
        "enabled": True,
    },
}


def get_sound_config() -> dict:
    """Get current sound configuration."""
    return get_setting("parrot_sounds", DEFAULT_SOUND_CONFIG)


def set_sound_config(config: dict):
    """Set sound configuration."""
    set_setting("parrot_sounds", config)


def get_sound_param(sound: str, param: str, default=None):
    """Get a parameter for a specific sound."""
    config = get_sound_config()
    if sound in config:
        return config[sound].get(param, default)
    return default


def set_sound_param(sound: str, param: str, value):
    """Set a parameter for a specific sound."""
    config = get_sound_config()
    if sound not in config:
        config[sound] = {}
    config[sound][param] = value
    set_sound_config(config)


def reset_sound_config():
    """Reset sound configuration to defaults."""
    set_sound_config(DEFAULT_SOUND_CONFIG.copy())


def reload_sound_config():
    """Reload sound configuration."""
    pass  # Currently just a hook for future use
