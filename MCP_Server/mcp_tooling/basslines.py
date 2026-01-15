"""
Bassline Generation Module
==========================
Generate bass notes from chord progressions using music theory rules and genre-specific idioms.

Based on detailed harmonic and rhythmic profiles:
- Jazz: Walking bass (quarter notes), guide tone targeting, chromatic approaches
- Rock/Pop: Root-5-Octave, locked to kick, 8th note driving
- Funk/Soul: Syncopated 16ths, ghost notes, octave jumps
- Reggae: Subtractive, one-drop feel, heavy low end
- Bossa Nova: Root-5 pattern with syncopation
- Country: 2-feel (Root-5 on 1 and 3)
"""

import random
from typing import List, Dict, Any, Optional, Union
from .theory import get_chord_notes
from .constants import SCALES

# Bass octave (MIDI note 36 = C2)
DEFAULT_BASS_OCTAVE = 2

# Note names for MIDI conversion
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def key_to_midi(key: str, octave: int = DEFAULT_BASS_OCTAVE) -> int:
    """Convert key name to MIDI note number at specified octave."""
    key_norm = key.upper().replace("DB", "C#").replace("EB", "D#").replace("GB", "F#").replace("AB", "G#").replace("BB", "A#")
    key_clean = key_norm.replace("M", "")
    try:
        return 12 * (octave + 1) + NOTE_NAMES.index(key_clean)
    except ValueError:
        return 36  # Default to C2

def get_chord_root_pitch(root_midi: int, scale_name: str, numeral: str) -> int:
    """Get the bass root note for a chord numeral."""
    chord_notes = get_chord_notes(root_midi, scale_name, numeral)
    if chord_notes:
        return chord_notes[0]
    return root_midi

def get_chord_tones(root_midi: int, scale_name: str, numeral: str) -> List[int]:
    """Get all tones for a chord."""
    return get_chord_notes(root_midi, scale_name, numeral)

def get_approach_note(target_pitch: int, style: str = "chromatic_below") -> int:
    """Get approach note to target pitch."""
    if style == "chromatic_below":
        return target_pitch - 1
    elif style == "chromatic_above":
        return target_pitch + 1
    elif style == "dominant_below": # 5th below
        return target_pitch - 7
    elif style == "fifth_above":
        return target_pitch + 7
    return target_pitch - 1 # Default

# --- GENRE-SPECIFIC GENERATORS ---

# --- Advanced Walking Bass Logic ---

# --- Advanced Walking Bass Logic ---

def pc_distance(a: int, b: int) -> int:
    """Minimum pitch-class distance modulo 12."""
    d1 = (a - b) % 12
    d2 = (b - a) % 12
    return min(d1, d2)

def infer_chord_degrees_from_pcs(root_pc: int, chord_pcs: List[int]) -> Dict[str, int]:
    """
    Infer 3rd/5th/7th pitch classes by interval from root,
    instead of assuming chord_tones list ordering.
    """
    pcs = set([pc % 12 for pc in chord_pcs])
    # third: prefer major 3rd, else minor 3rd
    third = (root_pc + 4) % 12 if (root_pc + 4) % 12 in pcs else (root_pc + 3) % 12
    # fifth: prefer perfect 5th, else diminished 5th, else augmented 5th
    if (root_pc + 7) % 12 in pcs:
        fifth = (root_pc + 7) % 12
    elif (root_pc + 6) % 12 in pcs:
        fifth = (root_pc + 6) % 12
    else:
        fifth = (root_pc + 8) % 12
    # seventh: prefer b7, else natural 7, else diminished 7 (9)
    if (root_pc + 10) % 12 in pcs:
        seventh = (root_pc + 10) % 12
    elif (root_pc + 11) % 12 in pcs:
        seventh = (root_pc + 11) % 12
    else:
        seventh = (root_pc + 9) % 12
    return {"third": third, "fifth": fifth, "seventh": seventh}

def dominant_of(pc: int) -> int:
    """Return pitch class of V of given pc (down a 5th / up a 7)."""
    return (pc + 7) % 12  # e.g. V of C(0) is G(7)

def _next_in_scale(scale_pcs: List[int], target_pc: int, direction: int) -> int:
    """Find next pitch class in scale in the given direction (+1 or -1)."""
    cur = target_pc
    for _ in range(1, 13):
        cur = (cur + direction) % 12
        if cur in scale_pcs:
            return cur
    return target_pc

def create_chromatic_enclosure_with_target(
    target_pitch: int,
    start_time: float,
    velocity: int,
    total_duration: float = 1.0,
    modal_strict: bool = False,
    scale_pcs: List[int] = None,
) -> List[Dict]:
    """
    Neighbor -> neighbor pickup (8th notes).
    Does NOT emit the target note (Beat 1 of next bar handles arrival).
    In modal_strict mode, uses diatonic neighbors instead of chromatic.
    """
    target_pc = target_pitch % 12
    
    if modal_strict and scale_pcs:
        scale_set = set(scale_pcs)
        below_pc = _next_in_scale(scale_set, target_pc, -1)
        above_pc = _next_in_scale(scale_set, target_pc, +1)
        p1 = _get_target_pitch_closest(below_pc, target_pitch)
        p2 = _get_target_pitch_closest(above_pc, target_pitch)
    else:
        # Chromatic neighbors
        lower, upper = target_pitch - 1, target_pitch + 1
        if random.random() < 0.5:
            p1, p2 = lower, upper
        else:
            p1, p2 = upper, lower
        # Clamp to bass register
        p1 = _get_target_pitch_closest(p1 % 12, target_pitch)
        p2 = _get_target_pitch_closest(p2 % 12, p1)

    return [
        {"pitch": p1, "start_time": start_time,       "duration": 0.5, "velocity": int(velocity * 0.85)},
        {"pitch": p2, "start_time": start_time + 0.5, "duration": 0.5, "velocity": int(velocity * 0.90)},
    ]

