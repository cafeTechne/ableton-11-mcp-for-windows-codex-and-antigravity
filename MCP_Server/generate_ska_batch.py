import random
import time
import subprocess
import sys
from mcp_tooling.generators import generate_chord_progression_advanced, generate_bassline_advanced_wrapper
from mcp_tooling.connection import get_ableton_connection

# Re-using logic from apply_melody_with_motifs (simulated integration)
# Since we are inside the server, we can import the module directly if paths allow, 
# or just shell out to it. Shelling out is cleaner for "using the workflow".
# But for batch efficiency, we'll replicate the core call.

def generate_ska_batch():
    """
    Generate 10 unique Ska Riffs in C Dorian.
    - Track 1: Ska Keys (ska_skank rhythm)
    - Track 2: Ska Bass (ska_strict style - diatonic walking)
    - Track 3: Horns (Generated via apply_melody workflow logic)
    """
    
    KEY = "C"
    SCALE = "dorian" 
    COUNT = 10
    
    # Expanded Progressions (4, 8, 12, 16 bars)
    DORIAN_PROGS = [
        # 4 Bars
        "i IV i IV",
        "IV IV i i",
        "bVII IV i i",  
        "i bIII IV bVII",
        
        # 8 Bars
        "i IV i IV i bVII i i", 
        "i i IV IV bVII bVII i i",
        "i bIII IV bVII i bIII IV bVII", # Repeated walkup
        "i IV i IV bVI bVII i i", # Rockout ending

        # 12 Bars (Bluesy)
        "i i i i IV IV i i v IV i v", # Minor Blues structure
        
        # 16 Bars
        "i IV i IV " * 2 + "bVI bVII i i " * 2
    ]
    
    conn = get_ableton_connection()
    
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

    t_keys = ensure_track(f"Ska Keys ({KEY} {SCALE})")
    t_bass = ensure_track(f"Ska Bass ({KEY} {SCALE})")
    
    print(f"Generating {COUNT} riffs in {KEY} {SCALE}...")
    
    base_seed = int(time.time())
    
    for i in range(COUNT):
        # Pick a progression (randomly)
        prog = random.choice(DORIAN_PROGS)
        print(f"Riff {i+1}: {prog} ({len(prog.split())} bars)")
        
        # 1. Chords
        generate_chord_progression_advanced(
            track_index=t_keys,
            clip_index=i,
            key=KEY,
            scale=SCALE,
            rhythm_style="ska_skank",
            progression=prog,
            velocity=90,
            beats_per_chord=4.0
        )
        conn.send_command("set_clip_name", {"track_index": t_keys, "clip_index": i, "name": prog})
        conn.send_command("set_clip_color", {"track_index": t_keys, "clip_index": i, "color_index": 1 + (i % 69)}) 

        # 2. Bass (Standard Walking - Chromatic allowed)
        # User requested "suped up bassline tool without the strict argument"
        generate_bassline_advanced_wrapper(
            track_index=t_bass,
            clip_index=i,
            key=KEY,
            scale=SCALE,
            progression=prog,
            style="walking", # Standard walking bass (chromaticism allowed)
            velocity=100,
            octave=1,
            seed=base_seed + i
        )
        conn.send_command("set_clip_name", {"track_index": t_bass, "clip_index": i, "name": prog})
        conn.send_command("set_clip_color", {"track_index": t_bass, "clip_index": i, "color_index": 1 + (i % 69)})

        # 3. Melody (Horn Section)
        try:
            from mcp_tooling.melody import generate_melody_from_progression
            
            t_melody = ensure_track(f"Ska Melody ({KEY} {SCALE})")

            notes, length = generate_melody_from_progression(
                chords=prog.split(),
                key=KEY,
                scale=SCALE,
                beats_per_chord=4.0,
                mood="horn_section", 
                seed=base_seed + 100 + i
            )
            
            conn.send_command("create_clip", {"track_index": t_melody, "clip_index": i, "length": len(prog.split()) * 4.0})
            conn.send_command("add_notes_to_clip", {"track_index": t_melody, "clip_index": i, "notes": notes})
            conn.send_command("set_clip_name", {"track_index": t_melody, "clip_index": i, "name": f"Horns {i+1}"})
            conn.send_command("set_clip_color", {"track_index": t_melody, "clip_index": i, "color_index": 1 + (i % 69)})
            
        except Exception as e:
            print(f"Failed to gen melody: {e}")

    print("Batch generation complete.")

if __name__ == "__main__":
    generate_ska_batch()
