import logging
from mcp_tooling.generators import generate_chord_progression_advanced
from mcp_tooling.ableton_helpers import ensure_track_exists
from mcp_tooling.connection import get_ableton_connection

# Configure logging
logging.basicConfig(level=logging.INFO)

def run():
    print("Verifying Modal Harmony & Clip Labels...")
    
    # 1. Setup Track
    keys_track = ensure_track_exists(None, prefer="midi")
    conn = get_ableton_connection()
    conn.send_command("set_track_name", {"track_index": keys_track, "name": "Modal Test"})
    
    # 2. Generate Modal Chords (Dorian)
    # This relies on the 'ProgressionGenerator' logic inside generators.py
    # We pass 'generate' as exact progression string to force algo if needed,
    # or just rely on scale='dorian' triggering it.
    
    print("Generating D Dorian...")
    res = generate_chord_progression_advanced(
        track_index=keys_track,
        clip_index=0,
        key="D",
        scale="dorian",
        progression="generate", 
        beats_per_chord=4.0
    )
    print(f"Result: {res}")
    print("Check Live Session: Clip 0 should be named 'D dorian: i - III - ...'")
    
    # 3. Generate Mixolydian (Explicitly different mode)
    print("Generating A Mixolydian...")
    res2 = generate_chord_progression_advanced(
        track_index=keys_track,
        clip_index=1,
        key="A",
        scale="mixolydian",
        progression="generate",
        beats_per_chord=4.0
    )
    print(f"Result: {res2}")
    print("Check Live Session: Clip 1 should be named 'A mixolydian: I - v - ...'")

if __name__ == "__main__":
    run()
