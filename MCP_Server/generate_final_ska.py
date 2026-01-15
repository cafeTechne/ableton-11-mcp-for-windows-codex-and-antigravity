import time
import random
import argparse
from mcp_tooling.generators import generate_chord_progression_advanced, generate_bassline_advanced_wrapper
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.melody import generate_melody_from_progression

def generate_final_ska():
    """
    Generate a full Ska Arrangement with Intro, Verse, and Chorus.
    Uses 'walking_mixolydian' bass style (Strict Diatonic) and 'horn_section' melody.
    Supports dynamic Key/Scale via CLI or Random selection.
    """
    parser = argparse.ArgumentParser(description="Generate Ska Song")
    parser.add_argument("--key", type=str, help="Musical Key (e.g. C, F#)")
    parser.add_argument("--scale", type=str, help="Scale/Mode (e.g. minor, dorian)")
    args = parser.parse_args()

    # --- CONFIGURATION ---
    # Randomize Key/Scale if not provided
    ALL_KEYS = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    # Ska works well in minor/dorian/mixolydian. The progressions below are written for Minor/Aeolian (i, iv, bVII).
    # Let's stick to Minor-compatible modes to ensure Roman Numerals resolve correctly.
    COMPATIBLE_MODES = ["aeolian", "minor", "dorian", "harmonic_minor"]
    
    KEY = args.key if args.key else random.choice(ALL_KEYS)
    SCALE = args.scale if args.scale else random.choice(COMPATIBLE_MODES)
    
    # Progression Data
    # IV - bVII - i (Common minor ska movements)
    
    # 1. Intro (4 Bars) - Simple, establishing groove
    # Abm | Abm | Dbmin | Eb7
    INTRO_PROG = ["i", "i", "iv", "V7"] 
    
    # 2. Verse (8 Bars) - The user's provided progression snippet (first half)
    # Fb | Bmaj7 | Dbmin | Eb dim ...
    # Mapping to Roman: VI | III | iv | vdim ...
    # Let's use a consolidated 8-bar block derived from user's input
    VERSE_PROG = [
        "VI", "VI",     # Fb
        "III", "III",   # Bmaj7
        "iv", "iv",     # Dbmin
        "vdim", "vdim"  # Ebdim
    ]
    
    # 3. Chorus (8 Bars) - Higher energy
    # Fbmaj7 | Gb7 | Cb7 | Dbmin7 ...
    CHORUS_PROG = [
        "VImaj7", "VImaj7", # Fbmaj7
        "bVII7", "bVII7",   # Gb7
        "III7", "III7",     # Cb7
        "i", "i"            # Abm (Resolve home)
    ]
    
    print(f"--- Generating Ska Arrangement: {KEY} {SCALE} ---")
    
    conn = get_ableton_connection()
    
    # --- TRACK SETUP ---
    def ensure_track(name):
        ctx = conn.send_command("get_song_context", {"include_clips": False})
        for tr in ctx.get("tracks", []):
             if tr["name"] == name:
                 return tr["index"]
        print(f"Creating track '{name}'...")
        res = conn.send_command("create_midi_track", {"index": -1})
        new_idx = res["index"]
        conn.send_command("set_track_name", {"track_index": new_idx, "name": name})
        return new_idx

    t_keys = ensure_track("Ska Keys")
    t_bass = ensure_track("Ska Bass")
    t_melody = ensure_track("Ska Horns")
    
    print(f"Tracks: Keys={t_keys}, Bass={t_bass}, Horns={t_melody}")
    
    # --- SECTIONS ---
    sections = [
        {"name": "Intro", "prog": INTRO_PROG, "scene_idx": 0},
        {"name": "Verse 1", "prog": VERSE_PROG, "scene_idx": 1},
        {"name": "Chorus 1", "prog": CHORUS_PROG, "scene_idx": 2}
    ]
    
    # --- GENERATION LOOP ---
    # Use time-based seed for variety, but print it for reproducibility
    base_seed = int(time.time())
    print(f"Base Seed: {base_seed}")

    for sec in sections:
        name = sec["name"]
        prog = sec["prog"]
        idx = sec["scene_idx"]
        
        print(f"\nGenerating Section: {name} (Scene {idx+1})")
        
        # 2. Keys (Ska Skank)
        print(f"  > Keys ({len(prog)} chords)")
        generate_chord_progression_advanced(
            track_index=t_keys,
            clip_index=idx,
            key=KEY,
            scale=SCALE,
            rhythm_style="ska_skank",
            progression=prog,
            velocity=90
        )
        
        # 3. Bass (Strict Diatonic Ska)
        print(f"  > Bass (Ska Strict / Diatonic)")
        generate_bassline_advanced_wrapper(
            track_index=t_bass,
            clip_index=idx,
            key=KEY,
            scale=SCALE,
            progression=prog,
            style="ska_strict", # Triggers strict diatonic mode + ska pattern
            velocity=100,
            octave=1,
            seed=base_seed + idx # Deterministic relative to base seed
        )
        
        # 4. Melody (Horn Section - Only for Chorus? or all?)
        # Let's do Verse and Chorus, maybe Intro is sparse.
        if "Intro" not in name:
            print(f"  > Horns (Horn Section Profile)")
            
            notes = generate_melody_from_progression(
                chords=prog,
                key=KEY,
                scale=SCALE,
                beats_per_chord=4.0,
                mood="horn_section",
                seed=base_seed + 100 + idx
            )
            
            # Write to clip
            clip_len = len(prog) * 4.0
            
            # Safe delete
            try:
                conn.send_command("delete_clip", {"track_index": t_melody, "clip_index": idx})
            except: pass
            
            conn.send_command("create_clip", {"track_index": t_melody, "clip_index": idx, "length": clip_len})
            conn.send_command("add_notes_to_clip", {"track_index": t_melody, "clip_index": idx, "notes": notes})
            conn.send_command("set_clip_name", {"track_index": t_melody, "clip_index": idx, "name": f"{name} Horns"})

    print("\n--- Arrangement Generation Complete ---")

if __name__ == "__main__":
    generate_final_ska()
