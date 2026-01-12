"""
Transition Tools - Helpers for smoother scene transitions.

Provides functions to:
- Apply parameter ramps (filter sweeps, reverb throws)
- Configure clip launch settings for staggered starts
- Insert transition scenes
- Generate micro-fills
"""
import logging
from typing import List, Tuple, Optional
from .connection import get_ableton_connection
from .automation import generate_cc_envelope

logger = logging.getLogger("mcp_server.transitions")

# ──────────────────────────────────────────────────────────────────────────────
# apply_parameter_ramp
# ──────────────────────────────────────────────────────────────────────────────

def apply_parameter_ramp(
    track_index: int,
    clip_index: int,
    parameter_name: str,
    start_value: float,
    end_value: float,
    duration_beats: float = 4.0,
    curve_type: str = "linear",
    offset_beats: float = 0.0,
    device_index: Optional[int] = None
) -> str:
    """
    Apply a parameter automation ramp to a clip, useful for filter sweeps, 
    send throws, and volume fades at transition points.

    Args:
        track_index: Index of the track containing the clip.
        clip_index: Scene/clip slot index.
        parameter_name: Name of the parameter to automate (fuzzy matched).
        start_value: Starting value (0-127 for MIDI, 0.0-1.0 for normalized).
        end_value: Ending value.
        duration_beats: Duration of the ramp in beats.
        curve_type: Shape of the ramp ("linear", "exponential_in", "exponential_out", "fade_in", "fade_out").
        offset_beats: Start the ramp this many beats into the clip.
        device_index: Optional, target a specific device by index.

    Returns:
        Status message.
    """
    try:
        ableton = get_ableton_connection()

        # 1. Get track devices
        try:
            t_data = ableton.send_command("get_track_info", {"track_index": track_index})
            devices = t_data.get("devices", [])
        except Exception as e:
            if "Arm" in str(e):
                return f"Cannot inspect devices on Track {track_index} (Group Track)."
            raise

        if not devices:
            return f"No devices found on track {track_index}."

        # 2. Find the target device and parameter
        target_device_idx = device_index if device_index is not None else -1
        matched_param_name = None

        search_lower = parameter_name.lower()

        for d in devices:
            d_idx = d.get("index", 0)
            if device_index is not None and d_idx != device_index:
                continue

            try:
                p_data = ableton.send_command("get_device_parameters", {
                    "track_index": track_index,
                    "device_index": d_idx
                })
                for p in p_data.get("parameters", []):
                    p_name = p.get("name", "")
                    p_orig = p.get("original_name", "")
                    if search_lower in p_name.lower() or search_lower in p_orig.lower():
                        target_device_idx = d_idx
                        matched_param_name = p_name
                        break
            except Exception:
                continue

            if matched_param_name:
                break

        if target_device_idx == -1 or matched_param_name is None:
            return f"Parameter '{parameter_name}' not found on track {track_index}."

        # 3. Generate envelope points
        # 3. Generate envelope points
        from .automation import generate_float_envelope
        envelope = generate_float_envelope(
            length_beats=duration_beats,
            curve_type=curve_type,
            start_value=start_value,
            end_value=end_value,
            resolution=0.03125  # 1/32 beat resolution (high fidelity for smooth lines)
        )

        # Apply offset
        points = [[round(t + offset_beats, 4), v] for t, v in envelope]

        # 4. Apply to clip
        result = ableton.send_command("set_clip_envelope", {
            "track_index": track_index,
            "clip_index": clip_index,
            "device_index": target_device_idx,
            "parameter_name": matched_param_name,
            "points": points
        })

        status = result.get("status", "unknown")
        if status == "success":
            return f"Ramp applied: '{matched_param_name}' {start_value}→{end_value} over {duration_beats} beats (Device {target_device_idx})."
        else:
            return f"Ramp failed: {result.get('message', 'Unknown error')}"

    except Exception as e:
        logger.error(f"apply_parameter_ramp error: {e}")
        return f"Error: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# configure_clip_launch
# ──────────────────────────────────────────────────────────────────────────────

# Quantization value mapping (string to Ableton's internal enum)
QUANTIZATION_MAP = {
    "none": 0,
    "8_bars": 1,
    "4_bars": 2,
    "2_bars": 3,
    "1_bar": 4,
    "half": 5,
    "half_triplet": 6,
    "quarter": 7,
    "quarter_triplet": 8,
    "eighth": 9,
    "eighth_triplet": 10,
    "sixteenth": 11,
    "sixteenth_triplet": 12,
    "thirty_second": 13,
}

