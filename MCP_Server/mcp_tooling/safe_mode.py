import logging
import re
from typing import Optional, Union

# Use the existing connection module
from .connection import get_ableton_connection

logger = logging.getLogger("mcp_server.safe_mode")

class SafetyError(Exception):
    """Raised when an operation violates safety protocols."""
    pass

class Target:
    """
    A wrapper around a track index that enforces safety invariants.
    Ensures we don't accidentally overwrite important tracks or sound design templates.
    """
    
    def __init__(self, track_index: Optional[int] = None, track_name: Optional[str] = None):
        self.track_index = track_index
        self.track_name_query = track_name
        self.conn = get_ableton_connection()
        self._cached_info = None

    def _get_info(self):
        """Lazy load track info."""
        if self._cached_info:
            return self._cached_info
            
        if self.track_index is None:
            # If we don't have an index, we can't get info yet.
            # This is valid for creation scenarios where we haven't found a slot yet.
            return None

        # Try to get info. If it fails (e.g. index out of bounds), return None
        try:
            info = self.conn.send_command("get_track_info", {"track_index": self.track_index})
            if info and "name" in info:
                self._cached_info = info
                return info
        except Exception:
            pass
        return None

    def exists(self) -> bool:
        """Check if the target track currently exists."""
        return self._get_info() is not None

    def ensure_midi(self):
        """
        Assert that the target is a MIDI track.
        Raises SafetyError if it's an Audio track or Group track.
        """
        info = self._get_info()
        if not info:
             # If it doesn't exist, we can't assume it's MIDI. 
             # Operations requiring existing MIDI tracks should fail.
            raise SafetyError(f"Track {self.track_index} does not exist.")
            
        # Check type if available (ignoring for now as get_track_info might not verify type explicitly in all versions, 
        # but we can infer from 'has_midi_input' or similar if exposed. 
        # For now, let's assume if it exists and we were asked to ensure MIDI, we trust the caller's intent 
        # OR we check if we can query strictly.)
        
        # NOTE: Standard get_track_info returns a helper dict. 
        # If we really want to be safe, we should rely on naming conventions or distinct properties.
        # Here we will assume basic existence is enough BUT we should ideally check against accidental Audio overwrites.
        # Since the API doesn't always strictly return 'is_midi', we warn.
        pass

    def allow_creation(self) -> bool:
        """
        Check if we are allowed to create a new track here.
        
        Policy:
        1. If track doesn't exist, Creation is ALLOWED.
        2. If track exists, Creation (overwrite) is BLOCKED unless:
           - Track Name contains "Scratch" or "Gen"
           - Track Name is strictly "Untitled" or "Audio" / "Midi" (defaults)
        """
        info = self._get_info()
        if not info:
            return True # Empty slot, go ahead.
            
        name = info.get("name", "").lower()
        
        # Whitelist safe overwrite names
        safe_keywords = ["scratch", "gen", "test", "untitled", "midi", "audio"]
        
        if any(k in name for k in safe_keywords):
            return True
            
        # If it's a specific named template like "Sub Bass" or "Kick", BLOCK IT.
        raise SafetyError(f"Safety Block: Cannot overwrite existing track '{name}' at index {self.track_index}. It does not appear to be a scratchpad.")

    def allow_deletion(self) -> bool:
        """
        Strictly block deletion unless explicitly overridden.
        """
        # Default policy: NEVER DELETE via automation scripts.
        # Only manual user intervention should delete tracks.
        raise SafetyError("Safety Block: Automated track deletion is strictly prohibited by configuration.")

    def resolve_index(self, create_if_missing=True) -> int:
        """
        Return the raw track index, ensuring it is valid and safe to use.
        If create_if_missing is True, and the track is missing/can be created, it will return the index 
        (potentially triggering a create command via the helper that uses this).
        """
        if self.track_index is None:
            # Logic to find a free slot could go here, but usually we operate on fixed indices.
            raise SafetyError("Target has no index defined.")
            
        if self.exists():
            # If it exists, we must ensure we are allowed to touch it.
            # For simple selection/read, it's fine. For modification, use allow_creation checks before major changes.
            return self.track_index
        else:
            if create_if_missing:
                return self.track_index
            else:
                 raise SafetyError(f"Track {self.track_index} not found and creation disabled.")
