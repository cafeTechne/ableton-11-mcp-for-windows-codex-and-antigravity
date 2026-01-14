import sys
import os
import random
import logging

# Add the parent directory to sys.path to allow importing from mcp_tooling
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import generate_chord_progression_advanced
from mcp_tooling.chords import get_all_progressions_by_category

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gemini_track_generator")

def main():
    logger.info("Starting Gemini Track Generator (Generic Reset)...")
    
    conn = get_ableton_connection()
    track_index = 1 # Track 2 is index 1
    start_scene = 0
    num_scenes = 20
    
    logger.info(f"Targeting Track {track_index + 1} for {num_scenes} scenes (starting at {start_scene}).")
    
    # Pre-fetch generic pools
    # get_all_progressions_by_category returns list of tuples: (chords, moods, source)
    major_progs = [{'chords': p[0], 'moods': p[1], 'source': p[2], 'category': 'major'} 
                   for p in get_all_progressions_by_category('major')]
                   
    minor_progs = [{'chords': p[0], 'moods': p[1], 'source': p[2], 'category': 'minor'} 
                   for p in get_all_progressions_by_category('minor')]
                   
    generic_pool = major_progs + minor_progs
    
    logger.info(f"Loaded {len(generic_pool)} generic progressions.")

    # --- SETUP TRACES ---
    # Ensure all target tracks are MIDI tracks.
    target_indices = [1, 2, 3, 4, 8, 9, 10, 11, 12]
    
    logger.info("Verifying target tracks...")
    for idx in target_indices:
        try:
            info = conn.send_command("get_track_info", {"track_index": idx})
            if info and info.get("type") != "midi":
                # CRITICAL SAFETY FIX: Do not delete tracks.
                logger.error(f"Track {idx} ({info.get('name')}) is NOT a MIDI track (Type: {info.get('type')}).")
                logger.error("Skipping verification for this track. Generation may fail for this specific index.")
                # We continue to the next track in verification, and let the generation loop verify individually or fail gracefully.
        except Exception as e:
            logger.warning(f"Could not verify track {idx}: {e}")

    for i in range(num_scenes):
        scene_index = start_scene + i
        
        # 1. Randomly select a progression from the generic pool
        prog_data = random.choice(generic_pool)
        chords = prog_data['chords']
        
        # Determine strict category for labeling
        cat = prog_data.get('category', 'generic')
        
        # Format progression string
        prog_str = " ".join(chords)
        
        logger.info(f"Scene {scene_index + 1}: Generating {cat} chords: {prog_str}")
        
        # --- CHORD GENERATION ---
        # Track 2: Ska Upstrokes (Index 1)
        # Track 3: Down Strokes (Index 2)
        # Track 4: Octave Jumps (Index 3)
        # Track 5: Release/Long (Index 4)
        
        # --- CHORD GENERATION ---
        # Track 2: Ska Upstrokes (Index 1)
        # Track 3: Down Strokes (Index 2)
        # Track 4: Octave Jumps (Index 3)
        # Track 5: Release/Long (Index 4)
        
        chord_configs = [
            (1, "ska_upstrokes", "Upstrokes"),
            (2, "reggae_downstrokes", "Downstrokes"),
            (3, "drive_octaves", "Octaves"),
            (4, "ballad", "Release/Long")   
        ]

        for trk_idx, style, label_suffix in chord_configs:
            try:
                # Using updated generator with rhythm_style support
                result = generate_chord_progression_advanced(
                    track_index=trk_idx,
                    clip_index=scene_index,
                    key="C",
                    scale="major",
                    progression=chords,
                    beats_per_chord=4.0,
                    voice_lead=True,
                    rhythm_style=style # New parameter
                )
                
                # Label chord clip
                clip_name = f"{cat}({label_suffix}): {prog_str}"
                conn.send_command("set_clip_name", {
                    "track_index": trk_idx,
                    "clip_index": scene_index,
                    "name": clip_name
                })
                
            except Exception as e:
                logger.error(f"Error generating chord style {style} for scene {scene_index}: {e}")


        # --- BASS GENERATION ---
        # Track 9: Walking (Index 8)
        # Track 10: Anchor (Index 9)
        # Track 11: Drive (Index 10)
        # Track 12: Threat (Index 11)
        # Track 13: Release (Index 12)
        
        bass_configs = [
            (8, "walking", "Walking"),
            (9, "anchor", "Anchor"),
            (10, "drive", "Drive"),
            (11, "threat", "Threat"),
            (12, "release", "Release")
        ]
        
        from mcp_tooling.generators import generate_bassline_advanced_wrapper
        
        for trk_idx, style, label_suffix in bass_configs:
            try:
                result = generate_bassline_advanced_wrapper(
                    track_index=trk_idx,
                    clip_index=scene_index,
                    key="C",
                    scale="major",
                    progression=chords,
                    beats_per_chord=4.0,
                    style=style,
                    velocity=100,
                    octave=1 if style != "threat" else 0 # Lower for threat
                )
                
                conn.send_command("set_clip_name", {
                    "track_index": trk_idx,
                    "clip_index": scene_index,
                    "name": f"Bass({label_suffix}): {prog_str}"
                })
            except Exception as e:
                logger.error(f"Error generating bass {style} for scene {scene_index}: {e}")


    logger.info("Track generation complete!")

if __name__ == "__main__":
    main()
