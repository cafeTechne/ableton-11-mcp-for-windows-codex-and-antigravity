"""
Rhythmic Comp Generator - Parametric & Humanized.

Provides genre-specific rhythmic patterns with support for:
- Articulations (ghost, accent, staccato, tenuto)
- Velocity Ranges (human dynamics)
- Groove Engine (Swing, Jitter, Strum)
"""

import logging
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("mcp_server.rhythmic_comp")

@dataclass
class Groove:
    """Parameters for humanizing the rhythm."""
    swing: float = 0.0          # 0.0 to 1.0 (0=straight, 1=heavy triplet)
    humanize_timing: float = 0.0 # 0.0 to 1.0 (random jitter amount approx +/- 20ms at max)
    humanize_velocity: float = 0.0 # 0.0 to 1.0 (additional random velocity flux)
    strum: float = 0.0          # Strum spread in beats (e.g. 0.05)

# Pattern Definition
# Format: List of (beat_offset, duration, vel_min, vel_max, articulation)
# beat_offset: Position within a bar (0-3 for 4/4)
# duration: Note length in beats
# vel_min, vel_max: Velocity range (0.0 - 1.0 multiplier of base)
# articulation: "normal", "ghost", "accent", "staccato", "tenuto"

COMP_PATTERNS = {
    # --- SKA / REGGAE ------------------------------
    "ska_skank": {
        "pattern": [
            (0.5, 0.25, 0.8, 0.9, "staccato"),  # & of 1
            (1.5, 0.25, 0.9, 1.0, "accent"),    # & of 2
            (2.5, 0.25, 0.8, 0.9, "staccato"),  # & of 3
            (3.5, 0.25, 0.9, 1.0, "accent"),    # & of 4
        ],
        "groove": Groove(swing=0.1, humanize_timing=0.05, strum=0.02),
        "description": "Classic Jamaican ska offbeat skank"
    },
    
    "ska_upstrokes": {
        "pattern": [
            # Beat 1
            (0.0, 0.1, 0.3, 0.5, "ghost"),      # 1: Ghost downstroke
            (0.5, 0.15, 0.9, 1.0, "accent"),    # &: Sharp upstroke
            # Beat 2
            (1.0, 0.1, 0.3, 0.45, "ghost"),     # 2
            (1.5, 0.15, 0.95, 1.1, "accent"),   # &: Stronger
            # Beat 3
            (2.0, 0.1, 0.3, 0.5, "ghost"),      # 3
            (2.5, 0.15, 0.9, 1.0, "accent"),    # &
            # Beat 4
            (3.0, 0.1, 0.3, 0.45, "ghost"),     # 4
            (3.5, 0.15, 0.95, 1.1, "accent"),   # &
        ],
        "groove": Groove(swing=0.05, humanize_timing=0.03, strum=0.01),
        "description": "3rd Wave Ska: Ghost downstrokes + sharp upstrokes"
    },

    "reggae_bubble": {
         "pattern": [
            (0.0, 0.15, 0.3, 0.4, "ghost"),  # 1
            (0.5, 0.3, 0.9, 1.0, "staccato"), # & (Main skank)
            (0.75, 0.15, 0.3, 0.4, "ghost"), # a (Double chop)
            (1.0, 0.15, 0.3, 0.4, "ghost"),  # 2
            (1.5, 0.3, 0.9, 1.0, "staccato"), # &
            (1.75, 0.15, 0.3, 0.4, "ghost"), # a
            (2.0, 0.15, 0.3, 0.4, "ghost"),
            (2.5, 0.3, 0.9, 1.0, "staccato"),
            (2.75, 0.15, 0.3, 0.4, "ghost"),
            (3.0, 0.15, 0.3, 0.4, "ghost"),
            (3.5, 0.3, 0.9, 1.0, "staccato"),
            (3.75, 0.15, 0.3, 0.4, "ghost"),
        ],
        "groove": Groove(swing=0.4, humanize_timing=0.05, strum=0.01),
        "description": "Reggae Keyboard Bubble (Organ)"
    },

    "reggae_skank": {
        "pattern": [
            (0.5, 0.35, 0.8, 0.9, "tenuto"),
            (1.5, 0.35, 0.85, 0.95, "tenuto"),
            (2.5, 0.35, 0.8, 0.9, "tenuto"),
            (3.5, 0.35, 0.9, 1.0, "tenuto"),
        ],
        "groove": Groove(swing=0.35, humanize_timing=0.1, strum=0.04),
        "description": "Laid-back reggae offbeat"
    },

    # --- FUNK --------------------------------------
    "funk_stabs": {
        "pattern": [
            (0.0, 0.2, 0.9, 1.1, "accent"),   # 1
            (0.75, 0.2, 0.7, 0.8, "staccato"), # a of 1
            (1.5, 0.2, 0.8, 0.95, "normal"),  # & of 2
            (3.0, 0.2, 0.9, 1.0, "accent"),   # 4
            (3.5, 0.2, 0.7, 0.85, "staccato"),# & of 4
        ],
        "groove": Groove(swing=0.2, humanize_timing=0.05, strum=0.02),
        "description": "Syncopated funk chord stabs"
    },

    "funk_clav": {
        "pattern": [
            (0.0, 0.15, 0.9, 1.0, "staccato"),
            (0.5, 0.15, 0.6, 0.75, "ghost"),
            (1.0, 0.15, 0.8, 0.9, "staccato"),
            (1.75, 0.15, 0.6, 0.7, "ghost"),
            (2.5, 0.15, 0.75, 0.9, "normal"),
            (3.0, 0.15, 0.9, 1.0, "accent"),
            (3.5, 0.15, 0.7, 0.8, "staccato"),
        ],
        "groove": Groove(swing=0.15, humanize_timing=0.03),
        "description": "Clavinet-style funk pattern"
    },

    # --- POP / ROCK / HOUSE ------------------------
    "house_piano": {
        "pattern": [
            (0.0, 0.5, 0.9, 1.0, "normal"),
            (1.0, 0.25, 0.7, 0.8, "staccato"),
            (1.5, 0.5, 0.85, 0.95, "accent"),
            (2.5, 0.25, 0.6, 0.75, "ghost"),
            (3.0, 0.5, 0.8, 0.9, "normal"),
        ],
        "groove": Groove(swing=0.1, humanize_timing=0.04, humanize_velocity=0.1),
        "description": "Classic house piano chords"
    },

    "disco_octaves": {
        "pattern": [
            (0.0, 0.2, 0.9, 1.0, "normal"),
            (0.5, 0.2, 0.8, 0.9, "normal"),
            (1.0, 0.2, 0.9, 1.0, "accent"),
            (1.5, 0.2, 0.8, 0.9, "normal"),
            (2.0, 0.2, 0.9, 1.0, "normal"),
            (2.5, 0.2, 0.8, 0.9, "normal"),
            (3.0, 0.2, 0.9, 1.0, "accent"),
            (3.5, 0.2, 0.85, 0.95, "normal"),
        ],
        "groove": Groove(swing=0.05, humanize_timing=0.02),
        "description": "Driving disco octave pattern"
    },

    "motown": {
        "pattern": [
            (0.0, 0.4, 0.9, 1.0, "staccato"),
            (1.0, 0.3, 0.8, 0.9, "staccato"),
            (2.0, 0.4, 0.9, 1.0, "accent"),
            (3.0, 0.3, 0.75, 0.85, "staccato"),
        ],
        "groove": Groove(swing=0.1, humanize_timing=0.08, strum=0.02),
        "description": "Classic Motown quarter-note feel"
    },
    
    "bossa_nova": {
        "pattern": [
            (0.0, 0.75, 0.8, 0.9, "tenuto"),
            (1.5, 0.5, 0.7, 0.8, "normal"),
            (2.5, 0.5, 0.75, 0.85, "accent"),
            (3.5, 0.4, 0.65, 0.75, "staccato"),
        ],
        "groove": Groove(swing=0.25, humanize_timing=0.06, strum=0.05),
        "description": "Bossa nova comping pattern"
    },

    "quarters": {
        "pattern": [
            (0.0, 0.9, 0.9, 1.0, "normal"),
            (1.0, 0.9, 0.8, 0.9, "normal"),
            (2.0, 0.9, 0.85, 0.95, "normal"),
            (3.0, 0.9, 0.8, 0.9, "normal"),
        ],
        "groove": Groove(humanize_timing=0.02),
        "description": "Simple quarter note comping"
    },
    
    "ballad": {
        "pattern": [
            (0.0, 3.8, 0.6, 0.8, "tenuto"),
        ],
        "groove": Groove(humanize_timing=0.1, strum=0.08, humanize_velocity=0.2), # Slow strum
        "description": "Sustained ballad chords"
    },
    
    # --- UTILITY / NEW ---
    "chug_palm_mute": {
        "pattern": [
             (0.0, 0.2, 0.8, 0.9, "staccato"),
             (0.5, 0.2, 0.8, 0.9, "staccato"),
             (1.0, 0.2, 0.9, 1.0, "accent"),
             (1.5, 0.2, 0.8, 0.9, "staccato"),
             (2.0, 0.2, 0.8, 0.9, "staccato"),
             (2.5, 0.2, 0.8, 0.9, "staccato"),
             (3.0, 0.2, 0.9, 1.0, "accent"),
             (3.5, 0.2, 0.8, 0.9, "staccato"),
        ],
        "groove": Groove(humanize_timing=0.03, humanize_velocity=0.05),
        "description": "Palm muted guitar chug"
    },
    
    "threat_pad": {
        "pattern": [
             (0.0, 3.8, 0.5, 0.7, "tenuto"),
        ],
        "groove": Groove(humanize_velocity=0.3),
        "description": "Ominous sustained pad"
    },

    "finger_picking": {
        "pattern": [
             # Special Arpeggiator Definition
             {"type": "arpeggio", "subdivision": 1.0/3.0, "gate": 0.4, "min_vel": 0.7, "max_vel": 0.9} 
        ],
        "groove": Groove(humanize_timing=0.02, humanize_velocity=0.05),
        "description": "Palm muted arpeggio triplets"
    },
    
    "walking_tritone": {
        "pattern": [
             # Root(0) -> b5(2) -> b3(1) -> b5(2).  (For dim7 chord: R, b3, b5, bb7)
             {"type": "arpeggio", "subdivision": 1.0, "gate": 0.8, "min_vel": 0.9, "max_vel": 1.0, "indices": [0, 2, 1, 2]}
        ],
        "groove": Groove(humanize_timing=0.03, swing=0.1),
        "description": "Walking tritone pattern (Root-b5-b3-b5)"
    }
}


