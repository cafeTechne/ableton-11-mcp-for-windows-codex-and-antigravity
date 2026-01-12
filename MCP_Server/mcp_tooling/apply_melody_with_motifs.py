"""
Single Melody Generator
=======================
Generates one melody track named after the mood.
Each run produces a fresh non-deterministic variation.
Track name = mood name for easy comparison.
"""

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.melody import (
    generate_melody_from_progression, 
    MOOD_PROFILES,
    get_chord_tones_from_scale,
    key_to_midi
)
from mcp_tooling.constants import NOTE_NAMES
import sys
import os

sys.path.append(os.getcwd())


def robust_infer_chord(notes: list, root_key_midi: int, scale_name: str = "mixolydian") -> str:
    """
    Infer chord function (I, ii, etc.) by comparing notes against
    diatonic triads of the target key/scale.
    """
    if not notes: return "I"
    
    unique_pcs = set([n['pitch'] % 12 for n in notes])
    
    # Generate candidates dynamically based on Scale
    candidates = {}
    numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii"] # Generic mapping
    
    for degree in range(7):
        # Get triad pitch classes
        triad_tones = get_chord_tones_from_scale(root_key_midi, scale_name, degree)
        triad_pcs = {t % 12 for t in triad_tones}
        label = numerals[degree]
        candidates[label] = triad_pcs

    best_fit = "?"
    max_overlap = 0
    min_extra = 99
    
    for name, chord_pcs in candidates.items():
        overlap = len(unique_pcs.intersection(chord_pcs))
        extra = len(unique_pcs - chord_pcs)
        
        # Score: Maximize overlap, minimize non-chord tones
        if overlap > max_overlap:
            max_overlap = overlap
            min_extra = extra
            best_fit = name
        elif overlap == max_overlap:
            if extra < min_extra:
                min_extra = extra
                best_fit = name
                
    return best_fit


