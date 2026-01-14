import time
from mcp_tooling.generators import generate_chord_progression_advanced, generate_bassline_advanced_wrapper, key_to_midi
from mcp_tooling.connection import get_ableton_connection

def generate_final_ska():
    # User Input:
    # Fb | Fb | Bmaj7 | Bmaj7 | Dbmin | Dbmin | Eb dim | Eb dim | Bmaj 7 | Bmaj 7 | Fbmaj7 | Fbmaj7| Gb7 |Gb7 | Cb7| Cb7| Dbmin7 | Gb | Dbmin7 | Gb | Cb7| C dim| Dbmin7 | Gb7 | Dbmin7 | Gb7 | Cb7| Eb dim| 
    
    # Mapping to Ab Aeolian (Ab Minor)
    # Fb -> VI
    # Bmaj7 -> III
    # Dbmin -> iv
    # Eb dim -> vdim
    # Gb -> bVII (Major Triad)
    # C dim -> #IIIdim
    
    progress_bars = [
        "VI", "VI", # Fb | Fb
        "III", "III", # Bmaj7 | Bmaj7
        "iv", "iv", # Dbmin | Dbmin
        "vdim", "vdim", # Eb dim | Eb dim
        "III", "III", # Bmaj 7 | Bmaj 7
        "VImaj7", "VImaj7", # Fbmaj7 | Fbmaj7
        "bVII7", "bVII7", # Gb7 | Gb7
        "III7", "III7", # Cb7 | Cb7
        "iv7", # Dbmin7
        "bVII", # Gb (Major Triad)
        "iv7", # Dbmin7
        "bVII", # Gb (Major Triad)
        "III7", # Cb7
        "#IIIdim", # C dim
        "iv7", # Dbmin7
        "bVII7", # Gb7
        "iv7", # Dbmin7
        "bVII7", # Gb7
        "III7", # Cb7
        "vdim" # Eb dim
    ]
    
    prog_str = "| " + " | ".join(progress_bars) + " |"
    
    key = "Ab"
    scale = "aeolian"
    
    print(f"--- Generating Final Ska Scene (Corrected) in {key} {scale} ---")
    print(f"Progression: {prog_str}")
    
    conn = get_ableton_connection()
    
    # 1. Ensure Tracks Exist (Reuse or Create)
    def ensure_track(name):
        # Scan tracks
        ctx = conn.send_command("get_song_context", {"include_clips": False})
        for tr in ctx.get("tracks", []):
             if tr["name"] == name:
                 print(f"Found existing track '{name}' at index {tr['index']}")
                 return tr["index"]
        # Create
        print(f"Creating new track '{name}'...")
        res = conn.send_command("create_midi_track", {"index": -1})
        new_idx = res["index"]
        conn.send_command("set_track_name", {"track_index": new_idx, "name": name})
        return new_idx

    t1_idx = ensure_track("Ska Keys Final")
    t2_idx = ensure_track("Ska Bass Final")
    
    print(f"Target Indices: {t1_idx}, {t2_idx}")
    
    # scene_index = 0 (First scene of new tracks)
    scene_idx = 0
    
    # 2. Generate Keys (Ska Skank)
    print("Generating Keys (Ska Skank)...")
    generate_chord_progression_advanced(
        track_index=t1_idx,
        clip_index=scene_idx,
        key=key,
        scale=scale,
        rhythm_style="ska_skank",
        velocity=90,
        progression=prog_str
    )

    # 3. Generate Bass (Jazz Walking for smoother feel)
    print("Generating Bass (Jazz Walking)...")
    generate_bassline_advanced_wrapper(
        track_index=t2_idx,
        clip_index=scene_idx,
        key=key,
        scale=scale,
        style="walking", # Jazz Walking
        progression=prog_str,
        velocity=100,
        octave=1
    )
    
    print("Done.")

if __name__ == "__main__":
    generate_final_ska()
