import random
import time
import argparse
import sys
from mcp_tooling.generators import generate_chord_progression_advanced, generate_bassline_advanced_wrapper
from mcp_tooling.connection import get_ableton_connection

# Attempt to import melody generator (handling potential circular/path issues)
try:
    from mcp_tooling.melody import generate_melody_from_progression
except ImportError:
    print("Error: Could not import mcp_tooling.melody")
    sys.exit(1)

def ensure_track(conn, name):
    ctx = conn.send_command("get_song_context", {"include_clips": False})
    for tr in ctx.get("tracks", []):
            if tr["name"] == name:
                return tr["index"]
    print(f"Creating track '{name}'...")
    res = conn.send_command("create_midi_track", {"index": -1})
    new_idx = res["index"]
    conn.send_command("set_track_name", {"track_index": new_idx, "name": name})
    return new_idx

# --- PROGRESSION LIBRARIES ---
# Defines characteristic Ska progressions for different modes
PROGRESSION_MAP = {
    "dorian": [
        "i IV i IV",          # Classic Dorian shift
        "IV IV i i",          # Start on IV
        "bVII IV i i",        # Rock cadence
        "i bIII IV bVII",     # Full walk up
        "i i i i IV IV i i v IV i v", # 12-bar Minor Blues
        "i IV i IV i bVII i i", # 8-bar
    ],
    "minor": [ # Aeolian / Natural Minor
        "i iv v i",
        "i bVI bVII i",    # Iron Maiden / Ska Punk
        "i bVII bVI V",    # Andalusian Cadence (Hit the Road Jack)
        "i iv bVI V",
        "i bIII bVII iv"
    ],
    "mixolydian": [ # Major-ish but with b7
        "I bVII IV I",     # Classic Rock/Ska (Sweet Home Alabama-ish)
        "I I bVII IV",
        "I v IV I",        # v is minor in Mixolydian
        "I bVII v I"
    ],
    "major": [ # Ionian
        "I vi IV V",       # 50s progression (Ska uses this a lot)
        "I IV V IV",       # Wild Thing / Twist and Shout
        "I V vi iii IV I IV V" # Pachelbel-ish / Basket Case
    ]
}

def generate_ska_batch(key, scale, count, strict_bass, base_seed, start_index=0, chiptune=False, chaos=False):
    conn = get_ableton_connection()
    scale_lower = scale.lower()
    
    # Resolve progressions
    if scale_lower in PROGRESSION_MAP:
        progs = PROGRESSION_MAP[scale_lower]
    else:
        print(f"Warning: No specific progressions for '{scale}'. Using 'dorian' defaults.")
        progs = PROGRESSION_MAP["dorian"]

    # Resolve Bass Style
    # User likes "standard walking" (advanced/chromatic) by default now, 
    # but "strict" (diatonic) is an option.
    bass_style = "ska_strict" if strict_bass else "walking"
    bass_label_style = "Strict" if strict_bass else "Walking"
    
    # Resolve Melody Mood
    if chaos:
        melody_mood = "ska_chaos"
        melody_label_style = "CHAOS"
    elif chiptune:
        melody_mood = "horn_section" # Chiptune handled by flag, but base mood still horn
        melody_label_style = "Chiptune"
    else:
        melody_mood = "horn_section"
        melody_label_style = "Horns"

    # Track Names
    t_keys = ensure_track(conn, f"Ska Keys ({key} {scale})")
    t_bass = ensure_track(conn, f"Ska Bass ({key} {scale} - {bass_label_style})")
    t_melody = ensure_track(conn, f"Ska Melody ({key} {scale} - {melody_label_style})")
    
    print(f"Generating {count} riffs in {key} {scale} starting at clip {start_index}...")
    print(f"Bass Style: {bass_style}")
    print(f"Melody Style: {melody_label_style} (Mood: {melody_mood})")

    for i in range(start_index, start_index + count):
        # Pick progression
        prog = random.choice(progs)
        print(f"Riff {i+1}: {prog} ({len(prog.split())} bars)")
        
        # 1. Chords (Keys)
        generate_chord_progression_advanced(
            track_index=t_keys,
            clip_index=i,
            key=key,
            scale=scale,
            rhythm_style="ska_skank",
            progression=prog,
            velocity=90,
            beats_per_chord=4.0
        )
        conn.send_command("set_clip_name", {"track_index": t_keys, "clip_index": i, "name": prog})
        conn.send_command("set_clip_color", {"track_index": t_keys, "clip_index": i, "color_index": 1 + (i % 69)}) 

        # 2. Bass
        generate_bassline_advanced_wrapper(
            track_index=t_bass,
            clip_index=i,
            key=key,
            scale=scale,
            progression=prog,
            style=bass_style,
            velocity=100,
            octave=1,
            seed=base_seed + i
        )
        conn.send_command("set_clip_name", {"track_index": t_bass, "clip_index": i, "name": prog})
        conn.send_command("set_clip_color", {"track_index": t_bass, "clip_index": i, "color_index": 1 + (i % 69)})

        # 3. Melody (Horns)
        try:
            notes, length = generate_melody_from_progression(
                chords=prog.split(),
                key=key,
                scale=scale,
                beats_per_chord=4.0,
                mood=melody_mood, 
                chiptune=chiptune, # Pass chiptune flag
                seed=base_seed + 100 + i
            )
            
            # Clip Length must match progression
            clip_len = len(prog.split()) * 4.0
            
            # Safe delete/create
            try: conn.send_command("delete_clip", {"track_index": t_melody, "clip_index": i})
            except: pass
            
            conn.send_command("create_clip", {"track_index": t_melody, "clip_index": i, "length": clip_len})
            conn.send_command("add_notes_to_clip", {"track_index": t_melody, "clip_index": i, "notes": notes})
            conn.send_command("set_clip_name", {"track_index": t_melody, "clip_index": i, "name": f"{melody_label_style} {i+1}"})
            conn.send_command("set_clip_color", {"track_index": t_melody, "clip_index": i, "color_index": 1 + (i % 69)})
            
        except Exception as e:
            print(f"Failed to gen melody for riff {i+1}: {e}")

    print("Generation Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a batch of Ska Riffs")
    parser.add_argument("--key", default="C", help="Key Root (e.g. C, F#, Bb)")
    parser.add_argument("--scale", default="dorian", help="Scale (major, minor, dorian, mixolydian)")
    parser.add_argument("--count", type=int, default=10, help="Number of riffs to generate")
    parser.add_argument("--strict-bass", action="store_true", help="Force strict diatonic bass (no chromatic lines)")
    parser.add_argument("--seed", type=int, help="Optional Seed")
    parser.add_argument("--start-index", type=int, default=0, help="Starting clip slot index")
    parser.add_argument("--chiptune", action="store_true", help="Enable chiptune constraints for melody")
    parser.add_argument("--chaos", action="store_true", help="Enable CHAOS mood (motifs everywhere)")
    
    args = parser.parse_args()
    
    seed = args.seed if args.seed else int(time.time())
    
    generate_ska_batch(args.key, args.scale, args.count, args.strict_bass, seed, args.start_index, args.chiptune, args.chaos)