def parse_chord_numeral_in_context(numeral: str, position_in_progression: int = 0) -> Dict[str, Any]:
    """
    Parse 'IIm7', 'V7alt' with rudimentary functional context extraction.
    """
    numeral_clean = numeral.strip()
    quality = "7"  # default
    
    # 1. Quality Detection
    if "maj7" in numeral or "maj" in numeral or "Δ" in numeral:
        quality = "maj7"
        if "#11" in numeral: quality = "maj7#11"
        
    elif "m7b5" in numeral or "ø" in numeral:
        quality = "m7b5"
        
    elif "dim7" in numeral or "dim" in numeral or "°" in numeral:
        quality = "dim7"
        
    elif "m7" in numeral or "min" in numeral or "min7" in numeral:
        quality = "m7" # Default Dorian
        # Context heuristic:
        if "VI" in numeral.upper(): quality = "m7_aeolian"
        if "III" in numeral.upper(): quality = "m7_phrygian"
        
    elif "alt" in numeral:
        quality = "7alt"
    elif "#11" in numeral:
        quality = "7#11"
    elif "b9" in numeral or "b13" in numeral:
        quality = "7b9" # Diminished/Altered proxy
    
    # Heuristic for minor chords denoted only by case (e.g. 'ii')
    elif numeral[0].islower() and "dim" not in numeral and "7" not in numeral:
        quality = "m7"
        if "vi" in numeral.lower(): quality = "m7_aeolian"
        if "iii" in numeral.lower(): quality = "m7_phrygian"
        
    return {"quality": quality, "raw": numeral}

# Alias for compatibility if needed, though we should update dispatcher
def parse_chord_numeral(numeral: str) -> Dict[str, Any]:
    return parse_chord_numeral_in_context(numeral)

def get_scale_for_chord(root_pc: int, chord_quality: str) -> List[int]:
    """
    Complete modal scale library for Jazz contexts.
    """
    scales = {
        # Major 7th
        "maj7": [0, 2, 4, 5, 7, 9, 11],  # Ionian
        "maj7#11": [0, 2, 4, 6, 7, 9, 11],  # Lydian
        
        # Dominant 7th
        "7": [0, 2, 4, 5, 7, 9, 10],  # Mixolydian (Default)
        "7alt": [0, 1, 3, 4, 6, 8, 10],  # Altered (Super Locrian)
        "7#11": [0, 2, 4, 6, 7, 9, 10],  # Lydian Dominant
        "7b13": [0, 2, 4, 5, 7, 8, 10],  # Mixolydian b6
        "7b9": [0, 1, 3, 4, 6, 7, 9, 10],  # Diminished Half-Whole (Wait, User said 0 1 4 5 etc? HW is 1, b2, #2, 3...)
                                           # HW Dim (Start half step): 0, 1, 3, 4, 6, 7, 9, 10. (C, Db, Eb, E, F#, G, A, Bb) -> fits 7b9 (E G Bb Db)
                                           # User sample: [0, 1, 4, 5, 7, 9, 10]?? That triggers E natural (4) and F (5)?
                                           # Let's use standard HW Diminished for 7b9 chords.
        
        # Minor 7th
        "m7": [0, 2, 3, 5, 7, 9, 10],  # Dorian
        "m7_aeolian": [0, 2, 3, 5, 7, 8, 10],  # Aeolian
        "m7_phrygian": [0, 1, 3, 5, 7, 8, 10],  # Phrygian
        
        # Half-dim
        "m7b5": [0, 2, 3, 5, 6, 8, 10],  # Locrian #2 (or just Locrian 0,1,3,5...)
                                          # User said Locrian Nat 2 : 0, 2, 3, 5, 6, 8, 10.
        
        # Diminished
        "dim7": [0, 2, 3, 5, 6, 8, 9, 11],  # Whole-Half Diminished (Starts Whole Step)? No, Dim7 usually implies usage of HW or WH.
                                            # For 'dim7' chord (C Eb Gb Bbb), WH is common: C D Eb F Gb Ab A B. 
                                            # User supplied: [0, 2, 3, 5, 6, 8, 9, 11]. Standard WH.
        
        # Augmented
        "aug": [0, 2, 4, 6, 8, 10],  # Whole Tone
    }
    
    # Default fallback
    intervals = scales.get(chord_quality, [0, 2, 4, 5, 7, 9, 10]) 
    return [(root_pc + i) % 12 for i in intervals]

def get_bebop_scale(root_pc: int, chord_quality: str) -> List[int]:
    """
    8-note Bebop Scales.
    """
    intervals = []
    if chord_quality in ["7", "7alt", "7#11", "7b9"]:
        # Dominant Bebop: 1 2 3 4 5 6 b7 7
        intervals = [0, 2, 4, 5, 7, 9, 10, 11]
    elif "maj7" in chord_quality:
        # Major Bebop: 1 2 3 4 5 #5 6 7
        intervals = [0, 2, 4, 5, 7, 8, 9, 11]
    elif "m7" in chord_quality:
        # Dorian Bebop: 1 2 b3 3 4 5 6 b7
        intervals = [0, 2, 3, 4, 5, 7, 9, 10]
    else:
        # Fallback to standard 7-note
        return get_scale_for_chord(root_pc, chord_quality)
        
    return [(root_pc + i) % 12 for i in intervals]

def get_blues_scale(root_pc: int, is_minor: bool = False) -> List[int]:
    """Blues scale."""
    if is_minor:
        intervals = [0, 3, 5, 6, 7, 10] # Minor Blues
    else:
        intervals = [0, 2, 3, 4, 5, 6, 7, 9, 10] # Major Blues / Ambiguous (Hybrid)
    return [(root_pc + i) % 12 for i in intervals]

def _get_target_pitch_closest(target_pc: int, current_pitch: int, valid_octaves: range = range(1, 4), min_pitch: int = 28, max_pitch: int = 55) -> int:
    """Find the pitch instance of target_pc closest to current_pitch."""
    # MIDI 36 = C2. Range E1 (28) to G3 (55).
    best_pitch = -1
    min_dist = 999
    
    for oct in range(0, 9): # Search wider, clamp later
        p = (oct + 1) * 12 + target_pc
        # Enforce range limits
        if p < min_pitch or p > max_pitch: continue
            
        dist = abs(p - current_pitch)
        if dist < min_dist:
            min_dist = dist
            best_pitch = p
            
    if best_pitch == -1: return 36 + target_pc # Default fallback
    return best_pitch