def generate_melody(mood="allegro", chiptune=False, key="F#", scale="mixolydian", seed=None, variance=0.5, motif=None, bars=None):
    """
    Generate a single melody track named after the mood.
    
    Args:
        mood: Italian term from approved list (default: "allegro")
        chiptune: If True, uses gaming/8-bit mode constraints
        key: Key root (e.g. "C", "F#")
        scale: Scale type ("major", "minor", "mixolydian")
        seed: Random seed for deterministic generation
        variance: 0.0-1.0 Humanization amount
        motif: Forced motif name
        bars: Optional target length in bars (will loop progression)
    """
    conn = get_ableton_connection()
    CHORD_TRACK_IDX = 0
    # Resolve Key/Scale from args
    from mcp_tooling.melody import key_to_midi
    KEY_ROOT = key_to_midi(key, 4)
    SCALE = scale
    
    # Resolve mood name for track title
    mood_key = mood.lower().replace(" ", "_")
    if mood_key not in MOOD_PROFILES:
        print(f"Warning: '{mood}' not found, using 'allegro'")
        mood_key = "allegro"
    
    track_name = f"{mood_key}_chip" if chiptune else mood_key
    
    print(f"Generating melody with mood: {mood_key} (Chiptune: {chiptune})")
    print(f"Key: {key} ({KEY_ROOT}), Scale: {SCALE}")
    if seed: print(f"Seed: {seed}, Variance: {variance}")
    if motif: print(f"Forced Motif: {motif}")
    
    # Find or create track
    target_idx = -1
    for i in range(60):
        try:
            info = conn.send_command("get_track_info", {"track_index": i})
            if info.get("name") == track_name:
                target_idx = i
                break
        except: continue
    
    if target_idx == -1:
        res = conn.send_command("create_midi_track", {})
        if isinstance(res, dict) and 'index' in res: target_idx = res['index']
        elif isinstance(res, int): target_idx = res
        conn.send_command("set_track_name", {"track_index": target_idx, "name": track_name})
        print(f"Created track '{track_name}' at index {target_idx}")
    else:
        print(f"Using existing track '{track_name}' at index {target_idx}")
    
    # Get chord track info
    chord_track_info = conn.send_command("get_track_info", {"track_index": CHORD_TRACK_IDX})
    clip_slots = chord_track_info.get("clip_slots", [])
    
    # Iterate scenes
    for scene_idx, slot in enumerate(clip_slots):
        if not slot.get("has_clip"): continue
        
        print(f"\nScene {scene_idx}:")
        
        # Read chord notes
        c_notes = conn.send_command("get_clip_notes", {"track_index": CHORD_TRACK_IDX, "clip_index": scene_idx})
        if not c_notes: continue
        
        # Analyze progression
        measures = {}
        for n in c_notes:
            m = int(n['start_time'] // 4)
            if m not in measures: measures[m] = []
            measures[m].append(n)
        
        sorted_measures = sorted(measures.keys())
        if not sorted_measures: continue
        
        progression = []
        for m in sorted_measures:
            pitches = measures[m]
            # Infer chord using DYNAMIC KEY
            chord_name = robust_infer_chord(pitches, KEY_ROOT, SCALE)
            progression.append(chord_name)
            
        print(f"  Progression: {progression}")
        
        # Logic to Extend/Loop Progression if bars requested
        if bars is not None:
            current_bars = len(progression)
            if current_bars > 0:
                # Loop progression to fill bars
                import math
                repeats = math.ceil(bars / current_bars)
                progression = (progression * repeats)[:bars]
                
        print(f"  Progression ({len(progression)} bars): {progression}")
        
        if not progression: continue
        
        # Generate melody
        new_notes, length = generate_melody_from_progression(
            chords=progression,
            key=key,
            scale=SCALE,
            beats_per_chord=4.0,
            velocity=95,
            octave=4,
            mood=mood_key,
            chiptune=chiptune,
            seed=seed,
            variance=variance,
            forced_motif=motif
        )
        
        # Write clip
        try: conn.send_command("delete_clip", {"track_index": target_idx, "clip_index": scene_idx})
        except: pass
        conn.send_command("create_clip", {"track_index": target_idx, "clip_index": scene_idx, "length": float(len(progression)*4)})
        conn.send_command("add_notes_to_clip", {"track_index": target_idx, "clip_index": scene_idx, "notes": new_notes})
        
        print(f"  -> {len(new_notes)} notes written")
    
    print(f"\nDone! Track '{track_name}' generated.")
    print("Run again for a new variation.")


def interactive_mode():
    """Interactive CLI for selecting mood and style."""
    print("\n🎹 MELODY GENERATOR 🎹")
    print("=======================")
    
    # 1. Style Selection
    print("\n[Select Style]")
    print("  1. Standard  (Orchestral/Piano - Humanized)")
    print("  2. Chiptune  (8-bit/Gaming - Quantized & Arpeggiated)")
    
    while True:
        choice = input("  > Choice [1-2] (default 1): ").strip()
        if not choice: choice = "1"
        if choice in ["1", "2"]: break
        print("  Invalid choice.")
        
    chiptune = (choice == "2")
    
    # 2. Category Selection
    categories = {
        "1": ("Fast / Energetic", [
            ("allegro", "Fast, cheerful"), ("vivace", "Lively, vivid"), 
            ("presto", "Very fast"), ("con_brio", "With vigor/spirit"), 
            ("spiritoso", "Spirited, witty"), ("con_fuoco", "With fire"), 
            ("propulsivo", "Propulsive energy"), ("brillante", "Sparkling"),
            ("vivo", "Vivid, alive"), ("prestissimo", "Extremely fast")
        ]),
        "2": ("Slow / Emotional", [
            ("adagio", "Slow, at ease"), ("largo", "Broad, very slow"), 
            ("dolce", "Sweet, tender"), ("cantabile", "Singing style"), 
            ("espressivo", "Expressive"), ("lento", "Slow"), 
            ("grave", "Solemn, slow"), ("andante", "Walking pace"),
            ("mesto", "Sad, mournful"), ("doloroso", "Painful, grieving"),
            ("pastorale", "Peaceful, rustic"), ("tranquillo", "Calm"),
            ("sereno", "Serene"), ("calmo", "Calmness")
        ]),
        "3": ("Dark / Intense", [
            ("agitato", "Agitated, restless"), ("furioso", "Furious, angry"), 
            ("minaccioso", "Threatening"), ("inesorabile", "Relentless"), 
            ("tenebroso", "Dark, shadowy"), ("ostinato", "Repetitive persistence"),
            ("motorico", "Motor-like drive"), ("martellato", "Hammered"),
            ("implacabile", "Unforgiving"), ("meccanico", "Mechanical"),
            ("funebre", "Funeral-like"), ("tragico", "Tragic"),
            ("violento", "Violent"), ("tempestoso", "Stormy"),
            ("drammatico", "Dramatic")
        ]),
        "4": ("Playful / Light", [
            ("giocoso", "Playful"), ("scherzando", "Joking"), 
            ("burlesco", "Burlesque, comic"), ("leggiero", "Light, nimble"), 
            ("grazioso", "Graceful"), ("allegretto", "Moderately fast"),
            ("capriccioso", "Whimsical"), ("buffo", "Comic"),
            ("semplice", "Simple, plain"), ("soave", "Gentle, smooth")
        ]),
        "5": ("Mysterious / Abstract", [
            ("misterioso", "Mysterious"), ("oscuro", "Obscure, dark"), 
            ("enigmatico", "Enigmatic"), ("sospeso", "Suspended"), 
            ("etereo", "Ethereal"), ("vago", "Vague, drifting"),
            ("surreale", "Surreal")
        ]),
        "6": ("Noble / Epic", [
            ("maestoso", "Majestic"), ("eroico", "Heroic"), 
            ("grandioso", "Grand"), ("nobile", "Noble"), 
            ("epico", "Epic"), ("solenne", "Solemn"),
            ("magnifico", "Magnificent"), ("sostenuto", "Sustained")
        ]),
    }
    
    print("\n[Select Mood Category]")
    for key, (name, _) in categories.items():
        print(f"  {key}. {name}")
    print("  0. Enter Manual Mood Name")
    
    while True:
        cat_choice = input(f"  > Choice [0-{len(categories)}] (default 1): ").strip()
        if not cat_choice: cat_choice = "1"
        if cat_choice == "0" or cat_choice in categories: break
        print("  Invalid choice.")
        
    if cat_choice == "0":
        mood = input("\n  > Enter mood name (e.g., 'allegro'): ").strip().lower() or "allegro"
    else:
         # 3. Mood Selection
        name, moods = categories[cat_choice]
        print(f"\n[Select {name} Mood]")
        for i, (m_name, m_desc) in enumerate(moods, 1):
            print(f"  {i}. {m_name.ljust(15)} : {m_desc}")
            
        while True:
            m_choice = input(f"  > Choice [1-{len(moods)}] (default 1): ").strip()
            if not m_choice: m_choice = "1"
            if m_choice.isdigit() and 1 <= int(m_choice) <= len(moods): break
            print("  Invalid choice.")
            
        mood = moods[int(m_choice) - 1][0]

    return mood, chiptune


if __name__ == "__main__":
    import sys
    import argparse
    
    # Check if arguments provided
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Generate melody from chord progression")
        parser.add_argument("mood", nargs="?", default="allegro", help="Mood (e.g., allegro, furioso)")
        parser.add_argument("--chiptune", action="store_true", help="Enable chiptune/gaming mode")
        parser.add_argument("--key", default="F#", help="Key root (e.g. C, F#)")
        parser.add_argument("--scale", default="mixolydian", help="Scale type (major, minor, mixolydian)")
        parser.add_argument("--seed", type=int, help="Random seed")
        parser.add_argument("--variance", type=float, default=0.5, help="Humanization variance (0.0-1.0)")
        parser.add_argument("--motif", help="Force specific motif (e.g. arpeggio_up)")
        parser.add_argument("--bars", type=int, help="Target length in bars (loops chords)")
        
        args = parser.parse_args()
        generate_melody(args.mood, args.chiptune, args.key, args.scale, args.seed, args.variance, args.motif, args.bars)
    else:
        # No args -> Interactive Mode
        try:
            mood, chiptune = interactive_mode()
            
            # Optional: Ask for advanced?
            print("\nUse advanced settings (Key/Scale/Seed/Variance/Motif/Length)? [y/N]")
            adv = input("  > ").strip().lower()
            key, scale, seed, variance, motif, bars = "F#", "mixolydian", None, 0.5, None, None
            
            if adv == 'y':
                k = input("  > Key [F#]: ").strip()
                if k: key = k
                s = input("  > Scale [mixolydian]: ").strip()
                if s: scale = s
                sd = input("  > Seed [Random]: ").strip()
                if sd: seed = int(sd)
                v = input("  > Variance [0.5]: ").strip()
                if v: variance = float(v)
                m = input("  > Motif [None]: ").strip()
                if m: motif = m
                b = input("  > Length (Bars) [Default]: ").strip()
                if b: bars = int(b)
            
            print(f"\n🚀 Launching: Mood='{mood}', Key={key} {scale}, Length={bars or 'Auto'}\n")
            generate_melody(mood, chiptune, key, scale, seed, variance, motif, bars)
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)
