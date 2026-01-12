import logging
import math
from typing import List, Dict, Any, Optional, Tuple
from .connection import get_ableton_connection

logger = logging.getLogger("mcp_server.automation")

# CC Constants
CC_MODULATION = 1
CC_EXPRESSION = 11
CC_VOLUME = 7
CC_PAN = 10

def generate_cc_envelope(
    length_beats: float,
    curve_type: str = "swell",
    start_value: int = 0,
    end_value: int = 127,
    resolution: float = 0.25,  # Points per beat
    attack_pct: float = 0.3,
    release_pct: float = 0.2
) -> List[Tuple[float, int]]:
    """
    Generate a list of (time, value) points for a CC envelope.
    
    curve_type:
        - "swell": Start low, peak in middle, fade out.
        - "fade_in": Linear ramp up.
        - "fade_out": Linear ramp down.
        - "constant": Flat value.
        - "linear": Linear ramp from start to end.
        - "exponential_in": Slow start, fast finish.
        - "exponential_out": Fast start, slow finish.
    """
    points = []
    num_points = max(2, int(length_beats / resolution))
    
    for i in range(num_points + 1):
        t = (i / num_points) * length_beats
        pct = i / num_points  # 0.0 to 1.0
        
        if curve_type == "swell":
            # Bell curve: sin(x * pi)
            val = math.sin(pct * math.pi)
        elif curve_type == "fade_in":
            val = pct
        elif curve_type == "fade_out":
            val = 1.0 - pct
        elif curve_type == "constant":
            val = 1.0
        elif curve_type == "linear":
            val = pct
        elif curve_type == "exponential_in":
            val = pct ** 2
        elif curve_type == "exponential_out":
            val = 1.0 - ((1.0 - pct) ** 2)
        elif curve_type == "attack_release":
            # Attack -> Sustain -> Release
            attack_end = attack_pct
            release_start = 1.0 - release_pct
            if pct < attack_end:
                val = pct / attack_end
            elif pct > release_start:
                val = 1.0 - ((pct - release_start) / release_pct)
            else:
                val = 1.0
        else:
            val = pct  # Default to linear
        
        # Map to value range
        mapped_val = int(start_value + (end_value - start_value) * val)
        mapped_val = max(0, min(127, mapped_val))
        points.append((round(t, 4), mapped_val))
    
    return points


def generate_float_envelope(
    length_beats: float,
    curve_type: str = "linear",
    start_value: float = 0.0,
    end_value: float = 1.0,
    resolution: float = 0.125
) -> List[Tuple[float, float]]:
    """
    Generate a list of (time, value) points for a parameter automation envelope (floats).
    Similar to generate_cc_envelope but preserves float precision for normalized params.
    """
    points = []
    num_points = max(2, int(length_beats / resolution))
    
    for i in range(num_points + 1):
        t = (i / num_points) * length_beats
        pct = i / num_points  # 0.0 to 1.0
        
        if curve_type == "swell":
            val = math.sin(pct * math.pi)
        elif curve_type == "fade_in":
            val = pct
        elif curve_type == "fade_out":
            val = 1.0 - pct
        elif curve_type == "constant":
            val = 1.0
        elif curve_type == "linear":
            val = pct
        elif curve_type == "exponential_in":
            val = pct ** 2
        elif curve_type == "exponential_out":
            val = 1.0 - ((1.0 - pct) ** 2)
        elif curve_type == "attack_release":
            # Simple attack/release
            # Assume 30% attack, 20% release
            attack_end = 0.3
            release_start = 0.8
            if pct < attack_end:
                val = pct / attack_end
            elif pct > release_start:
                val = 1.0 - ((pct - release_start) / 0.2)
            else:
                val = 1.0
        else:
            val = pct
        
        # Map to value range (Floats)
        mapped_val = start_value + (end_value - start_value) * val
        points.append((round(t, 4), mapped_val))
    
    return points