def plan_voice_leading_path(start_pitch: int, target_pitch: int, num_steps: int, chord_pcs: List[int], scale_pcs: List[int]) -> List[int]:
    """
    Generate smooth stepwise path from start to target.
    Actually snaps to scale/chord tones now.
    """
    path = []
    if num_steps <= 0: return path
    
    distance = target_pitch - start_pitch
    if distance == 0: return [start_pitch] * num_steps
    step_size = distance / (num_steps + 1)
    
    for i in range(num_steps):
        # FIX: use round() to avoid downward bias
        ideal_pitch = start_pitch + int(round(step_size * (i + 1)))
        pc = ideal_pitch % 12
        
        # SNAP LOGIC
        if pc in scale_pcs:
            path.append(ideal_pitch)
        else:
            # Not in scale? Find nearest neighbor that IS in scale
            # Search +/- 1, 2 semitones
            found = False
            for offset in [1, -1, 2, -2]:
                neighbor = ideal_pitch + offset
                if (neighbor % 12) in scale_pcs:
                    path.append(neighbor)
                    found = True
                    break
            
            if not found:
                # If heavily chromatic or scale sparse, just keep ideal (chromatic passing)
                path.append(ideal_pitch)
            
    return path

def get_beat_4_approach(next_root_pc: int, current_scale_pcs: List[int], current_pitch: int, next_root_pitch_hint: int = None, modal_strict: bool = False) -> int:
    """
    Directional beat 4 approach note selection.
    In modal_strict mode, only uses diatonic neighbors.
    """
    next_target = next_root_pitch_hint if next_root_pitch_hint is not None else _get_target_pitch_closest(next_root_pc, current_pitch)
    going_up = next_target > current_pitch

    if modal_strict:
        # Always diatonic in modal mode
        candidates = [pc for pc in current_scale_pcs if pc_distance(pc, next_root_pc) in [1, 2]]
        if candidates:
            best = min(candidates, key=lambda pc: abs(_get_target_pitch_closest(pc, current_pitch) - next_target))
            return _get_target_pitch_closest(best, current_pitch)
        # Fallback: just use next root directly
        return _get_target_pitch_closest(next_root_pc, current_pitch)
    
    # Non-modal: chromatic approach from direction of travel
    approach_pc = (next_root_pc - 1) % 12 if going_up else (next_root_pc + 1) % 12

    # Occasionally use diatonic neighbor
    if random.random() < 0.25:
        candidates = [pc for pc in current_scale_pcs if pc_distance(pc, next_root_pc) in [1, 2]]
        if candidates:
            best = min(candidates, key=lambda pc: abs(_get_target_pitch_closest(pc, current_pitch) - next_target))
            approach_pc = best

    return _get_target_pitch_closest(approach_pc, current_pitch)

def place_seventh_for_resolution(
    beat_3_pitch: int,
    current_seventh_pc: int,
    next_third_pc: Optional[int],
    current_pitch: int
) -> int:
    """
    Strategic seventh placement. Checks if 7th resolves by step to next 3rd.
    """
    if next_third_pc is None: return beat_3_pitch
    
    seventh_pitch = _get_target_pitch_closest(current_seventh_pc, current_pitch)
    next_third_target = _get_target_pitch_closest(next_third_pc, seventh_pitch)
    
    if abs(next_third_target - seventh_pitch) in [1, 2]:
        return seventh_pitch
    return beat_3_pitch



def maybe_anticipate_downbeat(note: Dict, next_root_pitch: int, probability: float = 0.1) -> List[Dict]:
    """
    Anticipate next chord root by eighth note.
    """
    if random.random() < probability:
        note["duration"] = max(0.3, note["duration"] - 0.5)
        anticipation = {
            "pitch": next_root_pitch,
            "start_time": note["start_time"] + note["duration"],
            "duration": 0.5,
            "velocity": int(note["velocity"] * 0.95)
        }
        return [note, anticipation]
    return [note]

def add_swing_feel(notes: List[Dict], swing_ratio: float = 0.67) -> List[Dict]:
    """Apply swing to off-beat notes (approx X.5)."""
    for note in notes:
        beat_pos = note["start_time"] % 1.0
        if 0.4 < beat_pos < 0.6:
            delay = (swing_ratio - 0.5)
            note["start_time"] += delay
    return notes

def limit_leap(pitch: int, ref: int, max_semitones: int = 5) -> int:
    """Octave-adjust pitch to keep it within max_semitones of ref."""
    if pitch is None or ref is None:
        return pitch
    while pitch - ref > max_semitones:
        pitch -= 12
    while ref - pitch > max_semitones:
        pitch += 12
    return pitch

def humanize(note: Dict, time_jitter: float = 0.012, dur_jitter: float = 0.02, max_dur: float = 0.95) -> Dict:
    """
    Add subtle timing and duration jitter to de-robot a note.
    Clamps timing to prevent crossing beat boundaries.
    """
    orig_start = note["start_time"]
    # Clamp jitter: don't go before bar start, small positive bias
    jitter = random.uniform(-time_jitter, time_jitter)
    if orig_start + jitter < 0:
        jitter = 0
    note["start_time"] = orig_start + jitter
    # Clamp duration to not exceed next beat
    note["duration"] = min(max_dur, max(0.1, note["duration"] + random.uniform(-dur_jitter, dur_jitter)))
    return note

