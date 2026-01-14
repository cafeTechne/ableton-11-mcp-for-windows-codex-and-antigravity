from mcp_tooling.generators import generate_chord_progression_advanced, generate_bassline_advanced_wrapper
from mcp_tooling.ableton_helpers import ensure_track_exists, ensure_clip_slot
import logging

# Test Script mimicking the user's request but using standard interface
def run():
    print("Testing Updated Standard Generators (G Phrygian)...")
    
    # Track Setup (Scenes 0-4)
    keys_track = ensure_track_exists(None, prefer="midi")
    bass_track = ensure_track_exists(None, prefer="midi")
    
    print(f"Tracks: Keys={keys_track}, Bass={bass_track}")
    
    for i in range(5):
        print(f"Generating Scene {i}...")
        
        # CHORDS
        # Passing scale='phrygian' and no progression should trigger NEW algo logic
        res = generate_chord_progression_advanced(
            track_index=keys_track,
            clip_index=i,
            key="G",
            scale="phrygian",
            progression="generate", # Explicit trigger just in case, or rely on logic
            rhythm_style="ska_skank", # Updated engine
            beats_per_chord=4.0
        )
        print(f"   Keys: {res}")
        
        # BASS
        # Bass generator parses progression string. 
        # But wait, generate_chord_progression_advanced returns a STATUS STRING not the progression list.
        # How do we coordinate Bass to use the SAME progression?
        # Standard workflow usually requires user to specify progression or use same seed/mood.
        # But here checking purely algorithmic uniqueness.
        # If I call generate_bassline, it will generate its OWN progression if I don't pass one.
        # This will result in Keys and Bass playing different chords!
        
        # ISSUE: The standard `generators.py` interface doesn't return the data object to pass to next function.
        # It assumes static presets or mood-based (random choice from small set).
        # For Algorithmic, how do we sync?
        # We can pass the SAME seed? But python random is global.
        # Or, we just accept they might drift, or we use a specific progression string returned?
        # `generate_chord_progression_advanced` returns a description string "Generated 4 chords...".
        # It doesn't return the progression.
        
        # For this test, let's just accept they might be independent (Polytonal Ska??) 
        # or...
        # We can construct a progression string manually using the new generator first?
        # But the point is to use the Standard Tool.
        
        # Actually, for the User's Request "Create 5 scenes", if they want them to match,
        # they usually use a workflow that generates the progression data first, then calls the tools.
        # BUT the user said "use the workflows @[/generate-chords]".
        # Those workflows operate per-clip.
        
        # For now, let's just run them independently to ensure they simply WORK (don't crash).
        # Syncing them is a deeper architectural issue (Shared Session State?)
        
        res_bass = generate_bassline_advanced_wrapper(
            track_index=bass_track,
            clip_index=i,
            key="G",
            scale="phrygian",
            progression="generate", # Will likely generate different chords
            style="walking",
            beats_per_chord=4.0
        )
        print(f"   Bass: {res_bass}")

if __name__ == "__main__":
    run()