def get_comp_pattern(style: str) -> Dict[str, Any]:
    """Get a comp pattern by name, with fuzzy matching."""
    style_lower = style.lower().replace(" ", "_").replace("-", "_")
    
    if style_lower in COMP_PATTERNS:
        return COMP_PATTERNS[style_lower]
        
    for name, pattern in COMP_PATTERNS.items():
        if style_lower in name or name in style_lower:
            return pattern
            
    logger.warning(f"Unknown comp style '{style}', defaulting to 'quarters'")
    return COMP_PATTERNS["quarters"]


def apply_groove(
    start_time: float, 
    duration: float, 
    velocity: int, 
    pitch: int,
    chord_index: int, 
    groove: Groove
) -> Tuple[float, float, int]:
    """
    Apply global groove settings to a single note.
    
    Args:
        start_time: Beat position
        duration: Length in beats
        velocity: MIDI velocity
        pitch: MIDI pitch (for strumming calculation)
        chord_index: Index of note in the chord (0=lowest)
        groove: Groove parameters
        
    Returns:
        (new_start, new_duration, new_velocity)
    """
    
    new_start = start_time
    new_dur = duration
    new_vel = velocity
    
    # 1. SWING
    # Basic swing logic: Delay even eighth notes (0.5, 1.5, 2.5, 3.5...)
    # We check if (start_time * 2) has a remainder (is it an offbeat?)
    # E.g. 0.5 -> 1.0. 
    # Logic: if start_time % 1.0 >= 0.5, push it.
    
    cycle_pos = start_time % 1.0
    if cycle_pos >= 0.5 and groove.swing > 0:
        # standard swing max is approx 0.16 beats delay (triplet feel is 0.66 vs 0.5)
        # 16th note swing is different, here we assume 8th note swing primarily for comping
        offset = groove.swing * 0.16 # arbitrary scaling
        new_start += offset
        # Shorten previous note? (Not implemented here, strictly note-on modification)
        
    # 2. STRUM
    # Offset based on pitch index. Lower notes first (usually).
    if groove.strum > 0 and chord_index > 0:
        strum_delay = groove.strum * chord_index
        new_start += strum_delay
        # Slightly reduce duration so it doesn't overlap excessively?
        # new_dur -= strum_delay
        
    # 3. HUMANIZATION (Timing Jitter)
    # +/- small amount
    if groove.humanize_timing > 0:
        jitter = (random.random() - 0.5) * groove.humanize_timing
        new_start += jitter
    
    # 4. HUMANIZATION (Velocity)
    if groove.humanize_velocity > 0:
        v_jitter = (random.random() - 0.5) * groove.humanize_velocity * 127
        new_vel = int(max(1, min(127, new_vel + v_jitter)))
        
    return new_start, new_dur, new_vel