def _gen_jazz_walking(
    root: int,
    chord_tones: List[int],
    next_root: Optional[int],
    start_time: float,
    duration: float,
    velocity: int,
    scale_obj=None,
    previous_pitch: int = None,
    chord_quality: str = "7",
    global_scale_pcs: List[int] = None,  # Modal context
) -> List[Dict]:
    notes = []
    
    # Initialize before use
    implied_dominant_pc = None

    # Timing: don't truncate
    beats = int(round(duration))
    if beats == 0 and duration > 0.5: beats = 1
    if beats <= 0: return notes

    current_pitch = previous_pitch if previous_pitch is not None else root

    root_pc = root % 12
    chord_pcs = [t % 12 for t in chord_tones] if chord_tones else [root_pc]
    chord_pcs_set = set(chord_pcs)
    
    # Determine if we're in modal-strict mode
    modal_strict = global_scale_pcs is not None

    # --- SCALE SELECTION ---
    if global_scale_pcs is not None:
        # Modal context: use ONLY global mode (no chord tone union)
        # Chord tones can be targets, but don't expand the movement vocabulary
        scale_pcs = sorted(set(global_scale_pcs))
    else:
        # Fallback to chord-scale theory
        if chord_quality == "dim7" and next_root is not None:
            next_root_pc = next_root % 12
            if (next_root_pc - root_pc) % 12 == 1:  # up a semitone resolution
                implied_dominant_pc = dominant_of(next_root_pc)
                chord_quality_for_scale = "7b9"
                scale_pcs = get_scale_for_chord(implied_dominant_pc, chord_quality_for_scale)
            else:
                scale_pcs = get_scale_for_chord(root_pc, chord_quality)
        else:
            scale_pcs = get_scale_for_chord(root_pc, chord_quality)

    # Infer structural tones
    degrees = infer_chord_degrees_from_pcs(root_pc, chord_pcs)
    third_pc, fifth_pc, seventh_pc = degrees["third"], degrees["fifth"], degrees["seventh"]

    beat_plan = [None] * beats

    # Beat 1: root anchor (or occasionally implied dominant root if we're in dim7->resolution mode)
    if implied_dominant_pc is not None and random.random() < 0.25:
        t1 = _get_target_pitch_closest(implied_dominant_pc, current_pitch)
    else:
        t1 = _get_target_pitch_closest(root_pc, current_pitch)
    
    # Sanitizer: In modal strict, root must be in scale (or we assume the chord is wrong/borrowed)
    # Actually, root usually defines the chord, so changing root changes harmony significantly.
    # But if we want NO chromaticism, we must snap.
    if modal_strict and global_scale_pcs:
         t1 = _get_target_pitch_closest(
             min(global_scale_pcs, key=lambda p: pc_distance(p, t1 % 12)), 
             t1
         )
    beat_plan[0] = t1

    # Beat 3: guide-tone structure (prefer 3rd/7th 80/20)
    # CHORD TONE FIDELITY: Only target 7th if chord has 4+ tones (extensions)
    if beats >= 3:
        has_seventh = len(chord_pcs) >= 4 or "7" in chord_quality or "maj" in chord_quality
        
        if has_seventh:
            guide_choices = [third_pc, seventh_pc, third_pc, seventh_pc, fifth_pc]  # 80/20-ish mixed
        else:
            guide_choices = [third_pc, fifth_pc, third_pc, root_pc, fifth_pc] # Triad focus
            
        target_pc = random.choice(guide_choices)
        
        # Sanitizer: Beat 3 target must be in scale for strict mode (if we picked a chord tone outside scale?)
        # But if we picked from chord tones, they might be outside scale (borrowed chord). 
        # In modal_strict, we must snap.
        if modal_strict and global_scale_pcs and (target_pc not in global_scale_pcs):
             target_pc = min(global_scale_pcs, key=lambda p: pc_distance(p, target_pc))
             
        beat_plan[2] = _get_target_pitch_closest(target_pc, beat_plan[0])

    # Beat 2: stepwise connector toward beat 3 (snap to scale)
    if beats >= 2:
        start_p = beat_plan[0]
        end_p = beat_plan[2] if beats >= 3 and beat_plan[2] is not None else beat_plan[0]
        path = plan_voice_leading_path(start_p, end_p, 1, chord_pcs, scale_pcs)
        beat_plan[1] = path[0] if path else _get_target_pitch_closest(random.choice(list(set(scale_pcs))), start_p)

    # Beat 4: directional approach to next root
    if beats >= 4 and next_root is not None:
        next_root_pitch_hint = _get_target_pitch_closest(next_root % 12, beat_plan[2] if beat_plan[2] is not None else beat_plan[0])
        beat_plan[3] = get_beat_4_approach(
            next_root % 12,
            scale_pcs,
            beat_plan[2] if beat_plan[2] is not None else beat_plan[0],
            next_root_pitch_hint=next_root_pitch_hint,
            modal_strict=modal_strict
        )

    # Limit leaps between consecutive beats (relaxed for natural walking)
    if beats >= 2:
        beat_plan[1] = limit_leap(beat_plan[1], beat_plan[0], max_semitones=7)
    if beats >= 3:
        beat_plan[2] = limit_leap(beat_plan[2], beat_plan[1], max_semitones=7)
    if beats >= 4:
        beat_plan[3] = limit_leap(beat_plan[3], beat_plan[2], max_semitones=7)

    # Emit notes
    for i in range(beats):
        # Beat 4 enclosure chance (only if we have a next root)
        if i == beats - 1 and beats >= 4 and next_root is not None and random.random() < 0.15:
            target_next = _get_target_pitch_closest(next_root % 12, beat_plan[2] if beat_plan[2] else beat_plan[0])
            enclosure = create_chromatic_enclosure_with_target(
                target_next, start_time + i, velocity, total_duration=1.0,
                modal_strict=modal_strict, scale_pcs=scale_pcs
            )
            notes.extend(enclosure)
            current_pitch = enclosure[-1]["pitch"]
            continue

        pitch = beat_plan[i] if beat_plan[i] is not None else _get_target_pitch_closest(root_pc, current_pitch)

        # Accents: 1 & 3 heavier, 2 & 4 lighter
        this_vel = int(velocity * (1.05 if i % 2 == 0 else 0.90))
        this_dur = 0.92 if i % 2 == 0 else 0.78

        n = {
            "pitch": pitch,
            "start_time": start_time + i,
            "duration": this_dur,
            "velocity": this_vel,
        }
        notes.append(humanize(n))
        current_pitch = pitch

    return notes

