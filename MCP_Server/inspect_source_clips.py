from mcp_tooling.connection import get_ableton_connection
import sys
import os

sys.path.append(os.getcwd())

def inspect_clips():
    conn = get_ableton_connection()
    
    chord_idx = 2
    bass_indices = [8, 9, 10]
    
    print(f"--- Inspecting Chords (Track {chord_idx}) ---")
    clip_slots = conn.send_command("get_track_info", {"track_index": chord_idx}).get("clip_slots", [])
    
    for i, slot in enumerate(clip_slots):
        if slot.get("has_clip"):
            print(f"  Slot {i}: Found Clip")
            
    print(f"--- Inspecting Bass (Tracks {bass_indices}) ---")
    for b_idx in bass_indices:
        try:
            info = conn.send_command("get_track_info", {"track_index": b_idx})
            clip_slots = info.get("clip_slots", [])
            for i, slot in enumerate(clip_slots):
                if slot.get("has_clip"):
                    print(f"  Track {b_idx} Slot {i}: Found Clip")
        except:
            print(f"  Track {b_idx} not found.")

if __name__ == "__main__":
    inspect_clips()
