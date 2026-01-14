from .constants import SCALES
from typing import List, Dict, Tuple, Optional

# Note name to MIDI offset lookup
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

class Scale:
    """Represents a musical scale structure."""
    def __init__(self, name: str, intervals: List[int]):
        self.name = name
        self.intervals = intervals
    
    def get_notes(self, root_midi: int) -> List[int]:
        """Get MIDI notes for this scale starting at root."""
        return [root_midi + i for i in self.intervals]

class Mode:
    """Represents a musical mode with logic to derive chords."""
    
    # Standard Diatonic Modes (intervals relative to Major scale)
    MODES = {
        'ionian':     [0, 2, 4, 5, 7, 9, 11], # Major
        'dorian':     [0, 2, 3, 5, 7, 9, 10],
        'phrygian':   [0, 1, 3, 5, 7, 8, 10],
        'lydian':     [0, 2, 4, 6, 7, 9, 11],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'aeolian':    [0, 2, 3, 5, 7, 8, 10], # Natural Minor
        'locrian':    [0, 1, 3, 5, 6, 8, 10],
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
        'bebop_dominant': [0, 2, 4, 5, 7, 9, 10, 11], # Mixolydian + Major 7
        'bebop_major':    [0, 2, 4, 5, 7, 8, 9, 11],  # Major + #5 (b6) - or is it b6? User said #5 between 5 and 6. 
                                                      # User: 1-2-3-4-5-#5-6-7. Intervals: 0, 2, 4, 5, 7, 8, 9, 11. Correct.
        'bebop_dorian':   [0, 2, 3, 4, 5, 7, 9, 10]   # Dorian + Major 3. Intervals: 0, 2, 3, 4, 5, 7, 9, 10.
    }
    
    def __init__(self, name: str, key_root: int):
        self.name = name.lower()
        self.key_root = key_root
        self.intervals = self.MODES.get(self.name, self.MODES['ionian'])
        
    def get_scale_notes(self) -> List[int]:
        """Return the 7 notes of the mode in the current key."""
        return [self.key_root + i for i in self.intervals]
        
    def get_chord(self, degree: int, extensions: str = "7") -> List[int]:
        """
        Get the chord at a specific scale degree (1-based).
        e.g. Dorian, degree=2 -> returns the ii chord (which is minor7 in Dorian? Wait.)
        
        Logic: Build thirds from the scale notes.
        """
        # 0-indexed degree
        d = (degree - 1) % 7
        
        # We need an infinite scale to wrap around
        # But efficiently: we just take the indices relative to the scale length (7)
        # Root, 3rd, 5th, 7th are indices d, d+2, d+4, d+6
        
        indices = [d, d+2, d+4]
        if "7" in extensions:
            indices.append(d+6)
        if "9" in extensions:
            indices.append(d+8)
            
        notes = []
        scale_notes = self.get_scale_notes()
        
        for idx in indices:
            # Calculate which scale note this is (modulo 7)
            # and how many octaves up it is
            s_idx = idx % 7
            octave_shift = (idx // 7)
            
            # Get the base pitch from our scale definition
            # Note: intervals are 0-based from key_root
            interval = self.intervals[s_idx]
            
            # Total semitones from key root = interval + octave*12
            pitch = self.key_root + interval + (octave_shift * 12)
            notes.append(pitch)
            
        return notes

    def get_roman_numeral(self, degree: int) -> str:
        """
        Analyze the chord at degree and return Roman Numeral (e.g. 'ii', 'IV', 'v').
        """
        chord_notes = self.get_chord(degree, extensions="") # Triad only for analysis
        # Root is chord_notes[0]
        root = chord_notes[0]
        third = chord_notes[1]
        fifth = chord_notes[2]
        
        r_to_3 = third - root
        r_to_5 = fifth - root
        
        numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
        base_num = numerals[degree-1]
        
        is_minor = (r_to_3 == 3)
        is_dim = (r_to_5 == 6)
        is_aug = (r_to_5 == 8)
        
        rn = base_num.lower() if is_minor or is_dim else base_num
        
        if is_dim:
            rn += "dim"
        elif is_aug:
            rn += "+"
            
        return rn

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

# Compatibility wrapper for existing code using get_chord_notes via string
def get_chord_notes(root_note, scale_name, numeral, inversion: int = 0):
    """
    Parse Roman numeral and return chord notes.
    Supports accidentals: bII, bVII, #IV, etc.
    Accidentals are relative to MAJOR scale reference.
    """
    import re
    from .constants import SCALES

    MAJOR = SCALES["major"]
    degree_map = {"i": 0, "ii": 1, "iii": 2, "iv": 3, "v": 4, "vi": 5, "vii": 6}

    # Strip comments like V(SecDom)
    numeral_base = re.sub(r"\(.*?\)", "", numeral.strip())

    # Parse leading accidentals: bb, b, ##, #
    m = re.match(r"^(?P<acc>(bb|##|b|#)*)?(?P<body>.*)$", numeral_base)
    acc = (m.group("acc") or "")
    body = (m.group("body") or "")

    # Accidentals shift in semitones
    acc_shift = acc.count("#") - acc.count("b")  # bb=-2, b=-1, #=+1, ##=+2

    # Quality tags
    body_l = body.lower()
    is_dim = ("dim" in body_l) or ("°" in body)
    is_aug = ("aug" in body_l) or ("+" in body)
    is_maj7 = ("maj7" in body_l) or ("maj" in body_l) or ("Δ" in body)
    has_7 = ("7" in body_l)
    has_9 = ("9" in body_l)

    # Extract roman numeral portion (i, ii, iii, iv, v, vi, vii)
    # Remove quality/ext tokens for degree detection
    deg_clean = re.sub(r"(dim|aug|maj7|maj|min7|min|m7|m|°|\+|7|9)", "", body_l)
    deg_clean = deg_clean.strip()

    # Keep just roman letters i/v
    deg_clean = re.sub(r"[^iv]", "", deg_clean)

    degree_idx = degree_map.get(deg_clean, 0)

    # Determine chord "case" from original body (major vs minor)
    first_roman = re.search(r"[IViv]+", body)
    starts_lower = bool(first_roman and first_roman.group(0)[0].islower())
    is_minor = starts_lower and (not is_dim) and (not is_aug)

    # Root interval: if accidentals present, use MAJOR degree reference to avoid double-flatting
    if acc:
        root_interval = MAJOR[degree_idx] + acc_shift
    else:
        # If no accidental, use the diatonic tone from the current mode
        scale = SCALES.get(scale_name, MAJOR)
        root_interval = scale[degree_idx]

    chord_root = root_note + root_interval

    # Build chord tones by quality
    if is_dim:
        triad = [0, 3, 6]
    elif is_aug:
        triad = [0, 4, 8]
    elif is_minor:
        triad = [0, 3, 7]
    else:
        triad = [0, 4, 7]

    notes = [chord_root + i for i in triad]

    # 7ths
    if has_7 or is_maj7:
        if is_dim:
            seventh = 9 if ("dim7" in body_l) else 10
        elif is_maj7:
            seventh = 11
        elif is_minor:
            seventh = 10
        else:
            seventh = 10
        notes.append(chord_root + seventh)

    # 9ths
    if has_9:
        notes.append(chord_root + 14)

    if inversion > 0:
        notes = invert_chord(notes, inversion)

    return notes


def voice_lead_progression(progression_notes: list) -> list:
    if len(progression_notes) <= 1:
        return progression_notes
    result = [progression_notes[0]]
    for i in range(1, len(progression_notes)):
        prev_chord = result[-1]
        current_chord = progression_notes[i]
        best_inversion = current_chord
        best_distance = float('inf')
        for inv in range(len(current_chord)):
            inverted = invert_chord(current_chord, inv)
            distance = sum(abs(inverted[j] - prev_chord[j % len(prev_chord)]) 
                          for j in range(len(inverted)))
            if distance < best_distance:
                best_distance = distance
                best_inversion = inverted
        result.append(best_inversion)
    return result

def get_scale_degree(note_midi: int, root_midi: int, scale_name: str = "major") -> int:
    rel_semitone = (note_midi - root_midi) % 12
    from .constants import SCALES
    scale = SCALES.get(scale_name, SCALES["major"])
    if rel_semitone in scale:
        return scale.index(rel_semitone) + 1
    return 0

def get_nearest_chord_tone(target_pitch: int, chord_notes: list) -> int:
    best_note = chord_notes[0]
    best_dist = float('inf')
    for base_note in chord_notes:
        base_pc = base_note % 12
        target_octave = (target_pitch // 12) * 12
        candidates = [base_pc + target_octave - 12, base_pc + target_octave, base_pc + target_octave + 12]
        for cand in candidates:
            dist = abs(cand - target_pitch)
            if dist < best_dist:
                best_dist = dist
                best_note = cand
    return best_note
