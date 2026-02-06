_V = "0.0.1"; print(f"[v{_V}] {__name__}")
"""
Sound-to-action mapping registry for parrot sound integration.

Provides configurable bindings between parrot sound labels and
navigation actions with parameters.
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SoundAction:
    """Represents an action bound to a sound."""
    action: Callable
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class SoundActionRegistry:
    """
    Registry for mapping parrot sounds to actions.

    Supports multiple actions per sound (action chains) and
    runtime parameter adjustment.
    """

    def __init__(self):
        self._mappings: Dict[str, List[SoundAction]] = {}

    def register_sound_action(
        self,
        sound_label: str,
        action: Callable,
        params: Dict[str, Any] = None,
        append: bool = False
    ):
        """
        Map a parrot sound to an action with parameters.

        Args:
            sound_label: Sound identifier (e.g., "pop", "hiss")
            action: Callable to invoke when sound detected
            params: Parameters to pass to action
            append: If True, add to existing actions; if False, replace
        """
        sound_action = SoundAction(
            action=action,
            params=params or {}
        )

        if append and sound_label in self._mappings:
            self._mappings[sound_label].append(sound_action)
        else:
            self._mappings[sound_label] = [sound_action]

    def unregister_sound_action(self, sound_label: str, action: Callable = None):
        """
        Remove a sound mapping.

        Args:
            sound_label: Sound identifier
            action: If provided, only remove this specific action;
                   if None, remove all actions for the sound
        """
        if sound_label not in self._mappings:
            return

        if action is None:
            del self._mappings[sound_label]
        else:
            self._mappings[sound_label] = [
                sa for sa in self._mappings[sound_label]
                if sa.action != action
            ]
            if not self._mappings[sound_label]:
                del self._mappings[sound_label]

    def get_action_for_sound(self, sound_label: str) -> Optional[List[SoundAction]]:
        """
        Look up actions for a sound.

        Args:
            sound_label: Sound identifier

        Returns:
            List of SoundAction objects, or None if not mapped
        """
        return self._mappings.get(sound_label)

    def set_sound_param(self, sound_label: str, param_name: str, value: Any):
        """
        Adjust parameters for an existing mapping.

        Updates the parameter for all actions registered to this sound.

        Args:
            sound_label: Sound identifier
            param_name: Parameter name to set
            value: New parameter value
        """
        if sound_label not in self._mappings:
            return

        for sound_action in self._mappings[sound_label]:
            sound_action.params[param_name] = value

    def get_sound_param(
        self,
        sound_label: str,
        param_name: str,
        default: Any = None
    ) -> Any:
        """
        Get a parameter value for a sound mapping.

        Args:
            sound_label: Sound identifier
            param_name: Parameter name
            default: Default value if not found

        Returns:
            Parameter value or default
        """
        if sound_label not in self._mappings:
            return default

        actions = self._mappings[sound_label]
        if actions:
            return actions[0].params.get(param_name, default)
        return default

    def execute_sound(self, sound_label: str) -> bool:
        """
        Execute all actions registered for a sound.

        Args:
            sound_label: Sound identifier

        Returns:
            True if any actions were executed, False otherwise
        """
        actions = self.get_action_for_sound(sound_label)
        if not actions:
            return False

        for sound_action in actions:
            if sound_action.enabled:
                sound_action.action(**sound_action.params)

        return True

    def list_sounds(self) -> List[str]:
        """Get list of all registered sound labels."""
        return list(self._mappings.keys())

    def clear(self):
        """Remove all sound mappings."""
        self._mappings.clear()


# Global registry instance
_global_registry = SoundActionRegistry()


def register_sound_action(
    sound_label: str,
    action: Callable,
    params: Dict[str, Any] = None,
    append: bool = False
):
    """Register action in global registry."""
    _global_registry.register_sound_action(sound_label, action, params, append)


def unregister_sound_action(sound_label: str, action: Callable = None):
    """Unregister action from global registry."""
    _global_registry.unregister_sound_action(sound_label, action)


def get_action_for_sound(sound_label: str) -> Optional[List[SoundAction]]:
    """Get actions from global registry."""
    return _global_registry.get_action_for_sound(sound_label)


def set_sound_param(sound_label: str, param_name: str, value: Any):
    """Set param in global registry."""
    _global_registry.set_sound_param(sound_label, param_name, value)


def execute_sound(sound_label: str) -> bool:
    """Execute sound actions from global registry."""
    return _global_registry.execute_sound(sound_label)


def get_registry() -> SoundActionRegistry:
    """Get the global SoundActionRegistry instance."""
    return _global_registry
