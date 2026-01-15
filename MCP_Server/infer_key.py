from mcp_tooling.connection import get_ableton_connection
import sys
from collections import Counter

def infer_key():
    conn = get_ableton_connection()
    target_name = "YMCK Square"
    
    # 1. Find Track
    track = None
    ctx = conn.send_command("get_song_context", {"include_clips": False})
    for tr in ctx.get("tracks", []):
        if target_name.lower() in tr["name"].lower():
            track = tr
            break
            
    if not track:
        print(f"Error: Track '{target_name}' not found.")
        return

    print(f"Found Track: {track['name']} (Index {track['index']})")

    # 2. Find a valid clip with notes
    # Get track info to check clip slots
    try:
        info = conn.send_command("get_track_info", {"track_index": track["index"]})
    except Exception as e:
        print(f"Error getting track info: {e}")
        return

    clip_slots = info.get("clip_slots", [])
    valid_scene_idx = -1
    
    for idx, slot in enumerate(clip_slots):
        if slot.get("has_clip"):
            valid_scene_idx = idx
            print(f"Found clip at Scene {idx}")
            break
            
    if valid_scene_idx == -1:
        print("Error: No clips found on track.")
        return

    # 3. Get Notes
    notes = conn.send_command("get_clip_notes", {"track_index": track["index"], "clip_index": valid_scene_idx})
    if not notes:
        print("Error: Clip found but contains no notes.")
        return
        
    print(f"Read {len(notes)} notes from Scene {valid_scene_idx}")

    if not notes:
        print("Error: No MIDI notes found on track.")
        return

    # 3. Analyze
    # Simple heuristic: Bass note (lowest pitch) is often root.
    # Most frequent notes are often tonic/dominant.
    
    pitches = [n['pitch'] for n in notes]
    pcs = [p % 12 for p in pitches]
    
    # Bass analysis (lowest 20% of notes)
    sorted_by_pitch = sorted(pitches)
    bass_notes = sorted_by_pitch[:max(1, int(len(pitches)*0.2))]
    bass_pcs = [p % 12 for p in bass_notes]
    
    bass_counter = Counter(bass_pcs)
    pc_counter = Counter(pcs)
    
    likely_root_pc = bass_counter.most_common(1)[0][0]
    
    # Map PC to Name
    pc_names = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    root_name = pc_names[likely_root_pc]
    
    print(f"\nAnalysis:")
    print(f"Most frequent Bass PC: {likely_root_pc} ({root_name})")
    print(f"Overall Notes Histogram: {dict(pc_counter)}")
    
    # Guess Scale (Major vs Minor3rd)
    # Check for minor 3rd (root + 3) vs major 3rd (root + 4)
    min3 = (likely_root_pc + 3) % 12
    maj3 = (likely_root_pc + 4) % 12
    
    count_min3 = pc_counter.get(min3, 0)
    count_maj3 = pc_counter.get(maj3, 0)
    
    scale_guess = "minor" if count_min3 > count_maj3 else "major"
    
    # Check for Dorian (Minor + Major 6th) vs Aeolian (Minor + Minor 6th)
    if scale_guess == "minor":
        maj6 = (likely_root_pc + 9) % 12
        min6 = (likely_root_pc + 8) % 12
        if pc_counter.get(maj6, 0) > pc_counter.get(min6, 0):
            scale_guess = "dorian"
            
    # Check for Mixolydian (Major + Minor 7th) vs Major (Major + Major 7th)
    if scale_guess == "major":
        min7 = (likely_root_pc + 10) % 12
        maj7 = (likely_root_pc + 11) % 12
        if pc_counter.get(min7, 0) > pc_counter.get(maj7, 0):
             scale_guess = "mixolydian"
    
    print(f"Inferred Key: {root_name}")
    print(f"Inferred Scale: {scale_guess}")
    
    # Return friendly string for next step
    print(f"COMMAND_ARGS: --key {root_name} --scale {scale_guess}")

if __name__ == "__main__":
    infer_key()