def apply_cc_automation(
    track_index: int,
    clip_index: int,
    cc_number: int,
    envelope: List[Tuple[float, int]],
    channel: int = 0,
    device_index: int = None,
    parameter_name: str = None
) -> str:
    """
    Apply CC automation to a clip by writing to a device parameter envelope.
    
    Args:
        track_index: Track index
        clip_index: Clip index
        cc_number: MIDI CC number (used for heuristic parameter matching if parameter_name not given)
        envelope: List of (time, value) tuples
        channel: MIDI channel (unused currently)
        device_index: Optional specific device index to target
        parameter_name: Optional specific parameter name to target
    
    Note: 
        This function maps CC numbers to common parameter names as a heuristic.
        For best results, specify device_index and parameter_name explicitly.
    """
    try:
        ableton = get_ableton_connection()
        
        # CC to parameter name mapping heuristic
        cc_param_map = {
            1: ["Modulation", "Mod Wheel", "CC1", "Macro 1", "Expression"],
            7: ["Volume", "Gain", "Level", "CC7"],
            10: ["Pan", "Panning", "CC10"],
            11: ["Expression", "Dynamics", "CC11", "Macro 2"],
            74: ["Filter Cutoff", "Cutoff", "Filter", "CC74", "Macro 3"],
        }
        
        # Get track info to find devices
        try:
            t_data = ableton.send_command("get_track_info", {"track_index": track_index})
            devices = t_data.get("devices", [])
        except Exception as e:
            if "Arm" in str(e):
                return f"Cannot inspect devices on Track {track_index} (Group Track limitation). Automation requires visible devices."
            raise e
        
        if not devices:
            return f"No devices found on track {track_index}. Add an instrument first."
        
        # Determine target device and parameter
        target_device_idx = device_index if device_index is not None else 0
        target_param_name = parameter_name
        
        if target_param_name is None:
            # Try to find a matching parameter based on CC number
            search_names = cc_param_map.get(cc_number, [f"CC{cc_number}", "Macro 1"])
            
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
                        for search in search_names:
                            if search.lower() in p_name.lower() or search.lower() in p_orig.lower():
                                target_device_idx = d_idx
                                target_param_name = p_name
                                break
                        if target_param_name:
                            break
                except Exception as e:
                    logger.debug(f"Error checking device {d_idx}: {e}")
                    continue
                if target_param_name:
                    break
        
        if target_param_name is None:
            # Fallback: Just use a generic parameter name that might exist
            target_param_name = f"Macro 1"
            logger.warning(f"No matching parameter found for CC{cc_number}. Trying '{target_param_name}'.")
        
        # Convert envelope to list format for JSON
        points = [[float(t), int(v)] for t, v in envelope]
        
        # Call the Remote Script
        result = ableton.send_command("set_clip_envelope", {
            "track_index": track_index,
            "clip_index": clip_index,
            "device_index": target_device_idx,
            "parameter_name": target_param_name,
            "points": points
        })
        
        status = result.get("status", "unknown")
        message = result.get("message", "")
        
        if status == "success":
            return f"CC{cc_number} envelope ({len(points)} pts) applied to '{target_param_name}' on Device {target_device_idx}. {message}"
        else:
            return f"CC{cc_number} automation failed: {message}"
        
    except Exception as e:
        logger.error(f"Error applying CC automation: {e}")
        return f"Error: {e}"


def apply_automation_logic(track_index: int, clip_index: int, parameter_name: str, start_val: float, end_val: float, duration_bars: int = 4, curve: str = "linear") -> str:
    """
    Apply an automation ramp to a clip (for device parameters).
    """
    try:
        ableton = get_ableton_connection()
        beats = float(duration_bars) * 4.0
        
        points = [
            [0.0, float(start_val)],
            [beats, float(end_val)]
        ]
        
        # 1. Inspect Track Devices
        try:
            t_data = ableton.send_command("get_track_info", {"track_index": track_index})
            devices = t_data.get("devices", [])
        except Exception as e:
            if "Arm" in str(e):
                return f"Cannot inspect devices on Track {track_index} (Group Track limitation). Automation requires visible devices."
            raise e
        target_device_idx = -1
        
        # Heuristic: Find first device with parameter 'parameter_name'
        for d in devices:
            d_idx = d["index"]
            p_data = ableton.send_command("get_device_parameters", {"track_index": track_index, "device_index": d_idx})
            for p in p_data.get("parameters", []):
                 if p.get("name") == parameter_name or p.get("original_name") == parameter_name:
                     target_device_idx = d_idx
                     break
            if target_device_idx != -1:
                break
        
        if target_device_idx == -1:
            return f"Parameter '{parameter_name}' not found on any device in track {track_index}."

        ableton.send_command("set_clip_envelope", {
            "track_index": track_index,
            "clip_index": clip_index,
            "device_index": target_device_idx,
            "parameter_name": parameter_name,
            "points": points
        })
        
        return f"Applied automation to '{parameter_name}' on Device {target_device_idx}: {start_val} -> {end_val} over {duration_bars} bars."
    except Exception as e:
        logger.error(f"Error applying automation: {e}")
        return f"Error: {e}"