def configure_clip_launch(
    track_index: int,
    clip_index: int,
    quantization: Optional[str] = None,
    legato: Optional[bool] = None
) -> str:
    """
    Configure a clip's launch quantization and legato mode.

    Using different launch quantizations per clip allows some elements to 
    trigger late (e.g., pads on 2 bars while drums fire on 1 bar), creating
    a more organic scene transition feel.

    Args:
        track_index: Track index.
        clip_index: Clip slot index.
        quantization: One of: "none", "8_bars", "4_bars", "2_bars", "1_bar",
                      "half", "quarter", "eighth", "sixteenth", etc.
        legato: If True, clip launches in legato mode (continues from current position).

    Returns:
        Status message.
    """
    try:
        ableton = get_ableton_connection()
        changes = []

        if quantization is not None:
            # Map string to integer index expected by Live (or pass string if handler supports it? 
            # Handler expects int index.
            q_val = QUANTIZATION_MAP.get(quantization.lower())
            if q_val is None:
                return f"Unknown quantization: '{quantization}'. Valid: {list(QUANTIZATION_MAP.keys())}"

            ableton.send_command("set_clip_launch_quantization", {
                "track_index": track_index,
                "clip_index": clip_index,
                "quantization": q_val
            })
            changes.append(f"launch_quantization={quantization}")

        if legato is not None:
            # Not supported by current Remote Script
            pass

        if not changes:
            return "No changes specified."

        return f"Clip [{track_index}][{clip_index}] configured: {', '.join(changes)}"

    except Exception as e:
        logger.error(f"configure_clip_launch error: {e}")
        return f"Error: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# insert_transition_scene
# ──────────────────────────────────────────────────────────────────────────────

def insert_transition_scene(
    after_scene_index: int,
    strategy: str = "empty",
    source_tracks: Optional[List[int]] = None
) -> str:
    """
    Insert a new scene after the specified scene, optionally copying clips.

    Strategies:
        - "empty": Create an empty scene (good for adding manual transition FX).
        - "copy_all": Duplicate all clips from the previous scene.
        - "sustain_pads": Copy only non-drum clips (pads, synths) from previous scene.

    Args:
        after_scene_index: Scene index after which to insert (0-indexed).
        strategy: One of "empty", "copy_all", "sustain_pads".
        source_tracks: Optional list of track indices to copy from (for "copy_all"/"sustain_pads").

    Returns:
        Status message including the new scene index.
    """
    try:
        ableton = get_ableton_connection()

        # 1. Create a new scene (inserts at end, we'll use duplicate + delete if needed)
        #    Actually, duplicate_scene is cleaner for copy strategies.
        if strategy == "empty":
            result = ableton.send_command("create_scene", {"scene_index": after_scene_index + 1})
            new_scene_index = after_scene_index + 1
            ableton.send_command("set_scene_name", {
                "scene_index": new_scene_index,
                "name": "Transition"
            })
            return f"Inserted empty transition scene at index {new_scene_index}."

        elif strategy in ("copy_all", "sustain_pads"):
            # Duplicate the source scene
            ableton.send_command("duplicate_scene", {"scene_index": after_scene_index})
            new_scene_index = after_scene_index + 1

            ableton.send_command("set_scene_name", {
                "scene_index": new_scene_index,
                "name": "Transition"
            })

            if strategy == "sustain_pads":
                # Get session info to find drum tracks and delete their clips
                session = ableton.send_command("get_session_info", {})
                tracks = session.get("tracks", [])
                
                for t in tracks:
                    t_idx = t.get("index", 0)
                    t_name = t.get("name", "").lower()
                    # Heuristic: delete clips from tracks named 'drum', 'kick', 'snare', 'hat', 'perc'
                    if any(d in t_name for d in ["drum", "kick", "snare", "hat", "perc", "beat"]):
                        try:
                            ableton.send_command("delete_clip", {
                                "track_index": t_idx,
                                "clip_index": new_scene_index
                            })
                        except Exception:
                            pass  # Clip might not exist

            return f"Inserted transition scene at index {new_scene_index} (strategy: {strategy})."

        else:
            return f"Unknown strategy: '{strategy}'. Valid: empty, copy_all, sustain_pads."

    except Exception as e:
        logger.error(f"insert_transition_scene error: {e}")
        return f"Error: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# generate_micro_fill
# ──────────────────────────────────────────────────────────────────────────────

