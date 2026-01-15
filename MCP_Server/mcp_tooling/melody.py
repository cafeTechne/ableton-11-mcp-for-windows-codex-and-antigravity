"""
Melody Generation Module (Chiptune Edition)
============================================
Generates melodies with:
- Diatonic pitch calculation (strict scale adherence)
- 20 approved chiptune mood profiles
- Counter-melody support for call-and-response texture

Mood Categories:
☀️ Bright/Energetic: allegro, vivace, giocoso, brillante, leggiero, con_brio
⚔️ Boss/Dark: agitato, furioso, tenebroso, minaccioso, inesorabile, incisivo, ostinato
🌙 Mysterious: misterioso, oscuro, sospeso, etereo
❤️ Emotional: dolce, tenero, cantabile
"""

import random
from typing import List, Dict, Optional
from .constants import SCALES, NOTE_NAMES

DEFAULT_OCTAVE = 4

# =============================================================================
# CHIPTUNE MOOD PROFILES (20 Approved Terms)
# =============================================================================
# Tuned for chiptune clarity: bright articulation, no orchestral weight

MOOD_PROFILES = {
    # 🕯️ DARK / SERIOUS / SOLEMN
    "grave": {
        "density": 0.35, "durations": [1.0, 2.0, 4.0], "velocity": (70, 95), "leap": 0.2, 
        "rest": 0.1, "sustain": 1.0, "prefer_long": 0.8, "contour": "descending", "tension": 0.6
    },
    "lento": {
        "density": 0.4, "durations": [1.0, 2.0], "velocity": (65, 85), "leap": 0.2, 
        "rest": 0.15, "sustain": 0.95, "prefer_long": 0.7, "contour": "wave", "tension": 0.4
    },
    "largo": {
        "density": 0.3, "durations": [2.0, 4.0], "velocity": (70, 90), "leap": 0.25, 
        "rest": 0.1, "sustain": 1.0, "prefer_long": 0.9, "contour": "descending", "tension": 0.3
    },
    "adagio": {
        "density": 0.45, "durations": [1.0, 2.0, 0.5], "velocity": (60, 85), "leap": 0.25, 
        "rest": 0.15, "sustain": 0.95, "prefer_long": 0.6, "contour": "wave", "tension": 0.25
    },
    "tenebroso": {
        "density": 0.6, "durations": [0.5, 0.25, 1.0], "velocity": (70, 90), "leap": 0.35, 
        "rest": 0.2, "sustain": 0.9, "prefer_long": 0.4, "contour": "descending", "tension": 0.5
    },
    "mesto": {
        "density": 0.4, "durations": [1.0, 2.0], "velocity": (50, 70), "leap": 0.3, 
        "rest": 0.2, "sustain": 0.9, "prefer_long": 0.7, "contour": "descending", "tension": 0.65
    },
    "funebre": {
        "density": 0.35, "durations": [1.0, 2.0], "velocity": (60, 80), "leap": 0.1, 
        "rest": 0.1, "sustain": 0.8, "prefer_long": 0.8, "contour": "static", "tension": 0.6
    },
    "severo": {
        "density": 0.5, "durations": [1.0, 0.5], "velocity": (80, 100), "leap": 0.2, 
        "rest": 0.05, "sustain": 0.8, "prefer_long": 0.5, "contour": "static", "tension": 0.5
    },
    "doloroso": {
        "density": 0.5, "durations": [0.5, 1.0, 2.0], "velocity": (60, 85), "leap": 0.4, 
        "rest": 0.15, "sustain": 0.95, "prefer_long": 0.5, "contour": "descending", "tension": 0.8
    },
    "tragico": {
        "density": 0.6, "durations": [1.0, 0.5, 4.0], "velocity": (80, 110), "leap": 0.45, 
        "rest": 0.1, "sustain": 0.9, "prefer_long": 0.4, "contour": "descending", "tension": 0.9
    },
    "pesante": {
        "density": 0.7, "durations": [0.5, 1.0], "velocity": (100, 127), "leap": 0.2, 
        "rest": 0.05, "sustain": 1.0, "prefer_long": 0.3, "contour": "static", "tension": 0.5
    },
    "maestoso": {
        "density": 0.6, "durations": [1.0, 0.5, 2.0], "velocity": (80, 110), "leap": 0.3, 
        "rest": 0.1, "sustain": 0.9, "prefer_long": 0.5, "contour": "ascending", "tension": 0.3
    },

    # 🎺 SKA / HORNS
    "horn_section": {
        "density": 0.35, "durations": [0.5, 1.0], "velocity": (100, 120), "leap": 0.3,
        "rest": 0.4, "sustain": 0.6, "prefer_long": 0.0, "contour": "static", "tension": 0.3,
        "motif_chance": 0.8, "staccato": True
    },

    # ⚙️ DRIVING / MECHANICAL / RELENTLESS
    "ostinato": {
        "density": 0.95, "durations": [0.5], "velocity": (85, 100), "leap": 0.0, 
        "rest": 0.0, "sustain": 0.8, "contour": "static", "tension": 0.4, "motif_chance": 0.8
    },
    "motorico": {
        "density": 1.0, "durations": [0.25], "velocity": (90, 100), "leap": 0.2, 
        "rest": 0.0, "sustain": 0.5, "contour": "static", "tension": 0.3, "motif_chance": 0.1
    },
    "incisivo": {
        "density": 0.8, "durations": [0.25], "velocity": (95, 115), "leap": 0.3, 
        "rest": 0.1, "sustain": 0.6, "contour": "arch", "tension": 0.45
    },
    "martellato": {
        "density": 0.85, "durations": [0.25, 0.5], "velocity": (110, 127), "leap": 0.2, 
        "rest": 0.05, "sustain": 0.4, "contour": "static", "tension": 0.6
    },
    "inesorabile": {
        "density": 0.9, "durations": [0.5, 0.25], "velocity": (90, 110), "leap": 0.1, 
        "rest": 0.02, "sustain": 0.85, "contour": "static", "tension": 0.55
    },
    "implacabile": {
        "density": 0.95, "durations": [0.25, 0.5], "velocity": (100, 120), "leap": 0.2, 
        "rest": 0.0, "sustain": 0.8, "contour": "ascending", "tension": 0.6
    },
    "meccanico": {
        "density": 0.9, "durations": [0.25], "velocity": (90, 95), "leap": 0.3, 
        "rest": 0.0, "sustain": 0.7, "contour": "wave", "tension": 0.3, "motif_chance": 0.2
    },
    "propulsivo": {
        "density": 0.85, "durations": [0.25, 0.5], "velocity": (90, 110), "leap": 0.3, 
        "rest": 0.05, "sustain": 0.8, "contour": "ascending", "tension": 0.4
    },

    # ⚡ FAST / ENERGETIC / JOYFUL
    "allegro": {
        "density": 0.75, "durations": [0.5, 0.25, 1.0], "velocity": (85, 105), "leap": 0.3, 
        "rest": 0.12, "sustain": 0.85, "contour": "arch", "tension": 0.3
    },
    "allegretto": {
        "density": 0.65, "durations": [0.5, 0.25], "velocity": (80, 100), "leap": 0.3, 
        "rest": 0.15, "sustain": 0.8, "contour": "wave", "tension": 0.25
    },
    "vivace": {
        "density": 0.4, "durations": [1.0, 2.0, 0.5], "velocity": (60, 85),
        "leap": 0.25, "rest": 0.15, "sustain": 0.95, "prefer_long": 0.7,
        "motif_chance": 0.3, "contour": "wave", "tension": 0.25
    },

    # 🎵 SUSTAINED / NOBLE
    "sostenuto": {  # Sustained
        "density": 0.75, "durations": [1.0, 2.0, 4.0], "velocity": (65, 85),
        "leap": 0.15, "rest": 0.02, "sustain": 1.0, "prefer_long": 0.7,
        "legato": True, "breath_chance": 0.4, "structured": True,
        "motif_chance": 0.5, "contour": "wave", "tension": 0.25
    },
    "maestoso": {  # Majestic
        "density": 0.6, "durations": [1.0, 0.5, 2.0], "velocity": (80, 110),
        "leap": 0.3, "rest": 0.1, "sustain": 0.9, "prefer_long": 0.5,
        "motif_chance": 0.4, "contour": "ascending", "tension": 0.3
    },
    
    # 🤪 CHAOTIC / WILD SKA
    "ska_chaos": {
        "density": 0.6, "durations": [0.25, 0.5, 0.25], "velocity": (90, 127),
        "leap": 0.6, "rest": 0.1, "sustain": 0.4, "prefer_long": 0.0,
        "motif_chance": 0.15, "contour": "wave", "tension": 0.7, 
        "staccato": True
    },
    "pastorale": {  # Peaceful/Nature
        "density": 0.5, "durations": [0.5, 1.0], "velocity": (60, 80),
        "leap": 0.25, "rest": 0.1, "sustain": 0.9, "prefer_long": 0.4,
        "motif_chance": 0.35, "contour": "wave", "tension": 0.2
    },
    "marziale": {  # March-like
        "density": 0.7, "durations": [0.5, 0.5, 1.0], "velocity": (90, 110),
        "leap": 0.3, "rest": 0.05, "sustain": 0.7, "prefer_long": 0.1,
        "motif_chance": 0.5, "contour": "ascending", "tension": 0.4
    },
}

