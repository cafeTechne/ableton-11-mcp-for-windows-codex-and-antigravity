from typing import List, Dict, Union
from .theory import get_chord_notes, key_to_midi

def parse_bar_chart(
    prog_str: str, 
    key_root: int, 
    scale_name: str, 
    beats_per_bar: float = 4.0
) -> List[Dict]:
    """
    Parses a string like "| i | IV V | ii |" into detailed progression data.
    """
    # Remove outer pipes if empty
    raw_bars = [b.strip() for b in prog_str.strip('|').split('|')]
    
    prog_data = []
    
    for bar_idx, content in enumerate(raw_bars):
        if not content.strip(): continue
        
        # Split by whitespace for chords within a bar
        chords = content.split()
        if not chords: continue
        
        dur_per_chord = beats_per_bar / len(chords)
        
        for ch_name in chords:
            # Parse notes
            notes = get_chord_notes(key_root, scale_name, ch_name)
            
            prog_data.append({
                "root": notes[0] if notes else key_root,
                "tones": notes,
                "duration": dur_per_chord,
                "chord": ch_name, # Standard key for generators.py
                "roman": ch_name, # Alias
                "bar": bar_idx + 1
            })
            
    return prog_data
