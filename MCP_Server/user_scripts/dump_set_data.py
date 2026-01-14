import json
import logging
import os
import sys
from typing import Dict, Any, List

# Add parent directory to path to allow importing mcp_tooling
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tooling.connection import get_ableton_connection

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dump_set_data")

def dump_set_data(output_file: str = "current_set_context.json"):
    """
    Connects to Ableton, retrieves full song context including detailed clip info,
    and saves it to a JSON file.
    """
    logger.info("Connecting to Ableton Live...")
    conn = get_ableton_connection()

    logger.info("Fetching high-level song context...")
    # Get basic context with clips included (this gives us the structure and basic clip info)
    context = conn.send_command("get_song_context", {"include_clips": True})
    
    if not context:
        logger.error("Failed to retrieve song context.")
        return

    tracks = context.get("tracks", [])
    logger.info(f"Found {len(tracks)} tracks. Iterating to get detailed clip info...")

    # Iterate through tracks to enrich clip data
    for track in tracks:
        track_index = track.get("index")
        clips = track.get("clips", [])
        
        if not clips:
            continue
            
        logger.info(f"Processing {len(clips)} clips on track {track_index} ({track.get('name')})...")
        
        enriched_clips = []
        for clip in clips:
            slot_index = clip.get("slot")
            try:
                # Fetch detailed info for this clip
                details = conn.send_command("get_clip_details", {
                    "track_index": track_index,
                    "clip_index": slot_index
                })
                
                if "status" in details and details["status"] == "error":
                    logger.warning(f"Could not get details for clip at T{track_index}:S{slot_index}: {details.get('message')}")
                    enriched_clips.append(clip) # Keep basic info if detailed fails
                else:
                    # Merge basic info with detailed info
                    # detailed info usually has more up-to-date properties
                    clip.update(details)
                    enriched_clips.append(clip)
                    
            except Exception as e:
                logger.error(f"Error fetching clip details for T{track_index}:S{slot_index}: {e}")
                enriched_clips.append(clip)
        
        # Update the track's clips list with the enriched versions
        track["clips"] = enriched_clips

    # Save to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved set data to {output_file}")
    except Exception as e:
        logger.error(f"Error saving to JSON file: {e}")

if __name__ == "__main__":
    dump_set_data()