def _gen_rock_pop_driving(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Rock/Pop Driving 8ths with Patterns.
    """
    notes = []
    subdivisions = 2 # 8th notes
    steps = int(round(duration * subdivisions))
    
    if steps == 0: return notes
    
    fifth = chord_tones[2] if len(chord_tones) > 2 else root + 7
    octave = root + 12
    
    pattern_type = random.choice(["straight_8", "root_5", "gallop"])
    
    for i in range(steps):
        note_offset = i / subdivisions
        p = root
        v = velocity
        d = 0.45
        
        # Beat logic
        is_downbeat = (i % 2 == 0)
        beat_num = (i // 2) + 1
        
        # Patterns
        if pattern_type == "root_5":
            # Root on 1, 5 on 3 (classic country/rock)
            if beat_num in [3, 4] and is_downbeat: p = fifth
            elif beat_num == 4 and not is_downbeat: p = fifth # push
            
        elif pattern_type == "gallop":
            # Iron Maiden style
            if not is_downbeat: v = int(velocity * 0.7)
            
        else: # straight_8
            # Occasional octave jump on weak beats
            if not is_downbeat and random.random() < 0.2: p = octave
            
        # Add note
        notes.append({
            "pitch": p,
            "start_time": start_time + note_offset,
            "duration": d,
            "velocity": v
        })
        
    return notes

def _gen_ska_bass(
    root: int,
    chord_tones: List[int],
    next_root: Optional[int],
    start_time: float,
    duration: float,
    velocity: int,
    modal_strict: bool = False,
    global_scale_pcs: List[int] = None,
    chord_quality: str = "",
    start_pitch: Optional[int] = None,
    is_phrase_end: bool = False,
    prev_direction: int = 0
) -> List[Dict]:
    """
    """
    notes = []
    beats = int(round(duration))
    if beats <= 0: return notes

    current_pitch = start_pitch if start_pitch is not None else root
    is_dim = "dim" in chord_quality or "°" in chord_quality
    
    if is_dim:
        # Decision: Use High-Tension "Climb" or Standard "Tritone Bounce"?
        # User Logic: "Don't play it out... only when at the end of the passage or probabilistically."
        # Theory: This is a Turnaround figure.
        
        do_climb = is_phrase_end or (random.random() < 0.2)
        
        if do_climb:
            # --- The "Eighth Climb" (Zig-Zag Stack) ---
            # "3-1-3-b5-3-b5-etc"
            
            # 1. Build Diminished Stack (Stack of minor 3rds)
            dim_stack = []
            curr = root
            for _ in range(12): 
                dim_stack.append(curr)
                curr += 3 
            
            notes = []
            step_dur = 0.5 # Eighth notes
            total_steps = int(duration / step_dur)
            
            pitch_sequence = []
            stack_idx = 0
            
            while len(pitch_sequence) < total_steps + 5:
                p1_idx = stack_idx + 1
                p2_idx = stack_idx
                p3_idx = stack_idx + 1
                
                if p3_idx >= len(dim_stack): break
                
                pitch_sequence.append(dim_stack[p1_idx])
                pitch_sequence.append(dim_stack[p2_idx])
                pitch_sequence.append(dim_stack[p3_idx])
                
                stack_idx += 1
                
            for i in range(total_steps):
                if i >= len(pitch_sequence): break
                
                p = pitch_sequence[i]
                t = start_time + (i * step_dur)
                
                notes.append({
                    "pitch": p,
                    "start_time": t,
                    "duration": 0.45,
                    "velocity": velocity if i % 2 == 0 else int(velocity * 0.9)
                })
            return notes
        
        else:
            # --- The "Tritone Bounce" (Fallback) ---
            # Standard, less jarring, but keeps the "tritone importance".
            # Pattern: Root -> b5 -> 3rd/Octave -> b5
            # Rhythm: Quarter notes (walking feel) or Eighths?
            # Let's do Quarter notes to contrast with the "Fast/Intense" climb.
            
            b5_pc = next((p % 12 for p in chord_tones if 5 <= (p - root) % 12 <= 7), (root + 6) % 12)
            third_pc = next((p % 12 for p in chord_tones if 3 <= (p - root) % 12 <= 4), (root + 3) % 12)
            
            notes = []
            for i in range(beats):
                p = root
                if i % 4 == 0: p = current_pitch # Anchor
                elif i % 4 == 1: p = _get_target_pitch_closest(b5_pc, current_pitch, max_pitch=84)
                elif i % 4 == 2: p = _get_target_pitch_closest(third_pc, current_pitch + 7, max_pitch=84)
                else: p = _get_target_pitch_closest(b5_pc, current_pitch, max_pitch=84)
                
                notes.append({
                    "pitch": p,
                    "start_time": start_time + i,
                    "duration": 0.6, # Staccato quarter
                    "velocity": velocity
                })
            return notes

    # --- Standard Ska (Arpeggio + Directional) ---

    # Determine Arpeggio Vocabulary
    # Basic: Root, 3rd, 5th, 6th/7th, Octave
    # We derive these from chord_tones to be harmonically accurate
    root_pc = root % 12
    vocab = sorted([t % 12 for t in chord_tones]) 
    
    # If vocab is small (triad), extend it
    if len(vocab) < 4:
        # Add octave
        vocab.append(root_pc)
    
    # Filter vocab by Modal Strict if needed
    if modal_strict and global_scale_pcs:
        vocab = [p for p in vocab if p in global_scale_pcs]
        if not vocab: vocab = [root_pc]

    # current_pitch defined above
    
    # Direction
    direction = 0
    if next_root is not None:
        target_pitch = _get_target_pitch_closest(next_root % 12, root, max_pitch=84)
        if target_pitch > root: direction = 1
        elif target_pitch < root: direction = -1
    
    # Static Centering (Tie-Breaker for repeated chords)
    # If direction is 0 (next_root == root), we need variation.
    # User Request: "One should ascend and the other should descend".
    # Logic: If we are "High" (> F2/53), go Down. If "Low", go Up.
    # This ensures that a static chord sets up the NEXT move by centering itself.
    # Static Centering & Contrast Logic
    if direction == 0:
        # A. Repeated Chord (Continuity Active)
        if start_pitch is not None:
             # Force mirror direction relative to root
             if start_pitch > root: direction = -1
             elif start_pitch < root: direction = 1
             else: direction = -prev_direction if prev_direction != 0 else 1
        
        # B. New Chord (Directional Contrast)
        # "It sounds weird when they both ascend"
        # Try to oppose the previous motion if we have no strong target pull.
        elif prev_direction != 0:
             direction = -1 if prev_direction > 0 else 1
        
        # C. Default Centering
        if direction == 0:
             if root > 53: direction = -1
             else: direction = 1
    
    for i in range(beats):
        pc = root_pc
        
        # Beat 1: Root (or Continuity Pitch)
        if i == 0:
            pitch = start_pitch if start_pitch is not None else root
        
        # Beat 2/3/4: Deterministic Ska Pattern
        else:
            # Pattern: Root - 5th - Octave/3rd - 5th
            # This guarantees movement and Ska feel.
            
            # Find intervals in vocab
            # 5th (7 semitones)
            fifth_pc = next((p for p in vocab if 6 <= (p - root_pc) % 12 <= 8), (root_pc + 7) % 12)
            
            # 3rd detection (Robust)
            # 1. Check Vocab
            min_3_vocab = next((p for p in vocab if (p - root_pc) % 12 == 3), None)
            maj_3_vocab = next((p for p in vocab if (p - root_pc) % 12 == 4), None)
            
            if min_3_vocab is not None:
                third_pc = min_3_vocab
            elif maj_3_vocab is not None:
                third_pc = maj_3_vocab
            else:
                # 2. Check Scale Context
                if global_scale_pcs:
                    min_3_scale = (root_pc + 3) % 12 in global_scale_pcs
                    maj_3_scale = (root_pc + 4) % 12 in global_scale_pcs
                    if min_3_scale and not maj_3_scale: third_pc = (root_pc + 3) % 12
                    elif maj_3_scale and not min_3_scale: third_pc = (root_pc + 4) % 12
                    else: third_pc = (root_pc + 4) % 12 # Default
                else:
                    # 3. Check Chord Quality Implication
                    # If quality string implies minor ('m', 'dim'), default to minor 3rd
                    if "m" in chord_quality or "dim" in chord_quality or "i" in chord_quality: # Wait, 'i' isn't passed in quality usually
                         third_pc = (root_pc + 3) % 12
                    else:
                         third_pc = (root_pc + 4) % 12
            
            pitch = current_pitch
            
            # Simple Pattern Logic
            if i % 4 == 1: # Beat 2 -> 5th
                pitch = _get_target_pitch_closest(fifth_pc, current_pitch, max_pitch=84)
            elif i % 4 == 2: # Beat 3 -> Octave or 3rd (High)
                # Try Octave first for energy
                octave_target = root + 12
                # If we are already high, maybe 3rd?
                # Just bias towards Octave/High 3rd
                pitch = _get_target_pitch_closest(third_pc, current_pitch + 5, max_pitch=84)
            elif i % 4 == 3: # Beat 4 -> 5th (Return)
                pitch = _get_target_pitch_closest(fifth_pc, current_pitch, max_pitch=84)
            else:
                pitch = current_pitch # Should be covered by Beat 1 logic but safe fallback

        # Check: If pitch == current_pitch (Stagnation), force a move to any neighbor
        if pitch == current_pitch and i > 0:
             # Force 5th or 3rd
             pitch = _get_target_pitch_closest(fifth_pc, current_pitch + 2, max_pitch=84)
             
        notes.append({
            "pitch": pitch,
            "start_time": start_time + i,
            "duration": 0.6 if i % 2 == 0 else 0.5, # Staccato feel
            "velocity": velocity if i == 0 else int(velocity * 0.9)
        })
        current_pitch = pitch

    return notes

def _gen_funk_syncopated(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Funk/Soul Syncopated 16ths
    Rule: The "One" is sacred. Ghost notes. Octave pops. Space.
    """
    notes = []
    # Funk is less about filling every slot, more about the grid
    # We'll generate a 1-bar pattern (16 slots)
    
    octave = root + 12
    flat_seven = root + 10 # approximate
    if len(chord_tones) > 3: flat_seven = chord_tones[3]
    
    # Always hit the ONE
    notes.append({
        "pitch": root,
        "start_time": start_time,
        "duration": 0.6, # fat
        "velocity": int(velocity * 1.1)
    })
    
    # Construct a random syncopated rhythm for the rest of the bar
    # 16th note grid
    grid = [0] * 16
    # 0 = rest, 1 = root, 2 = octave, 3 = ghost, 4 = 7th
    
    # High probability spots for funk
    # the "a" of 1 (1.75), "and" of 2 (2.5), "e" of 3 (3.25), 4 (4.0)
    
    # Preset patterns
    patterns = [
        # Bootsy-ish
        {4: 2, 6: 3, 8: 1, 10: 3, 12: 1, 14: 4},
        # Rocco-ish
        {2: 3, 3: 3, 4: 1, 7: 2, 10: 3, 12: 1, 15: 4},
        # Generic Disco Octaves
        {2: 2, 4: 1, 6: 2, 8: 1, 10: 2, 12: 1, 14: 2}
    ]
    
    selected_pat = random.choice(patterns)
    
    for step, note_type in selected_pat.items():
        if step == 0: continue # Already did the one
        
        step_time = step * 0.25
        if step_time >= duration: break
        
        p = root
        v = velocity
        d = 0.2
        
        if note_type == 2: p = octave
        elif note_type == 3: # Ghost
            p = root # muffled
            v = int(velocity * 0.5)
            d = 0.1
        elif note_type == 4: p = flat_seven
        
        notes.append({
            "pitch": p,
            "start_time": start_time + step_time,
            "duration": d,
            "velocity": v
        })
        
    return notes

def _gen_reggae_dub(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Reggae/Dub
    Rule: Avoid the One (mostly). Emphasize 3 (One Drop). Deep subs.
    """
    notes = []
    
    # Common Reggae Pattern: Drop One, Hit 2 and 3 and 4
    # OR: Hit 3 hard (One Drop)
    
    pattern_type = random.choice(["one_drop", "steppers"])
    
    if pattern_type == "one_drop":
        # Rest on 1. Hit 3.
        # Beat 3 is start_time + 2.0
        if duration >= 3:
            notes.append({
                "pitch": root,
                "start_time": start_time + 2.0, # Beat 3
                "duration": 0.8,
                "velocity": int(velocity * 1.1) 
            })
            # Maybe a pickup to 3?
            notes.append({
                 "pitch": root - 5, # Low 5th
                 "start_time": start_time + 1.5,
                 "duration": 0.4,
                 "velocity": int(velocity * 0.8)
            })
    else:
        # Steppers: Four on floor feel, but bass often syncopated
        # Root on 1, 2, 3, 4?
        pass # simplified for now
        
    # Fallback to simple melodic if pattern logic fails (e.g. short clips)
    if not notes and duration >= 1:
         notes.append({ "pitch": root, "start_time": start_time, "duration": duration, "velocity": velocity })

    return notes
    
def _gen_country_2feel(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Country 2-Feel
    Rule: Root on 1, 5th on 3. Walkups.
    """
    notes = []
    
    fifth = chord_tones[2] if len(chord_tones) > 2 else root + 7
    lower_fifth = root - 5
    
    # Beat 1: Root
    notes.append({
        "pitch": root,
        "start_time": start_time,
        "duration": 0.9,
        "velocity": int(velocity * 1.1)
    })
    
    # Beat 3: 5th (if duration allows)
    if duration >= 3:
        p = lower_fifth if random.random() < 0.5 else fifth
        notes.append({
            "pitch": p,
            "start_time": start_time + 2.0,
            "duration": 0.9,
            "velocity": velocity
        })
        
    # Walkup? (Beat 4)
    if duration >= 4 and next_root:
        # Simple chromatic walk
        notes.append({
            "pitch": next_root - 1, # leading tone
            "start_time": start_time + 3.0,
            "duration": 0.9,
            "velocity": int(velocity * 0.9)
        })
        
    return notes

def _gen_anchor(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Anchor Bass
    Rule: Deep sustained roots. Minimal movement. Grounding.
    """
    return [{
        "pitch": root,
        "start_time": start_time,
        "duration": duration * 0.95,
        "velocity": int(velocity * 1.1)
    }]



def _gen_drive(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Drive Bass
    Rule: Constant uniform rhythm (8ths or 16ths). Octave jumps.
    """
    notes = []
    octave = root + 12
    subdivisions = 2 
    steps = int(round(duration * subdivisions))
    
    if steps == 0: return notes
    
    for i in range(steps):
        offset = i / subdivisions
        pitch = root
        
        # Octave jump on some upbeats for energy
        if i % 2 != 0 and random.random() < 0.4:
            pitch = octave
            
        notes.append({
            "pitch": pitch,
            "start_time": start_time + offset,
            "duration": 0.4,
            "velocity": velocity if i % 2 == 0 else int(velocity * 0.9)
        })
    return notes

def _gen_threat(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Threat Bass
    Rule: Pedal tones (rearticulated). Chromatic approaches. Low rumble.
    """
    notes = []
    # Rapid low pulsing (16ths) or steady quarters with chromatic tension?
    # User asked for "Pedal tones + chromatic approach"
    
    # 1. Pedal tone pulse
    notes.append({
         "pitch": root - 12, # Drop octave for threat
         "start_time": start_time,
         "duration": duration - 0.5,
         "velocity": int(velocity * 0.8)
    })
    
    # 2. Chromatic approach at end
    if next_root:
        approach = next_root - 1 # Chromatic below
        notes.append({
            "pitch": approach,
            "start_time": start_time + duration - 0.5,
            "duration": 0.5,
            "velocity": int(velocity * 1.1)
        })
    
    return notes

def _gen_release(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Release Bass
    Rule: Long notes, few attacks. Gentle.
    """
    # Simply a softer, longer root note, maybe higher octave?
    return [{
        "pitch": root,
        "start_time": start_time,
        "duration": duration,
        "velocity": int(velocity * 0.7) # Softer
    }]



# --- MAIN DISPATCHER ---


def _gen_punk_bass(root, current_time, duration, velocity):
    """
    Driving 8th notes on Root. Punk style.
    """
    notes = []
    # 8th notes = 0.5 beats.
    step = 0.5
    t = 0.0
    while t < duration - 0.01:
        notes.append({
            "pitch": root,
            "start_time": current_time + t,
            "duration": step * 0.9, # Slight separation
            "velocity": int(velocity * random.uniform(0.9, 1.1))
        })
        t += step
    return notes



def _gen_tritone_bass(root, chord_tones, current_time, duration, velocity):
    """
    Walking Tritone Bounce (Root -> b5 -> 3rd/Octave -> b5)
    Quarter note feel.
    """
    # 1. Identify Tritone (b5) and 3rd
    b5_pc = next((p % 12 for p in chord_tones if 5 <= (p - root) % 12 <= 7), (root + 6) % 12)
    # Prefer lower 3rd or octave
    third_pc = next((p % 12 for p in chord_tones if 3 <= (p - root) % 12 <= 4), (root + 3) % 12)
    
    current_pitch = root
    beats = int(max(1, round(duration)))
    notes = []
    
    for i in range(beats):
        p = root
        if i % 4 == 0: p = current_pitch # Anchor
        elif i % 4 == 1: p = _get_target_pitch_closest(b5_pc, current_pitch, max_pitch=84)
        elif i % 4 == 2: p = _get_target_pitch_closest(third_pc, current_pitch + 7, max_pitch=84)
        else: p = _get_target_pitch_closest(b5_pc, current_pitch, max_pitch=84)
        
        notes.append({
            "pitch": p,
            "start_time": current_time + i,
            "duration": 0.6, # Staccato quarter
            "velocity": velocity
        })
    return notes


def generate_bassline_from_progression(
    chords: List[str],
    key: str,
    scale: str = "major",
    beats_per_chord: float = 4.0,
    style: str = "walking", # "jazz", "rock", "funk", "reggae", "country"
    velocity: int = 100,
    octave: int = DEFAULT_BASS_OCTAVE,
    total_bars: Optional[int] = None,
    seed: int = None
) -> tuple: # (notes, length)
    """
    Generate complete bassline.
    style maps to genre-specific generators.
    """
    if seed is not None:
        random.seed(seed)

    root_midi = key_to_midi(key, octave)
    all_notes = []
    
    # Pre-calc roots and chord tones for improved context awareness
    prog_data = []
    prog_data = []
    for chord in chords:
        if isinstance(chord, dict):
            # Pre-parsed data (e.g. from parse_bar_chart)
            prog_data.append(chord)
        else:
            # String parsing
            t = get_chord_tones(root_midi, scale, chord)
            # Use first tone as root if available, else fallback
            r = t[0] if t else get_chord_root_pitch(root_midi, scale, chord)
            prog_data.append({"root": r, "tones": t})
        
    # Calculate timing
    if total_bars:
        beats_total = total_bars * 4
        beats_per_chord = beats_total / len(chords)
    
    current_time = 0.0
    
    # Create Scale Object for Modal/Diatonic context
    from .theory import Mode
    mode_obj = Mode(scale, root_midi)
    
    # Compute global scale pitch classes for modal context
    # Only enforce modal_strict for non-major/minor scales (Phrygian, Dorian, etc.)
    # This allows chromatic approaches in standard jazz (major/minor)
    if scale.lower() not in ("major", "minor", "natural_minor", "harmonic_minor", "melodic_minor"):
        global_scale_pcs = [n % 12 for n in mode_obj.get_scale_notes()]
    else:
        # For standard scales, we usually allow chromaticism in Jazz/Walking.
        # But for Ska (Modal Strict), we need a sanitized set if implied.
        # If user passed a standard scale, we construct it:
        global_scale_pcs = [n % 12 for n in mode_obj.get_scale_notes()]
        
        # User Logic: "If A min (Aeolian), make sure diminished chords imply Harmonic Minor."
        # This means we must allow the Major 7th (Leading Tone) in the valid vocabulary.
        # Otherwise, G# (in G#dim) gets filtered out in A Minor (Natural).
        if scale.lower() in ["minor", "aeolian", "natural_minor"]:
             # Add Major 7th (Interval 11)
             leading_tone = (mode_obj.key_root + 11) % 12
             if leading_tone not in global_scale_pcs:
                 global_scale_pcs.append(leading_tone)
    
    # "Original Mixolydian" / Strict Diatonic Mode Logic
    # If style is 'walking_mixolydian', we force modal_strict using the project's key/scale.
    # This ensures "Chord Tone Fidelity" (1-13 extensions within diatonic scale) and avoids chromaticism.
    force_modal_strict = False
    if style == "walking_mixolydian":
        style = "walking" # Use standard walking generator
        force_modal_strict = True
        if global_scale_pcs is None:
             # Force creation if not already done (e.g. Major/Minor keys)
             global_scale_pcs = [n % 12 for n in mode_obj.get_scale_notes()]
    
    # "Ska Strict" - Non-Chromatic Ska Bass
    if style == "ska_strict":
        style = "ska"
        force_modal_strict = True
        if global_scale_pcs is None:
             global_scale_pcs = [n % 12 for n in mode_obj.get_scale_notes()]
             
    last_pitch = None
    last_direction = 0 # 1 (Up), -1 (Down), 0 (Static)
    
    style_arg = style
    for i, data in enumerate(prog_data):
        # Handle List Style
        if isinstance(style_arg, list):
             style = style_arg[i] if i < len(style_arg) else style_arg[-1]
        else:
             style = style_arg
             
        tones = data["tones"]
        # Root is 0th tone (usually) or data['root'] might be just a pitch class or midi.
        # Ideally: root = tones[0] for bass logic to agree with chord voicing logic.
        root = tones[0] if tones else data["root"]
        
        if isinstance(chords[i], dict):
            chord_name_raw = chords[i].get("roman", "")
        else:
            chord_name_raw = chords[i]
        
        # Quality Analysis
        q_info = parse_chord_numeral(chord_name_raw)
        chord_quality = q_info["quality"]
        
        # Next chord logic
        if i+1 < len(prog_data):
            next_tones = prog_data[i+1]["tones"]
            next_root = next_tones[0] if next_tones else prog_data[i+1]["root"]
            
        # Determine Duration
        duration = data.get("duration", beats_per_chord)
            
        # Ska Repeat Logic (Continuity)
        ska_start_pitch = None
        if style == "ska" and i > 0 and last_pitch is not None:
             prev_root = prog_data[i-1]["root"]
             if root == prev_root: 
                 ska_start_pitch = last_pitch
            
        # Dispatch
        if style in ["jazz", "walking", "swing"]:
            notes = _gen_jazz_walking(
                root, tones, next_root, 
                current_time, beats_per_chord, velocity, 
                scale_obj=mode_obj,
                previous_pitch=last_pitch,
                chord_quality=chord_quality,
                global_scale_pcs=global_scale_pcs if (global_scale_pcs and (scale.lower() not in ("major", "minor") or force_modal_strict)) else None  # Pass global_scale for strict mode
            )
        elif style == "ska":
            notes = _gen_ska_bass(
                root, tones, next_root, 
                current_time, duration, velocity, 
                modal_strict=(global_scale_pcs is not None),
                global_scale_pcs=global_scale_pcs,
                chord_quality=chord_quality,
                start_pitch=ska_start_pitch,
                is_phrase_end=(i == len(prog_data) - 1),
                prev_direction=last_direction
            )
        elif style == "tritone":
            notes = _gen_tritone_bass(root, tones, current_time, duration, velocity)
        elif style in ["rock", "pop", "driving", "metal", "punk"]:
            notes = _gen_rock_pop_driving(root, tones, next_root, current_time, duration, velocity)
        elif style in ["funk", "soul", "rnb", "syncopated"]:
            notes = _gen_funk_syncopated(root, tones, next_root, current_time, duration, velocity)
        elif style in ["reggae", "dub"]:
            notes = _gen_reggae_dub(root, tones, next_root, current_time, duration, velocity)
        elif style in ["country", "blues", "folk"]:
            notes = _gen_country_2feel(root, tones, next_root, current_time, duration, velocity)
        elif style in ["anchor", "root"]:
            notes = _gen_anchor(root, tones, next_root, current_time, duration, velocity)
        elif style in ["drive", "octaves"]:
            notes = _gen_drive(root, tones, next_root, current_time, beats_per_chord, velocity)
        elif style in ["threat", "tension"]:
            notes = _gen_threat(root, tones, next_root, current_time, beats_per_chord, velocity)
        elif style in ["release", "pad"]:
            notes = _gen_release(root, tones, next_root, current_time, beats_per_chord, velocity)
        elif style == "guide_tones":
             # New Guide Tone Style!
             # Need to implement separate function or just use _gen_jazz_walking with specific params?
             # User requested it as separate style.
             # I didn't implement _gen_guide_tones yet.
             # Fallback to walking for now or skip.
             notes = _gen_jazz_walking(
                root, tones, next_root, 
                current_time, beats_per_chord, velocity, 
                scale_obj=mode_obj,
                previous_pitch=last_pitch,
                chord_quality=chord_quality
             )
        else:
            # Default fallback (Root notes)
            notes = [{
                "pitch": root,
                "start_time": current_time,
                "duration": beats_per_chord - 0.1,
                "velocity": velocity
            }]
            
        all_notes.extend(notes)
        if notes:
            last_pitch = notes[-1]["pitch"]
            # Calculate net direction of this chunk
            diff = notes[-1]["pitch"] - notes[0]["pitch"]
            if diff > 0: last_direction = 1
            elif diff < 0: last_direction = -1
            else: last_direction = 0
            
        current_time += duration
        
    return all_notes, current_time

# Alias for compatibility with generators.py import
generate_bassline_advanced = generate_bassline_from_progression
