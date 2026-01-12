import logging
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

from .connection import get_ableton_connection
from .util import (
    update_cache_item, update_cache_parameters_by_name, 
    CACHE_FILE, SAMPLE_CACHE_FILE
)
from .ableton_helpers import ensure_device, ensure_track_exists, ensure_clip_slot

logger = logging.getLogger("mcp_server.devices")

def _clean_stem_variants(stem: str) -> List[str]:
    """Generate potential cleaned names for a sample stem."""
    variants = []
    variants.append(stem)
    s = stem
    s = re.sub(r'[_ -]+(\d+bpm|\d+hz|[a-gA-G][#b]?(?:min|maj|m)?)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[_ -]+v\d+$', '', s, flags=re.IGNORECASE) 
    if s != stem: variants.append(s)
    parts = re.split(r'[_ -]+', stem)
    if len(parts) > 1 and len(parts[0]) > 2:
        variants.append(parts[0])
    unique = []
    for v in variants:
         if v not in unique and v: unique.append(v)
    return unique

def _resolve_sample_uri_by_name(name: str, category: str = "sounds", max_items: int = 200) -> Optional[Dict[str, Any]]:
    ableton = get_ableton_connection()
    try:
        result = ableton.send_command("search_loadable_devices", {
            "query": name, "category": category, "max_items": max_items
        })
    except Exception:
        return None
    items = result.get("items", [])
    if not items: return None
    
    def _score(item: Dict[str, Any]) -> int:
        name_lower = str(item.get("name", "")).lower()
        score_val = 0
        if name_lower == name.lower(): score_val -= 2
        if name_lower.startswith(name.lower()): score_val -= 1
        return score_val
    items.sort(key=_score)
    return items[0]

def _resolve_sample_uri(ableton, file_path):
    try:
        stem = Path(file_path).stem.lower()
        # 1. Try path lookup (simplified for now: skip trusted path logic unless strict)
        # 2. Search "Samples"
        res = ableton.send_command("get_browser_items_at_path", {"path": "Samples"}) 
        if res.get("items"):
            for item in res.get("items", []):
                if not item.get("is_loadable", False): continue
                name_lower = str(item.get("name", "")).lower()
                if name_lower == stem or name_lower == f"{stem}.wav" or name_lower == f"{stem}.aif":
                     return item.get("uri")
                     
        # 3. Fallback: name-based search
        variants = _clean_stem_variants(stem)
        for variant in variants:
            try:
                resolved = _resolve_sample_uri_by_name(variant, category="sounds", max_items=400)
                if resolved and resolved.get("uri"):
                    return resolved.get("uri")
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Error resolving sample URI: {e}")
    return None

def load_simpler_with_sample_logic(track_index: int, file_path: str, device_slot: int = -1) -> str:
    try:
        ableton = get_ableton_connection()
        if not file_path: return "file_path is required"

        device_index = ensure_device(ableton, track_index, "Simpler", device_slot)
        if device_index is None:
             load_res = load_device_by_name(track_index, "Simpler", category="instruments")
             if not load_res.get("loaded"): return "Failed to load Simpler"
             device_index = ensure_device(ableton, track_index, "Simpler", device_slot)
        
        if device_index is None:
             try:
                 track_info = ableton.send_command("get_track_info", {"track_index": track_index})
                 devices = track_info.get("devices", [])
                 if not devices: return "No devices found on track"
                 device_index = len(devices) - 1
             except Exception:
                 # If inspection fails (Group Track?), assume device 0 (Instrument)
                 device_index = 0

        sample_uri = _resolve_sample_uri(ableton, file_path)
        if not sample_uri: return f"Could not resolve browser URI for sample: {file_path}"
        
        res = ableton.send_command("hotswap_browser_item", {
            "track_index": track_index, "device_index": device_index, "item_uri": sample_uri
        })
        return f"Loaded sample into Simpler: {res.get('item_name')}"
    except Exception as e:
        return f"Error loading Simpler: {e}"

def load_sampler_with_sample_logic(track_index: int, file_path: str, device_slot: int = -1) -> str:
    try:
        ableton = get_ableton_connection()
        if not file_path: return "file_path is required"

        device_index = ensure_device(ableton, track_index, "Sampler", device_slot)
        if device_index is None:
             load_res = load_device_by_name(track_index, "Sampler", category="instruments")
             if not load_res.get("loaded"): return "Failed to load Sampler"
             device_index = ensure_device(ableton, track_index, "Sampler", device_slot)
        
        if device_index is None:
             try:
                 track_info = ableton.send_command("get_track_info", {"track_index": track_index})
                 devices = track_info.get("devices", [])
                 if not devices: return "No devices found on track"
                 device_index = len(devices) - 1
             except Exception:
                 device_index = 0

        sample_uri = _resolve_sample_uri(ableton, file_path)
        if not sample_uri: return f"Could not resolve browser URI for sample: {file_path}"
        
        res = ableton.send_command("hotswap_browser_item", {
            "track_index": track_index, "device_index": device_index, "item_uri": sample_uri
        })
        return f"Loaded sample into Sampler: {res.get('item_name')}"
    except Exception as e:
        return f"Error loading Sampler: {e}"

