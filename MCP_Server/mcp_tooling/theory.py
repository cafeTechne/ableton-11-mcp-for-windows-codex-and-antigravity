from .constants import SCALES

# Note name to MIDI offset lookup
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def key_to_midi(key: str, octave: int = 4) -> int:
    """
    Convert key name to MIDI note number.
    Handles 'Bb', 'C#', 'min', 'Min', etc.
    """
    k = key.strip()
    
    # Extract note part
    note_part = k[:1].upper()
    if len(k) > 1:
        c2 = k[1]
        if c2 == "#":
            note_part += "#"
        elif c2.lower() == "b": 
             note_part += "b"
             
    # Normalize flats
    note_part = note_part.replace("Db", "C#").replace("Eb", "D#").replace("Gb", "F#").replace("Ab", "G#").replace("Bb", "A#")
    note_part = note_part.replace("Cb", "B").replace("Fb", "E")
    
    try:
        idx = NOTE_NAMES.index(note_part)
        return 12 * (octave + 1) + idx
    except ValueError:
        return 60 + (12 * (octave - 4))


def invert_chord(notes: list, inversion: int = 0) -> list:
    """
    Apply inversion to a chord.
    
    Args:
        notes: List of MIDI pitches (root position)
        inversion: 0=root, 1=first, 2=second, 3=third (for 7ths)
    
    Returns:
        List of MIDI pitches with inversion applied
    
    Example:
        [60, 64, 67] (C major root) with inversion=1 -> [64, 67, 72] (1st inversion)
    """
    if not notes or inversion == 0:
        return notes
    
    # Clamp inversion to valid range
    max_inv = len(notes) - 1
    inversion = min(inversion, max_inv)
    
    result = list(notes)
    for _ in range(inversion):
        # Move lowest note up an octave
        lowest = result.pop(0)
        result.append(lowest + 12)
    
    return result


def get_chord_notes(root_note, scale_name, numeral, inversion: int = 0):
    """
    Get MIDI note values for a chord given a root, scale, and numeral.
    
    Args:
        root_note (int): MIDI root note of the KEY.
        scale_name (str): Name of scale (major, minor, etc).
        numeral (str): Roman numeral degree (e.g. ii7, V).
        inversion (int): 0=root, 1=first, 2=second, 3=third inversion
        
    Returns:
        List[int]: List of MIDI pitches.
    """
    # scale logic
    scale = SCALES.get(scale_name, SCALES["major"])
    # Map Numeral to Scale Degree
    degree_map = {"i": 0, "ii": 1, "iii": 2, "iv": 3, "v": 4, "vi": 5, "vii": 6}
    
    # Clean numeral
    num_clean = numeral.lower().replace("dim", "").replace("aug", "").replace("maj", "").replace("min", "").replace("7", "").replace("9", "")
    # Handle borrowed chords (bIII, bVI, etc.)
    num_clean = num_clean.replace("b", "").replace("#", "")
    degree_idx = degree_map.get(num_clean, 0)
    
    # Base Root index in scale
    scale_degree = degree_idx
    
    # Build triad: Root, 3rd, 5th
    indices = [scale_degree, (scale_degree + 2) % 7, (scale_degree + 4) % 7]
    
    # Add 7th if requested
    if "7" in numeral:
        indices.append((scale_degree + 6) % 7)
    # Add 9th? 
    if "9" in numeral:
         indices.append((scale_degree + 8) % 7)
         
    notes = []
    for i in indices:
        # Calculate pitch regarding octave wrapping relative to the KEY root
        
        scale_val = scale[i]
        
        # Calculate how many octaves above the start of the scale this degree is.
        # This is strictly theoretical relative logic
        # e.g. if we are at index i, how many times did we wrap around 7?
        # But we build intervals from the scale_degree.
        
        # We need the absolute index in the infinite scale arrray.
        # The base_step is the interval distance from key root.
        # e.g. V chord. Root=4. 3rd=6. 5th=1 (next octave).
        
        base_step = degree_idx + (2 if i == indices[1] else 4 if i == indices[2] else 
                                  6 if (len(indices) > 3 and i == indices[3]) else 
                                  8 if (len(indices) > 4 and i == indices[4]) else 0)
                                  
        # If it's the root of the chord (index 0 of indices), base_step = degree_idx.
        
        cycles = base_step // 7
        step_mod = base_step % 7
        
        # Retrieve semitone offset from scale
        # If scale is [0,2,4...]
        semitones_in_scale = scale[step_mod]
        
        semitones_total = semitones_in_scale + (cycles * 12)
        
        notes.append(root_note + semitones_total)
    
    # Apply inversion if requested
    if inversion > 0:
        notes = invert_chord(notes, inversion)
        
    return notes


def voice_lead_progression(progression_notes: list) -> list:
    """
    Apply voice leading to a progression - minimize movement between chords.
    Returns a new list with inversions chosen for smooth transitions.
    
    Args:
        progression_notes: List of chord note lists (each in root position)
    
    Returns:
        List of chord note lists with voice leading applied
    """
    if len(progression_notes) <= 1:
        return progression_notes
    
    result = [progression_notes[0]]  # Start with first chord as-is
    
    for i in range(1, len(progression_notes)):
        prev_chord = result[-1]
        current_chord = progression_notes[i]
        
        # Try all inversions and pick the one with minimum total movement
        best_inversion = current_chord
        best_distance = float('inf')
        
        for inv in range(len(current_chord)):
            inverted = invert_chord(current_chord, inv)
            # Calculate total voice movement
            distance = sum(abs(inverted[j] - prev_chord[j % len(prev_chord)]) 
                          for j in range(len(inverted)))
            if distance < best_distance:
                best_distance = distance
                best_inversion = inverted
        
        result.append(best_inversion)
    
    return result


def get_scale_degree(note_midi: int, root_midi: int, scale_name: str = "major") -> int:
    """
    Determine the scale degree of a note (1-based).
    Returns 0 if not in scale.
    """
    # Normalize to 0-11 relative to root
    rel_semitone = (note_midi - root_midi) % 12
    scale = SCALES.get(scale_name, SCALES["major"])
    
    if rel_semitone in scale:
        return scale.index(rel_semitone) + 1
    return 0

def get_guide_tones(chord_notes: list) -> list:
    """
    Extract the 3rd and 7th of a chord.
    Assumes chord_notes are sorted [Root, 3rd, 5th, 7th...].
    Simple heuristic: index 1 is 3rd, index 3 is 7th usually.
    """
    guides = []
    if len(chord_notes) > 1:
        guides.append(chord_notes[1]) # 3rd
    if len(chord_notes) > 3:
        guides.append(chord_notes[3]) # 7th
    return guides

def get_nearest_chord_tone(target_pitch: int, chord_notes: list) -> int:
    """
    Find the note in chord_notes closest to target_pitch.
    Auto-octaves the chord notes to find the best match.
    """
    best_note = chord_notes[0]
    best_dist = float('inf')
    
    # Check all chord tones in extended range (-1 to +1 octave relative to target)
    for base_note in chord_notes:
        # Normalize to 0-11
        base_pc = base_note % 12
        # Find octave closest to target
        target_octave = (target_pitch // 12) * 12
        candidates = [
            base_pc + target_octave - 12,
            base_pc + target_octave,
            base_pc + target_octave + 12
        ]
        
        for cand in candidates:
            dist = abs(cand - target_pitch)
            if dist < best_dist:
                best_dist = dist
                best_note = cand
                
    return best_note