def generate_comp_notes(
    chord_notes: List[int],
    pattern: List[tuple], # (offset, dur, min, max, art)
    bar_offset: float,
    base_velocity: int = 100,
    groove: Optional[Groove] = None,
    duration_beats: float = 4.0 # Default to 4/4 bar if unspecified
) -> List[Dict[str, Any]]:
    """
    Generate note events for a single bar of comping.
    Now supports range-based velocity and grooves.
    """
    if groove is None:
        groove = Groove()
        
    notes = []
    
    # Sort chord notes for strumming logic
    chord_notes_sorted = sorted(chord_notes)
    
    for entry in pattern:
        # ARPEGGIATOR LOGIC
        if isinstance(entry, dict) and entry.get("type") == "arpeggio":
            # Generate Arpeggio Sequence for full bar (assume 4 beats)
            # Or pass duration? Default 4.0.
            subdiv = entry.get("subdivision", 0.5)
            gate = entry.get("gate", 0.5)
            min_v = entry.get("min_vel", 0.7)
            max_v = entry.get("max_vel", 0.9)
            indices = entry.get("indices", None) # Optional fixed sequence
            
            t = 0.0
            idx = 0
            while t < duration_beats - 0.01:
                # Select pitch
                if not chord_notes_sorted: break
                
                if indices:
                    # Use fixed indices (looping)
                    note_idx = indices[idx % len(indices)]
                    pitch = chord_notes_sorted[note_idx % len(chord_notes_sorted)]
                else:
                    # Default linear Up
                    pitch = chord_notes_sorted[idx % len(chord_notes_sorted)]
                
                # Jitter
                t_jitter = 0
                v_jitter = 0
                if groove:
                    if groove.humanize_timing: t_jitter = (random.random()-0.5)*groove.humanize_timing
                    if groove.humanize_velocity: v_jitter = (random.random()-0.5)*groove.humanize_velocity*127
                
                final_vel = int(base_velocity * (min_v + random.random()*(max_v-min_v))) + int(v_jitter)
                final_vel = max(1, min(127, final_vel))
                
                notes.append({
                    "pitch": pitch,
                    "start_time": bar_offset + t + t_jitter,
                    "duration": subdiv * gate,
                    "velocity": final_vel,
                    "mute": False
                })
                
                t += subdiv
                idx += 1
            continue

        # Unpack pattern entry (support legacy 3-tuple just in case, or forceful new 5-tuple)
        if hasattr(entry, "__len__") and len(entry) == 5:
            beat_offset, dur, v_min, v_max, articulation = entry
        elif hasattr(entry, "__len__") and len(entry) == 3:
             # Legacy fallback
             beat_offset, dur, v_mod = entry
             v_min, v_max = v_mod, v_mod
             articulation = "normal"
        else:
            continue
            
        # 1. Determine base velocity
        # Interpolate random factor
        r_factor = random.random()
        vel_scale = v_min + (v_max - v_min) * r_factor
        
        raw_velocity = int(base_velocity * vel_scale)
        
        # 2. Articulation Adjustments
        actual_dur = dur
        
        if articulation == "ghost":
            raw_velocity *= 0.6
            actual_dur *= 0.8
        elif articulation == "accent":
            raw_velocity *= 1.15
        elif articulation == "staccato":
             actual_dur *= 0.5
        elif articulation == "tenuto":
             actual_dur *= 1.1
             
        # Clamp velocity
        raw_velocity = max(1, min(127, raw_velocity))
        
        # 3. Per-Pitch generation with Groove
        for idx, pitch in enumerate(chord_notes_sorted):
            
            # Apply groove logic per note
            g_start, g_dur, g_vel = apply_groove(
                start_time=beat_offset, # Local to bar
                duration=actual_dur,
                velocity=raw_velocity,
                pitch=pitch,
                chord_index=idx,
                groove=groove
            )
            
            # Global time
            abs_start = bar_offset + g_start
            
            notes.append({
                "pitch": pitch,
                "start_time": abs_start,
                "duration": g_dur,
                "velocity": int(max(1, min(127, g_vel))), # Final clamp
                "mute": False
            })
            
    return notes


def list_comp_styles() -> List[str]:
    """Return a list of available comp styles."""
    return list(COMP_PATTERNS.keys())
