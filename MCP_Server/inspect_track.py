from mcp_tooling.connection import get_ableton_connection

def inspect_notes():
    conn = get_ableton_connection()
    track_name = "2-Square Sweep" # Fuzzy matched in previous step as "Square Sweep"
    track_idx = 1 # From logs
    
    print(f"Inspecting notes for '{track_name}' (Index {track_idx})...")
    
    # Get Clip 0 (Scene 0)
    notes = conn.send_command("get_clip_notes", {"track_index": track_idx, "clip_index": 0})
    if not notes:
        print("Clip 0 is empty.")
    else:
        print(f"Clip 0 has {len(notes)} notes.")
        # Print first bar notes
        bar1 = [n for n in notes if n['start_time'] < 4.0]
        print(f"Bar 1 Notes: {[n['pitch'] for n in bar1]}")
        # Print bar 5 notes (Scene 0 might be long?)
        bar5 = [n for n in notes if 16.0 <= n['start_time'] < 20.0]
        print(f"Bar 5 Notes: {[n['pitch'] for n in bar5]}")

    # Check key/name of track to be sure
    info = conn.send_command("get_track_info", {"track_index": track_idx})
    print(f"Track Name: {info['name']}")

if __name__ == "__main__":
    inspect_notes()