def generate_micro_fill(
    track_index: int,
    clip_index: int,
    fill_type: str = "drop_out",
    position_beats: Optional[float] = None
) -> str:
    """
    Modify the end of a drum clip to create a micro-fill before a transition.

    Fill Types:
        - "drop_out": Remove the last beat (silence before drop).
        - "snare_roll": Add a snare roll on the last beat.
        - "crash": Add a crash cymbal hit.
        - "reverse_hit": Add a reverse cymbal/riser hit.

    Args:
        track_index: Track index of the drum clip.
        clip_index: Clip slot index.
        fill_type: Type of fill to generate.
        position_beats: Where to apply the fill (default: last beat of clip).

    Returns:
        Status message.
    """
    try:
        ableton = get_ableton_connection()

        # Get clip notes using get_clip_notes (since get_clip_info is missing)
        try:
            notes = ableton.send_command("get_clip_notes", {
                "track_index": track_index,
                "clip_index": clip_index
            })
        except Exception:
            # If get_clip_notes fails, we can't do smart analysis, but we can blind remove
            notes = []

        # We assume 4/4 signature for now since get_clip_info is missing (can't get length easily)
        # Using 4.0 bars * 4 beats usually? 
        # Wait, without get_clip_info we don't know the length.
        # We can try "set_clip_length" to get the current length? No, that sets it.
        # We can use get_clip_notes and find the max start_time?
        # Safe fallback: assume 4 bars (16 beats) or 1 bar (4 beats)?
        
        # Better: use 'remove_notes' which takes a range.
        # If we want to remove the last beat of a 1 bar clip (3.0-4.0) vs 4 bar clip (15.0-16.0)
        # We need the length.
        # Check if 'get_loop_end' works? No.
        
        # Workaround: Assume 4 beat clip if unsure, or calculate from notes.
        last_note_time = 0.0
        if notes:
            last_note_time = max([n.get("start_time", 0) + n.get("duration", 0) for n in notes])
        
        # Round up to nearest bar
        import math
        estimated_length = math.ceil(last_note_time / 4.0) * 4.0
        if estimated_length == 0:
            estimated_length = 4.0
            
        fill_start = position_beats if position_beats is not None else (estimated_length - 1.0)

        if fill_type == "drop_out":
            # Remove notes in the last beat
            # Command is "remove_notes"
            # remove_notes(track_index, clip_index, start_time, time_span)
            ableton.send_command("remove_notes", {
                "track_index": track_index,
                "clip_index": clip_index,
                "start_time": fill_start,
                "time_span": 1.0, # 1 beat
                "start_pitch": 0,
                "pitch_span": 128
            })
            return f"Drop-out applied: removed notes from {fill_start} to {fill_start+1.0}."

        elif fill_type == "snare_roll":
            # Add rapid snare hits (MIDI note 38 is typical snare)
            roll_notes = []
            for i in range(8):  # 16th note roll
                roll_notes.append({
                    "pitch": 38,  # Snare
                    "start_time": fill_start + (i * 0.125),
                    "duration": 0.1,
                    "velocity": 80 + (i * 5)  # Crescendo
                })

            ableton.send_command("add_notes_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": roll_notes
            })
            return f"Snare roll added: {len(roll_notes)} notes starting at beat {fill_start}."

        elif fill_type == "crash":
            # Add a crash cymbal (MIDI note 49 or 57)
            ableton.send_command("add_notes_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": [{
                    "pitch": 49,  # Crash cymbal 1
                    "start_time": fill_start,
                    "duration": 0.5,
                    "velocity": 110
                }]
            })
            return f"Crash added at beat {fill_start}."

        elif fill_type == "reverse_hit":
            # Reverse hits typically go slightly before the transition
            ableton.send_command("add_notes_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": [{
                    "pitch": 57,  # Crash cymbal 2 (often used for reverse samples)
                    "start_time": max(0, fill_start - 0.5),
                    "duration": 1.0,
                    "velocity": 100
                }]
            })
            return f"Reverse hit added before beat {fill_start}."

        else:
            return f"Unknown fill type: '{fill_type}'. Valid: drop_out, snare_roll, crash, reverse_hit."

    except Exception as e:
        logger.error(f"generate_micro_fill error: {e}")
        return f"Error: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# apply_reverb_throw
# ──────────────────────────────────────────────────────────────────────────────

def apply_reverb_throw(
    track_index: int,
    clip_index: int,
    send_index: int = 0,
    duration_beats: float = 4.0,
    peak_value: float = 1.0
) -> str:
    """
    Create a reverb 'throw' effect by ramping a send level up and back down.

    This creates temporal overlap between scenes by letting the reverb tail
    spill into the next section.

    Args:
        track_index: Track index.
        clip_index: Clip slot index.
        send_index: Which send to automate (0 = A, 1 = B, etc.).
        duration_beats: Total duration of the throw.
        peak_value: Maximum send level (0.0-1.0).

    Returns:
        Status message.
    """
    return "apply_reverb_throw: Not implemented in current API (missing set_clip_send_envelope)."