# Aliases for convenience
MOOD_ALIASES = {
    # Compounds
    "allegro_giocoso": "giocoso",
    "vivace_leggiero": "vivace",
    "agitato_tenebroso": "agitato",
    "furioso_incisivo": "furioso",
    "inesorabile_ostinato": "inesorabile",
    "misterioso_sospeso": "misterioso",
    "dolce_cantabile": "dolce",
    "tenero_espressivo": "tenero",
    "maestoso_solenne": "maestoso",
    
    # Category Shortcuts
    "dark": "grave",
    "driving": "ostinato", 
    "fast": "allegro",
    "light": "dolce",
    "flowing": "andante",
    "dramatic": "agitato",
    "mysterious": "misterioso",
    "playful": "giocoso",
    "noble": "nobile",
    
    # Common Terms
    "happy": "allegro",
    "sad": "mesto",
    "angry": "furioso",
    "calm": "tranquillo",
    "epic": "epico",
    "scary": "tenebroso",
    "boss": "agitato",
    "final_boss": "inesorabile",
    "chill": "andante"
}

DEFAULT_MOOD = "allegro"

# =============================================================================
# MOTIF LIBRARY
# =============================================================================
# Reusable melodic fragments (scale degrees relative to current position)
# Positive = up, Negative = down

MOTIFS = {
    "ascending_third": [0, 1, 2],        # Stepwise climb (3 notes)
    "descending_third": [0, -1, -2],     # Stepwise descent
    "neighbor_upper": [0, 1, 0],         # Upper neighbor return
    "neighbor_lower": [0, -1, 0],        # Lower neighbor return
    "enclosure": [1, -1, 0],             # Approach from above, below, land
    "leap_stepback": [3, 2, 1],          # Leap up, step back down
    "arpeggio_up": [0, 2, 4],            # Triad arpeggio ascending
    "arpeggio_down": [4, 2, 0],          # Triad arpeggio descending
    "scalar_run_up": [0, 1, 2, 3],       # 4-note ascending run
    "scalar_run_down": [0, -1, -2, -3],  # 4-note descending run
}