def load_sample_by_name_logic(sample_name: str, track_index: Optional[int] = None, clip_index: int = 0, category: str = "sounds", fire: bool = False) -> str:
    try:
        ableton = get_ableton_connection()
        target_track = ensure_track_exists(track_index, prefer="audio")
        ensure_clip_slot(target_track, clip_index)
        
        resolved = _resolve_sample_uri_by_name(sample_name, category=category)
        if not resolved or not resolved.get("uri"):
            return f"No sample found matching '{sample_name}'"

        load_resp = ableton.send_command("load_browser_item", {
            "track_index": target_track, "item_uri": resolved.get("uri"), "clip_index": clip_index
        })
        
        if load_resp.get("loaded") and fire:
             ableton.send_command("fire_clip", {"track_index": target_track, "clip_index": clip_index})
             return f"Loaded and fired '{load_resp.get('item_name')}'"
        return f"Loaded '{load_resp.get('item_name')}'"
    except Exception as e:
        return f"Error: {e}"

def load_drum_kit_logic(track_index: int, rack_uri: str, kit_path: str) -> str:
    try:
        ableton = get_ableton_connection()
        ableton.send_command("load_browser_item", {"track_index": track_index, "item_uri": rack_uri})
        
        kit_result = ableton.send_command("get_browser_items_at_path", {"path": kit_path})
        kit_items = kit_result.get("items", [])
        loadable = [i for i in kit_items if i.get("is_loadable")]
        if not loadable: return f"No loadable kits at {kit_path}"
        
        kit_uri = loadable[0].get("uri")
        ableton.send_command("load_browser_item", {"track_index": track_index, "item_uri": kit_uri})
        return f"Loaded kit '{loadable[0].get('name')}'"
    except Exception as e:
        return f"Error: {e}"

def load_device_logic(track_index: int, device_uri: str, device_slot: int = -1) -> str:
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("load_device", {
            "track_index": track_index, "device_uri": device_uri, "device_slot": device_slot
        })
        if result.get("loaded", False):
            # Cache update logic
            parameter_meta = result.get("parameters")
            device_name = result.get("item_name", device_uri)
            try:
                # Fetch fresh parameters
                device_index = max(result.get("device_count", 1) - 1, 0)
                meta_resp = ableton.send_command("get_device_parameters", {
                    "track_index": track_index, "device_index": device_index
                })
                device_name = meta_resp.get("device_name", device_name)
                parameter_meta = meta_resp.get("parameters", parameter_meta)
            except Exception: pass
            
            update_cache_item(name=result.get("item_name", device_uri), uri=device_uri, parameters=parameter_meta)
            if device_name and parameter_meta:
                update_cache_parameters_by_name(device_name, parameter_meta)
            return f"Loaded device '{result.get('item_name')}'"
        return f"Failed to load device (uri: {device_uri})"
    except Exception as e:
        return f"Error: {e}"

def load_clip_by_name_logic(clip_name: str, track_index: Optional[int] = None, clip_index: int = 0, category: str = "all", fire: bool = False) -> str:
    try:
        ableton = get_ableton_connection()
        target_track = ensure_track_exists(track_index, prefer="audio") 
        ensure_clip_slot(target_track, clip_index)
        
        resolved = _resolve_sample_uri_by_name(clip_name, category=category)
        if not resolved or not resolved.get("uri"):
            return f"No clip found matching '{clip_name}'"

        load_resp = ableton.send_command("load_browser_item", {
            "track_index": target_track, "item_uri": resolved.get("uri"), "clip_index": clip_index
        })
        
        if load_resp.get("loaded") and fire:
             ableton.send_command("fire_clip", {"track_index": target_track, "clip_index": clip_index})
             return f"Loaded and fired '{load_resp.get('item_name')}'"
        return f"Loaded '{load_resp.get('item_name')}'"
    except Exception as e:
        return f"Error: {e}"

def plan_load_device_logic(query: str) -> str:
    """Offline planning tool to check what URI a query resolves to."""
    result = {"query": query, "found": False, "resolved_device_uri": None, "resolved_sample_uri": None, "error": None}
    
    # 1. Check Device
    try:
        # Deprecated: resolve_uri_by_name removed - URIs are unreliable
        dev_uri = None
        if dev_uri:
            result["found"] = True
            result["resolved_device_uri"] = dev_uri
            return json.dumps(result, indent=2)
    except Exception as e:
        result["error"] = f"Device lookup error: {str(e)}"

    # 2. Check Sample (Names) - Offline check via Cache File
    try:
        if SAMPLE_CACHE_FILE.exists():
            s_cache = json.loads(SAMPLE_CACHE_FILE.read_text())
            items = s_cache.get("items", [])
            matches = [i for i in items if query.lower() in i.get("name", "").lower()]
            if matches:
                 result["found"] = True
                 result["resolved_sample_uri"] = matches[0].get("uri")
                 return json.dumps(result, indent=2)
    except Exception: pass

    return json.dumps(result, indent=2)

def search_and_load_device(track_index: int, query: str, category: str = "all") -> str:
    """
    Search for a device by name and load it onto a track.
    
    This is a convenience wrapper that combines browser search + device load.
    Commonly used in user scripts to load effects and instruments.
    
    Args:
        track_index: Target track
        query: Device name to search for (e.g., "EQ Eight", "Compressor", "Grand Piano")
        category: Browser category ("audio_effects", "instruments", "midi_effects", "all")
    
    Returns:
        Status message
    """
    try:
        ableton = get_ableton_connection()
        
        # Search for the device
        # Use live browser search instead of URI resolution
        result = ableton.send_command("search_and_load_device", {
            "track_index": track_index,
            "query": query,
            "category": category
        })
        
        if result.get("loaded"):
            return f"Loaded: {result.get('item_name', query)}"
        else:
            return f"Failed to load: {query}"
            
    except Exception as e:
        return f"Error: {e}"