# Motif transformations
def _motif_invert(m): return [-d for d in m]
def _motif_retrograde(m): return m[::-1]
def _motif_sequence_up(m): return [d + 2 for d in m]
def _motif_sequence_down(m): return [d - 2 for d in m]

MOTIF_VARIATIONS = {
    "exact": lambda m: m,
    "inversion": _motif_invert,
    "retrograde": _motif_retrograde,
    "sequence_up": _motif_sequence_up,
    "sequence_down": _motif_sequence_down,
}

# =============================================================================
# RHYTHM CELLS (for rhythmic cohesion)
# =============================================================================
# Each cell is a list of durations that sum to 4 beats (one measure)
# Used for rhythmic repetition within phrases

RHYTHM_CELLS = {
    # Energetic / Bright - more subdivisions
    "allegro": [
        [1.0, 0.5, 0.5, 1.0, 1.0],      # Quarter-8th-8th-Quarter-Quarter
        [0.5, 0.5, 1.0, 0.5, 0.5, 1.0], # 8th-8th-Quarter-8th-8th-Quarter
        [1.0, 1.0, 0.5, 0.5, 1.0],      # Syncopated feel
    ],
    # Sustained / Legato - longer notes
    "sostenuto": [
        [2.0, 2.0],                      # Half-Half
        [4.0],                           # Whole note
        [2.0, 1.0, 1.0],                 # Half-Quarter-Quarter
        [1.0, 3.0],                      # Quarter-DottedHalf
    ],
    # Boss / Intense - driving rhythms
    "furioso": [
        [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # Straight 8ths
        [0.5, 0.5, 0.5, 0.5, 1.0, 1.0],  # 8ths to quarters
        [1.0, 0.5, 0.5, 0.5, 0.5, 1.0],  # Accented downbeat
    ],
    # Mysterious - irregular, spacious
    "misterioso": [
        [1.5, 0.5, 2.0],                 # Dotted-Quarter + 8th + Half
        [2.0, 0.5, 1.5],                 # Asymmetric
        [1.0, 2.0, 1.0],                 # Centered weight
    ],
    # Playful - bouncy
    "giocoso": [
        [0.75, 0.25, 0.75, 0.25, 1.0, 1.0],  # Dotted-8th + 16th pattern
        [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0], # Pickup feel
        [1.0, 0.5, 0.5, 0.5, 0.5, 1.0],
    ],
    # Default fallback
    "default": [
        [1.0, 1.0, 1.0, 1.0],            # Straight quarters
        [2.0, 1.0, 1.0],                 # Half + quarters
        [1.0, 1.0, 2.0],                 # Quarters + half
    ],
}

def get_rhythm_cell(mood_key: str) -> list:
    """Get a random rhythm cell appropriate for the mood."""
    # Map moods to rhythm categories
    mood_to_category = {
        # Allegro (Fast/Energetic)
        "allegro": "allegro", "vivace": "allegro", "brillante": "allegro", "leggiero": "allegro",
        "con_brio": "allegro", "presto": "allegro", "prestissimo": "allegro", "vivo": "allegro",
        "spiritoso": "allegro", "con_fuoco": "allegro", "propulsivo": "allegro",
        
        # Giocoso (Playful/Bouncy)
        "giocoso": "giocoso", "scherzando": "giocoso", "burlesco": "giocoso", 
        "capriccioso": "giocoso", "buffo": "giocoso", "allegretto": "giocoso", 
        "grazioso": "giocoso", "fluente": "giocoso",
        
        # Furioso (Driving/Intense)
        "furioso": "furioso", "agitato": "furioso", "incisivo": "furioso", "ostinato": "furioso",
        "inesorabile": "furioso", "impeto": "furioso", "tempestoso": "furioso", 
        "violento": "furioso", "motorico": "furioso", "martellato": "furioso", 
        "implacabile": "furioso", "meccanico": "furioso",
        
        # Sostenuto (Slow/Sustained)
        "sostenuto": "sostenuto", "dolce": "sostenuto", "tenero": "sostenuto", 
        "cantabile": "sostenuto", "largo": "sostenuto", "adagio": "sostenuto", 
        "grave": "sostenuto", "lento": "sostenuto", "maestoso": "sostenuto", 
        "nobile": "sostenuto", "solenne": "sostenuto", "grandioso": "sostenuto", 
        "pastorale": "sostenuto", "mesto": "sostenuto", "funebre": "sostenuto", 
        "doloroso": "sostenuto", "tranquillo": "sostenuto", "sereno": "sostenuto", 
        "calmo": "sostenuto", "languido": "sostenuto", "espressivo": "sostenuto",
        "soave": "sostenuto", "semplice": "sostenuto", "andante": "sostenuto",
        
        # Misterioso (Irregular/Spacious)
        "misterioso": "misterioso", "oscuro": "misterioso", "sospeso": "misterioso", 
        "etereo": "misterioso", "tenebroso": "misterioso", "minaccioso": "misterioso",
        "enigmatico": "misterioso", "vago": "misterioso", "surreale": "misterioso",
        "severo": "misterioso", "pesante": "misterioso", "tragico": "misterioso",
        "drammatico": "misterioso", "appassionato": "misterioso", "ironico": "misterioso"
    }
    category = mood_to_category.get(mood_key, "default")
    cells = RHYTHM_CELLS.get(category, RHYTHM_CELLS["default"])
    return random.choice(cells)

# =============================================================================
# PHRASE CONTOURS
# =============================================================================
import math

CONTOURS = {
    "arch": lambda pos: 1.0 - abs(pos - 0.5) * 2,    # Peak at center
    "wave": lambda pos: 0.5 + 0.5 * math.sin(pos * 2 * math.pi),  # Oscillating
    "ascending": lambda pos: pos,                     # Rising
    "descending": lambda pos: 1.0 - pos,              # Falling
    "static": lambda pos: 0.5,                        # Flat/neutral
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def key_to_midi(key: str, octave: int = 4) -> int:
    """Convert key name to MIDI note number."""
    k = key.upper().replace("DB", "C#").replace("EB", "D#").replace("GB", "F#").replace("AB", "G#").replace("BB", "A#")
    k = k.replace("CB", "B").replace("FB", "E").replace("E#", "F").replace("B#", "C")
    if k.endswith("M"): k = k[:-1]
    try:
        return 12 * (octave + 1) + NOTE_NAMES.index(k)
    except ValueError:
        return 60

def get_scale_pitch(root_midi: int, scale_name: str, degree: int) -> int:
    """Get MIDI pitch for scale degree (0-indexed, handles octave wrapping)."""
    scale = SCALES.get(scale_name, SCALES["major"])
    octave_offset = degree // 7
    degree_in_scale = degree % 7
    if degree < 0:
        octave_offset = -1 + ((degree + 1) // 7)
        degree_in_scale = degree % 7
    semitone_offset = scale[degree_in_scale]
    return root_midi + semitone_offset + (octave_offset * 12)

def get_chord_tones_from_scale(root_midi: int, scale_name: str, chord_degree: int) -> List[int]:
    """Get triad [Root, 3rd, 5th] for chord built on scale degree."""
    return [
        get_scale_pitch(root_midi, scale_name, chord_degree),
        get_scale_pitch(root_midi, scale_name, chord_degree + 2),
        get_scale_pitch(root_midi, scale_name, chord_degree + 4)
    ]

def numeral_to_degree(numeral: str) -> int:
    """Convert Roman numeral to scale degree (0-indexed)."""
    lookup = {"i": 0, "ii": 1, "iii": 2, "iv": 3, "v": 4, "vi": 5, "vii": 6, "VII": 6}
    clean = numeral.lower().replace("dim", "").replace("aug", "").replace("maj", "").replace("min", "").replace("7", "").replace("9", "").replace("b", "").replace("#", "")
    return lookup.get(clean, 0)

def resolve_mood(mood: str) -> dict:
    """Resolve mood name (including aliases) to profile."""
    mood_key = (mood or DEFAULT_MOOD).lower().replace(" ", "_")
    
    # Check aliases first
    if mood_key in MOOD_ALIASES:
        mood_key = MOOD_ALIASES[mood_key]
    
    return MOOD_PROFILES.get(mood_key, MOOD_PROFILES[DEFAULT_MOOD])

def weighted_duration_choice(durations: List[float], prefer_long: float) -> float:
    """Select duration with optional weighting toward longer notes.
    
    Args:
        durations: List of available durations
        prefer_long: 0.0-1.0, probability weight toward longer durations
    """
    if prefer_long <= 0 or len(durations) <= 1:
        return random.choice(durations)
    
    sorted_durs = sorted(durations)
    weights = []
    for i, d in enumerate(sorted_durs):
        # Higher index = longer duration = higher weight when prefer_long > 0
        weight = 1.0 + (prefer_long * i * 2)
        weights.append(weight)
    
    return random.choices(sorted_durs, weights=weights)[0]


def select_motif(profile: dict, contour_direction: float = 0.0) -> tuple:
    """
    Select a motif and variation based on mood profile and contour direction.
    
    Args:
        profile: Mood profile dict
        contour_direction: -1.0 to 1.0 (negative=descending, positive=ascending)
    
    Returns:
        (motif_name, motif_degrees, variation_name)
    """
    leap_chance = profile.get("leap", 0.3)
    prefer_long = profile.get("prefer_long", 0.0)
    
    # Select motif type based on mood characteristics
    # Higher leap = prefer arpeggios and leaps; Lower = scalar/stepwise
    if leap_chance > 0.35:
        candidates = ["arpeggio_up", "arpeggio_down", "leap_stepback", "enclosure"]
    elif prefer_long > 0.5:
        candidates = ["scalar_run_up", "scalar_run_down", "ascending_third", "descending_third"]
    else:
        candidates = list(MOTIFS.keys())  # All motifs available
    
    # Bias direction based on contour
    if contour_direction > 0.3:
        # Ascending contour: prefer upward motifs
        ascending = [m for m in candidates if "up" in m or "ascending" in m or "upper" in m]
        if ascending:
            candidates = ascending + candidates[:2]  # Mix with some variety
    elif contour_direction < -0.3:
        # Descending contour: prefer downward motifs
        descending = [m for m in candidates if "down" in m or "descending" in m or "lower" in m]
        if descending:
            candidates = descending + candidates[:2]
    
    motif_name = random.choice(candidates)
    motif = MOTIFS[motif_name]
    
    # Select variation
    var_weights = {
        "exact": 0.5,        # Most common
        "sequence_up": 0.15,
        "sequence_down": 0.15,
        "inversion": 0.1,
        "retrograde": 0.1,
    }
    var_name = random.choices(list(var_weights.keys()), weights=list(var_weights.values()))[0]
    varied_motif = MOTIF_VARIATIONS[var_name](list(motif))  # Apply variation
    
    return motif_name, varied_motif, var_name


def apply_motif_notes(
    base_degree: int,
    motif: list,
    root_midi: int,
    scale: str,
    start_time: float,
    duration_per_note: float,
    sustain: float,
    vel_min: int,
    vel_max: int
) -> list:
    """
    Generate note dicts from a motif pattern.
    
    Args:
        base_degree: Starting scale degree
        motif: List of relative degree offsets
        root_midi: Key root in MIDI
        scale: Scale name
        start_time: Starting beat position
        duration_per_note: Duration for each note
        sustain: Sustain multiplier
        vel_min/vel_max: Velocity range
    
    Returns:
        List of note dicts
    """
    notes = []
    current_time = start_time
    
    for i, offset in enumerate(motif):
        degree = base_degree + offset
        pitch = get_scale_pitch(root_midi, scale, degree)
        
        # Clamp to melodic range (C4-C6)
        while pitch < 60: pitch += 12
        while pitch > 84: pitch -= 12
        
        # Slight velocity arc within motif
        vel_mod = 5 if i == len(motif) // 2 else 0  # Peak in middle
        vel = random.randint(vel_min, vel_max) + vel_mod
        vel = max(1, min(127, vel))
        
        notes.append({
            "pitch": pitch,
            "start_time": current_time,
            "duration": duration_per_note * sustain * random.uniform(0.9, 1.0),
            "velocity": vel
        })
        current_time += duration_per_note
    
    return notes


def get_contour_bias(contour_type: str, phrase_position: float, range_degrees: int = 6) -> int:
    """
    Get register bias based on phrase position and contour shape.
    
    Args:
        contour_type: One of "arch", "wave", "ascending", "descending", "static"
        phrase_position: 0.0 to 1.0 (start to end of phrase)
        range_degrees: Maximum degrees to shift (+/-)
    
    Returns:
        Degree offset to apply to pitch selection
    """
    func = CONTOURS.get(contour_type, CONTOURS["arch"])
    normalized = func(phrase_position)  # 0.0 to 1.0
    # Map to -range to +range
    return int((normalized - 0.5) * 2 * range_degrees)


def get_phrase_velocity_mod(phrase_position: float) -> int:
    """
    Apply phrase dynamics curve (crescendo to golden ratio peak, then diminuendo).
    
    Args:
        phrase_position: 0.0 to 1.0
    
    Returns:
        Velocity modifier (-5 to +10)
    """
    peak_pos = 0.618  # Golden ratio
    distance = abs(phrase_position - peak_pos)
    return int((1.0 - distance) * 12) - 4  # Range: -4 to +8


# =============================================================================
# STRUCTURAL TENSION ENGINE (Meyer/Narmour/Schenker)
# =============================================================================
# Emotion emerges from expectation management: Implication -> Realization

# Stability weights for scale degrees (Schenker hierarchy)
# Degree 0=Root, 1=2nd, 2=3rd, 3=4th, 4=5th, 5=6th, 6=7th
STABILITY_WEIGHTS = {
    0: 1.0,   # Root - most stable (tonic anchor)
    1: 0.2,   # 2nd - tensions, wants to resolve
    2: 0.7,   # 3rd - chord tone, stable
    3: 0.3,   # 4th - suspension, wants to fall to 3rd
    4: 0.85,  # 5th - very stable (dominant anchor)
    5: 0.25,  # 6th - color tone, mild tension
    6: 0.15,  # 7th - leading tone, strong pull to root
}


def calculate_structural_weight(
    candidate_degree: int,
    current_degree: int,
    prev_interval: int,
    chord_degree: int,
    contour_target: int,
    home_degree: int = 0,
    tension: float = 0.5
) -> float:
    """
    Calculate the structural weight for a candidate pitch based on music theory forces.
    
    Forces (all summed):
    1. Stability (Schenker): Chord tones attract, dissonances repel
    2. Gap Fill (Narmour): Large leaps create strong pull to reverse
    3. Inertia (Narmour Process): Small steps continue direction slightly
    4. Contour (Friedmann): Global shape attraction
    5. Line Integrity (IR3): Penalize consecutive leaps (avoids "sporadic" feel)
    6. Registral Return (IR4): Gravitational pull to phrase starting pitch
    
    Args:
        candidate_degree: The scale degree we're considering (0-6, relative to scale root)
        current_degree: Where we are now (scale degree)
        prev_interval: Previous melodic interval (signed, in scale degrees)
        chord_degree: Current chord root (scale degree)
        contour_target: Target degree from global contour shape
        home_degree: The starting pitch of the phrase (for registral return)
        tension: 0.0 = consonant (resolve), 1.0 = dissonant (resist)
    
    Returns:
        Weight (higher = more likely to be chosen)
    """
    weight = 0.0
    interval = candidate_degree - current_degree
    interval_abs = abs(interval)
    prev_interval_abs = abs(prev_interval)
    
    # --- 1. STABILITY VECTOR (Schenker) ---
    # How stable is this note relative to the current chord?
    relative_to_chord = (candidate_degree - chord_degree) % 7
    stability = STABILITY_WEIGHTS.get(relative_to_chord, 0.3)
    
    # Tension inverts stability: high tension = prefer UNSTABLE notes
    if tension > 0.5:
        stability = 1.0 - stability
    weight += stability * 2.0  # Strong influence
    
    # --- 2. GAP FILL VECTOR (Narmour - Reversal) ---
    # After a leap, we expect reversal
    if prev_interval_abs > 2:  # Previous was a leap (> 3rd)
        # Candidate should move in OPPOSITE direction
        expected_direction = -1 if prev_interval > 0 else 1
        actual_direction = 1 if interval > 0 else (-1 if interval < 0 else 0)
        
        if actual_direction == expected_direction:
            weight += 2.0  # Strong bonus for gap fill (Boosted)
        elif actual_direction == -expected_direction:
            weight -= 2.0  # Strong Penalty for continuing leap direction
    
    # --- 3. INERTIA VECTOR (Narmour - Process) ---
    # After a step, slight bias to continue direction
    if prev_interval_abs <= 2 and prev_interval != 0:  # Previous was step
        expected_direction = 1 if prev_interval > 0 else -1
        actual_direction = 1 if interval > 0 else (-1 if interval < 0 else 0)
        
        if actual_direction == expected_direction:
            weight += 0.8  # Boosted bonus for linearity (was 0.3)
    
    # --- 4. CONTOUR VECTOR (Friedmann) ---
    # Pull towards global contour shape
    distance_to_contour = abs(candidate_degree - contour_target)
    contour_attraction = max(0, 1.0 - distance_to_contour * 0.2)
    weight += contour_attraction * 0.5
    
    # --- 5. LINE INTEGRITY (IR3 - Anti-Sporadic) ---
    # Penalize consecutive leaps
    if prev_interval_abs > 2 and interval_abs > 2:
        weight -= 3.0  # Massive penalty for double leaps (arpeggios excepted by stability)
    
    # --- 6. REGISTRAL RETURN (IR4) ---
    # Slight pull back to the "home" pitch of the phrase
    distance_to_home = abs(candidate_degree - home_degree)
    if distance_to_home > 7: # If far away
        # Bias towards home
        direction_to_home = 1 if home_degree > current_degree else -1
        actual_direction = 1 if interval > 0 else (-1 if interval < 0 else 0)
        if actual_direction == direction_to_home:
            weight += 0.5
    
    # --- 7. STEPWISE PREFERENCE ---
    # Small intervals generally preferred over large
    if interval_abs <= 2:
        weight += 0.8  # Steps are smooth (Boosted from 0.5)
    elif interval_abs >= 5:
        weight -= 0.5  # Large leaps are rare
    
    return max(0.01, weight)  # Ensure non-zero for probability


def weighted_pitch_choice(weights: dict) -> int:
    """
    Choose a pitch (scale degree) based on structural weights.
    
    Args:
        weights: Dict of {degree: weight}
    
    Returns:
        Chosen degree
    """
    degrees = list(weights.keys())
    probs = list(weights.values())
    total = sum(probs)
    probs = [p / total for p in probs]
    
    return random.choices(degrees, weights=probs, k=1)[0]


#
# MAIN GENERATION FUNCTION
# =============================================================================

def generate_melody_from_progression(
    chords: List[str],
    key: str,
    scale: str = "major",
    beats_per_chord: float = 4.0,
    velocity: int = 90,
    octave: int = 4,
    mood: str = None,
    chiptune: bool = False,  # Phase 7: Gaming/Chiptune Mode
    seed: int = None,
    variance: float = 0.5,
    forced_motif: str = None
) -> tuple:
    """
    Generate a melody for a given chord progression.
    
    Args:
        chords: List of chord names (e.g. ["I", "vi", "IV", "V"])
        key: Key root (e.g. "C", "F#")
        scale: Scale type ("major", "minor", "mixolydian")
        beats_per_chord: Duration of each chord in beats
        velocity: Base velocity
        octave: Base octave
        mood: Mood profile name
        chiptune: If True, override with gaming constraints
        seed: Random seed for deterministic generation
        variance: 0.0-1.0, amount of humanization (timing/velocity jitter)
        forced_motif: Name of motif to force (overrides mood)
    """
    if seed is not None:
        random.seed(seed)
    
    profile = resolve_mood(mood)
    
    # Extract profile parameters
    density = profile.get("density", 0.75)
    durations = profile.get("durations", [0.5, 0.25, 1.0])
    vel_min, vel_max = profile.get("velocity", (80, 110))
    leap_chance = profile.get("leap", 0.3)
    rest_chance = profile.get("rest", 0.1)
    sustain = profile.get("sustain", 0.9)
    prefer_long = profile.get("prefer_long", 0.0)
    legato = profile.get("legato", False)
    breath_chance = profile.get("breath_chance", 0.0)
    structured = profile.get("structured", False)
    
    # NEW: Motif and contour parameters
    motif_chance = profile.get("motif_chance", 0.3)
    contour_type = profile.get("contour", "arch")
    tension_profile = profile.get("tension", 0.4)
    
    # PHASE 7: CHIPTUNE OVERRIDES
    if chiptune:
        # Force strict 1/8 and 1/16 grid
        durations = [0.25, 0.5, 0.5, 0.5, 1.0] 
        # Disable "human" nuance
        sustain = 1.0       # Full gate
        vel_min, vel_max = 100, 110  # Consistent velocity
        breath_chance = 0.0 # Machine-like
        legato = False      # Clear articulation
        if variance == 0.5: variance = 0.1 # Reduce default variance for chiptune
        density = min(1.0, density + 0.2) # High density (busy)
        motif_chance = 0.4  # More repetitive
        tension_profile = 0.2       # Consonant (Video game music tends to be tonal)
        
    root_midi = key_to_midi(key, octave)
    all_notes = []
    
    current_time = 0.0
    
    current_degree = 0
    home_degree = 0        # Phase 5b (IR4): Start pitch of phrase
    previous_interval = 0  
    prev_chord = None
    
    # RHYTHM MEMORY: Track rhythm patterns for repetition (A-A-B-A structure)
    # Resolve mood key for rhythm cell lookup
    mood_key = (mood or "allegro").lower().replace(" ", "_")
    if mood_key in MOOD_ALIASES:
        mood_key = MOOD_ALIASES[mood_key]
    
    current_rhythm_cell = get_rhythm_cell(mood_key)
    prev_rhythm_cell = None
    rhythm_index = 0
    rhythmic_repetition = 0.6
    
    # M1: MOTIF REUSE TRACKING
    notes_since_motif = 0
    motif_reuse_threshold = 7
    
    total_duration = len(chords) * beats_per_chord
    
    # Initialize home_degree to first chord root
    if chords:
        home_degree = numeral_to_degree(chords[0])
        current_degree = home_degree
    
    for i, chord_name in enumerate(chords):
        chord_degree = numeral_to_degree(chord_name)
        next_chord = chords[i + 1] if i + 1 < len(chords) else None
        will_change = (next_chord is not None and next_chord != chord_name)
        cursor = 0.0
        
        # RHYTHM CELL SELECTION
        if prev_rhythm_cell is not None and random.random() < rhythmic_repetition:
            current_rhythm_cell = prev_rhythm_cell[:]
        else:
            current_rhythm_cell = get_rhythm_cell(mood_key)
        rhythm_index = 0
        
        while cursor < beats_per_chord:
            # Calculate phrase position (0.0 to 1.0)
            phrase_pos = (current_time + cursor) / total_duration if total_duration > 0 else 0.5
            
            # Phase 6 split logic
            is_antecedent = phrase_pos < 0.5
            
            # Phrase contour
            contour_func = CONTOURS.get(contour_type, CONTOURS["arch"])
            contour_value = contour_func(phrase_pos)
            contour_direction = contour_value - 0.5
            
            # Density check
            if not legato and random.random() > density:
                dur = weighted_duration_choice(durations, prefer_long)
                if cursor + dur > beats_per_chord:
                    dur = beats_per_chord - cursor
                cursor += dur
                continue
            
            # Motif Check (M1 with Forced Reuse)
            remaining_beats = beats_per_chord - cursor
            is_strong_beat = (cursor == 0.0 or cursor == 2.0)
            
            forced_motif_this_cycle = (notes_since_motif >= motif_reuse_threshold and remaining_beats >= 1.5)
            use_motif = forced_motif_this_cycle or (
                is_strong_beat and
                remaining_beats >= 1.5 and
                random.random() < motif_chance
            )
            
            if use_motif:
                # Select and apply motif
                if forced_motif_this_cycle and forced_motif and forced_motif in MOTIFS:
                    motif_name = forced_motif
                    # Use raw motif without variation if forced? Or allow variations?
                    # Let's keep it simple: Exact match if forced
                    motif_degrees = list(MOTIFS[forced_motif])
                    var_name = "exact"
                else:
                    motif_name, motif_degrees, var_name = select_motif(profile, contour_direction * 2)

                motif_dur = min(0.5, max(durations))
                motif_total_dur = motif_dur * len(motif_degrees)
                
                if cursor + motif_total_dur <= beats_per_chord:
                    chord_tone_offset = random.choice([0, 2, 4])
                    contour_bias = get_contour_bias(contour_type, phrase_pos, range_degrees=3)
                    base_degree = chord_degree + chord_tone_offset + contour_bias
                    
                    motif_notes = apply_motif_notes(
                        base_degree=base_degree,
                        motif=motif_degrees,
                        root_midi=root_midi,
                        scale=scale,
                        start_time=current_time + cursor,
                        duration_per_note=motif_dur,
                        sustain=sustain,
                        vel_min=vel_min,
                        vel_max=vel_max
                    )
                    
                    for note in motif_notes:
                        note_phrase_pos = note["start_time"] / total_duration
                        vel_mod = get_phrase_velocity_mod(note_phrase_pos)
                        
                        # Apply Variance
                        if variance > 0:
                            # Timing jitter (+/- 10% of variance)
                            jitter_time = (random.random() - 0.5) * 0.1 * variance
                            note["start_time"] = max(current_time, note["start_time"] + jitter_time)
                            
                            # Velocity jitter (+/- 20 * variance)
                            jitter_vel = int((random.random() - 0.5) * 40 * variance)
                            vel_mod += jitter_vel
                            
                        note["velocity"] = max(1, min(127, note["velocity"] + vel_mod))
                    
                    all_notes.extend(motif_notes)
                        
                    cursor += motif_total_dur
                    current_degree = base_degree + motif_degrees[-1]
                    notes_since_motif = 0
                    continue
            
            # Duration Selection (Rhythm Cells)
            if rhythm_index < len(current_rhythm_cell):
                dur = current_rhythm_cell[rhythm_index]
                rhythm_index += 1
            else:
                dur = weighted_duration_choice(durations, prefer_long)
            
            if cursor + dur > beats_per_chord:
                dur = beats_per_chord - cursor
            
            is_beat_one = (cursor == 0.0)
            is_beat_three = (int(cursor) == 2)
            is_strong_beat = is_beat_one or is_beat_three
            is_last_beat = (int(cursor) >= beats_per_chord - 1)
            is_last_note = (cursor + dur >= beats_per_chord)
            
            if not legato and not is_strong_beat and random.random() < rest_chance:
                cursor += dur
                continue
            
            # Pitch Logic: Phase 5 Comprehensive Grammar
            is_approach_beat = is_last_beat and will_change
            is_cadence = is_last_note and will_change
            
            is_antecedent_end = (phrase_pos >= 0.45 and phrase_pos < 0.55) and is_last_note
            is_consequent_end = is_cadence and phrase_pos >= 0.9
            
            forced_degree = None
            if is_antecedent_end:
                forced_degree = chord_degree + 4  # 5th (Question)
            elif is_consequent_end:
                forced_degree = chord_degree      # Root (Answer)
            
            if forced_degree is None and is_strong_beat:
                chord_tone = random.choice([0, 2, 4])
                forced_degree = chord_degree + chord_tone
            
            contour_target = chord_degree + get_contour_bias(contour_type, phrase_pos, range_degrees=3)
            
            effective_tension = tension_profile
            if is_cadence or is_antecedent_end or is_consequent_end:
                effective_tension = 0.0
            
            if forced_degree is not None:
                target_degree = forced_degree
                previous_interval = target_degree - current_degree
            else:
                # Structural Weighting
                candidate_weights = {}
                for candidate in range(current_degree - 5, current_degree + 6):
                    weight = calculate_structural_weight(
                        candidate_degree=candidate,
                        current_degree=current_degree,
                        prev_interval=previous_interval,
                        chord_degree=chord_degree,
                        contour_target=contour_target,
                        home_degree=home_degree,  # IR4: Home Register
                        tension=effective_tension
                    )
                    candidate_weights[candidate] = weight
                
                target_degree = weighted_pitch_choice(candidate_weights)
                previous_interval = target_degree - current_degree
            
            current_degree = target_degree
            pitch = get_scale_pitch(root_midi, scale, target_degree)
            
            while pitch < 60: pitch += 12
            while pitch > 84: pitch -= 12
            
            vel = random.randint(vel_min, vel_max)
            vel += get_phrase_velocity_mod(phrase_pos)
            if is_beat_one: vel += 10
            vel = max(1, min(127, vel))
            
            note_sustain = sustain * random.uniform(0.9, 1.0)
            if legato and is_last_note and will_change and random.random() < breath_chance:
                note_sustain *= 0.75
            
            # Apply Variance (Humanization)
            start_time = current_time + cursor
            if variance > 0:
                # Timing jitter
                jitter_time = (random.random() - 0.5) * 0.1 * variance
                start_time = max(current_time, start_time + jitter_time)
                
                # Velocity jitter
                jitter_vel = int((random.random() - 0.5) * 40 * variance)
                vel += jitter_vel
                vel = max(1, min(127, vel))

            note_event = {
                "pitch": pitch,
                "start_time": start_time,
                "duration": dur * note_sustain,
                "velocity": vel
            }
            all_notes.append(note_event)
            
            notes_since_motif += 1
            cursor += dur
        
        prev_rhythm_cell = current_rhythm_cell[:]
        prev_chord = chord_name
        current_time += beats_per_chord
    
    return all_notes, current_time


def generate_counter_melody(
    chords: List[str],
    key: str,
    scale: str = "major",
    beats_per_chord: float = 4.0,
    velocity: int = 80,
    octave: int = 4,
    mood: str = None
) -> tuple:
    """
    Generate a counter-melody (off-beats, chord changes).
    Creates call-and-response texture.
    """
    profile = resolve_mood(mood)
    
    vel_min, vel_max = profile["velocity"]
    vel_min = max(50, vel_min - 10)
    vel_max = max(70, vel_max - 10)
    
    root_midi = key_to_midi(key, octave)
    all_notes = []
    current_time = 0.0
    prev_chord = None
    
    for chord_name in chords:
        chord_degree = numeral_to_degree(chord_name)
        is_chord_change = (chord_name != prev_chord)
        prev_chord = chord_name
        
        # Off-beat positions
        off_beat_positions = [0.5, 1.5, 2.5, 3.5]
        if is_chord_change:
            off_beat_positions.insert(0, 2.0)
        
        for pos in off_beat_positions:
            if pos >= beats_per_chord:
                continue
            
            if random.random() > 0.6:
                continue
            
            target_degree = chord_degree + random.choices([0, 2, 4], weights=[0.2, 0.4, 0.4])[0]
            pitch = get_scale_pitch(root_midi, scale, target_degree)
            
            while pitch < 55: pitch += 12
            while pitch > 79: pitch -= 12
            
            dur = random.choice([0.25, 0.5])
            vel = random.randint(vel_min, vel_max)
            
            all_notes.append({
                "pitch": pitch,
                "start_time": current_time + pos,
                "duration": dur * 0.9,
                "velocity": vel
            })
        
        current_time += beats_per_chord
    
    return all_notes, current_time


def get_available_moods() -> List[str]:
    """Return list of all available mood profiles."""
    return list(MOOD_PROFILES.keys())
