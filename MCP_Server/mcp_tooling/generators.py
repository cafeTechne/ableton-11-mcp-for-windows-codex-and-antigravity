import math
import logging
import random
from typing import Optional, List, Dict, Any, Union
from .connection import get_ableton_connection
from .connection import get_ableton_connection
from .theory import get_chord_notes, invert_chord, voice_lead_progression, key_to_midi
from .progression_generator import ProgressionGenerator
from .constants import PROGRESSIONS, SCALES
from .chords import (
    prog_maj, prog_min, prog_modal, prog_all_extended,
    parse_progression, get_progressions_by_mood, get_progressions_by_genre,
    CHORD_TYPES, MOODS, GENRES
)
from .util import load_device_by_name
from .ableton_helpers import ensure_track_exists, ensure_clip_slot
from .basslines import generate_bassline_advanced as gen_bass_adv_logic
from .strings import generate_strings_advanced as gen_strings_adv_logic
from .woodwinds import generate_woodwinds_advanced as gen_winds_adv_logic
from .brass import generate_brass_advanced as gen_brass_adv_logic
from .parsing import parse_bar_chart
from .humanization import HumanizeProfile, apply_humanization
from .automation import generate_cc_envelope, apply_cc_automation, CC_MODULATION, CC_EXPRESSION
from .rhythmic_comp import get_comp_pattern, generate_comp_notes, list_comp_styles, COMP_PATTERNS

logger = logging.getLogger("mcp_server.generators")

# Note name to MIDI offset lookup
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def normalize_key_and_scale(key: str, scale: str):
    """
    Robustly normalize key and scale inputs.
    Returns: (key_raw, key_norm, scale_norm)
    """
    key_raw = key or ""
    k = (key or "").strip().upper()
    
    # Take first token (e.g. "C minor" -> "C")
    if k:
        k = k.split()[0]

    # Enharmonic normalization
    # Convert flats 'B' form to sharps for NOTE_NAMES list and handle E#/B# etc.
    enharm = {
        "DB": "C#", "EB": "D#", "GB": "F#", "AB": "G#", "BB": "A#",
        "CB": "B",  "FB": "E",  "E#": "F",  "B#": "C",
    }
    k = enharm.get(k, k)

    # Strip common suffixes: MAJ/MIN, then single trailing M
    for suffix in ("MAJ", "MIN"):
        if k.endswith(suffix) and len(k) > len(suffix):
            k = k[:-len(suffix)]
            break
            
    # Strip trailing 'M' (Note: this just strips the suffix, does not infer minor scale)
    if len(k) > 1 and k.endswith("M"):
        k = k[:-1]

    s = (scale or "").lower().strip()
    if s not in SCALES:
        s = "major"

    # Final check for valid pitch class
    if k not in NOTE_NAMES:
        logger.warning(f"Key input '{key_raw}' (normalized '{k}') not recognized with scale '{s}'. Defaulting to 'C'.")
        k = "C"

    return key_raw, k, s


def key_to_midi(key: str, octave: int = 4) -> int:
    """
    Convert key name to MIDI note number (robust for C, Cm, Cmin, Cmaj, Db, F#).
    Expects normalized keys (e.g. from normalize_key_and_scale), but has defensive fallback.
    """
    if not key:
        return 60

    k = key.strip().upper()

    # If user passes "C MINOR"/"C MAJOR", keep first token
    k = k.split()[0]

    # Normalize flats and enharmonics
    k = (k.replace("DB", "C#")
           .replace("EB", "D#")
           .replace("GB", "F#")
           .replace("AB", "G#")
           .replace("BB", "A#")
           .replace("CB", "B")
           .replace("FB", "E")
           .replace("E#", "F")
           .replace("B#", "C"))

    # Strip common quality suffixes without nuking the pitch name
    for suffix in ("MAJ", "MIN"):
        if k.endswith(suffix):
            k = k[:-len(suffix)]
            break

    # Strip trailing 'M' (minor shorthand like "AM" sometimes) or 'm' already uppercased
    if len(k) > 1 and k.endswith("M"):
        k = k[:-1]

    try:
        return 12 * (octave + 1) + NOTE_NAMES.index(k)
    except ValueError:
        return 60  # Default to C4


def finalize_notes(notes: List[Dict[str, Any]], clip_length: float) -> List[Dict[str, Any]]:
    clip_length = float(clip_length)
    EPS = 1e-6
    out: List[Dict[str, Any]] = []

    if not math.isfinite(clip_length) or clip_length <= 0:
        return out

    for n in notes:
        try:
            p = int(n["pitch"])
            s = float(n["start_time"])
            d = float(n["duration"])
            v = int(n["velocity"])
        except (KeyError, TypeError, ValueError):
            continue

        # Reject NaN/Inf early
        if not (math.isfinite(s) and math.isfinite(d)):
            continue

        # Clamp pitch/velocity
        p = max(0, min(127, p))
        v = max(1, min(127, v))

        # Clamp start time into clip
        s = max(0.0, s)
        if s >= clip_length:
            continue

        # Clamp duration into clip
        d = max(0.0, min(d, clip_length - s))
        if d <= EPS:
            continue

        out.append({"pitch": p, "start_time": s, "duration": d, "velocity": v})


    out.sort(key=lambda n: (n["start_time"], n["pitch"]))
    return out


def generate_chord_progression(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    genre_progression: str = "pop_1",
    instrument_name: Optional[str] = None
) -> str:
    """
    Simple chord progression generator using preset progressions.
    
    This is a simplified wrapper around generate_chord_progression_advanced
    for backwards compatibility and ease of use.
    
    Args:
        track_index: Target track index
        clip_index: Target clip slot
        key: Musical key (e.g., "C", "Dm", "F#")
        scale: Scale type ("major" or "minor")
        genre_progression: Preset name like "pop_1", "jazz_1", etc.
        instrument_name: Optional instrument to load
    """
    return generate_chord_progression_advanced(
        track_index=track_index,
        clip_index=clip_index,
        key=key,
        scale=scale,
        progression=genre_progression,
        mood=None,
        velocity=90,
        beats_per_chord=4.0,
        voice_lead=True,
        humanize=0.0,
        groove="straight"
    )


def generate_chord_progression_advanced(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Union[str, List[str], List[Dict[str, Any]]] = None, # Can be preset name, string, or list
    mood: Optional[str] = None,
    velocity: int = 80,
    duration: float = 4.0, # Total duration in beats if total_bars not set? Or beats_per_chord?
    beats_per_chord: float = 4.0,
    voice_lead: bool = True,
    strum: float = 0.0,
    humanize: float = 0.0,
    groove: str = "straight",
    arpeggiate: bool = False,
    total_bars: Optional[int] = None,
    rhythm_style: Optional[str] = None # NEW: Support for ska, reggae, etc.
) -> str:
    """
    Advanced chord progression generator with voice leading, strumming, and rhythmic styles.
    """
    conn = get_ableton_connection()

    # 1. Parse Progression
    # ... (existing parsing logic, simplified for brevity here as we are inside the function)
    # Note: In real edit, I must be careful not to delete the body.
    # Since replace_file_content replaces the block, I need to see the body first.
    # I'll just change the signature and the dispatch logic.
    
    # ... (Parsing logic is assumed to be handled by caller or existing code outside this block)
    # Wait, I need to see the implementation to insert the rhythm logic. 
    # I will do this in the NEXT tool call after viewing the file.

    """
    Advanced chord generator with voice leading, inversions, and mood support.
    
    Current limitations:
    - `duration` (total duration) is currently ignored in favor of `total_bars` or `beats_per_chord`.
    - `strum` and `arpeggiate` are reserved for future implementation.
    """
    try:
        ableton = get_ableton_connection()
        ensure_track_exists(track_index, prefer="midi", allow_create=True)
        ensure_clip_slot(track_index, clip_index, allow_create=True)
        
        # Normalize Inputs
        mood = mood.lower().strip() if mood else None

        # Validation
        key_raw, key, scale = normalize_key_and_scale(key, scale)

        # Guard timing inputs
        if total_bars is not None and total_bars <= 0:
            total_bars = None

        beats_per_chord = float(beats_per_chord)
        if beats_per_chord < 0.001:
            return f"Error: beats_per_chord too small ({beats_per_chord})"
            
        # Clamp performance inputs
        velocity = max(1, min(127, int(velocity)))
        humanize = max(0.0, min(1.0, float(humanize)))

        # 1. Resolve Progression
        root_midi = key_to_midi(key, 3) # Chords usually octave 3
        
        chord_list = []
        source_metadata = ""
        precalculated_notes = None # If generator gives us notes directly
        custom_durations = None # For bar chart inputs


        # Check if we should use the Algorithmic Generator
        # Trigger if:
        # A) Explicit request (progression="generate" or "algo")
        # B) Scale is a mode (not major/minor) and no explicit preset
        # C) No inputs provided (default to algorithmic instead of static pop_1? Optional, but cool feature)
        
        use_algo = False
        if progression in ["generate", "algo", "random"]: use_algo = True
        elif scale not in ["major", "minor"] and not progression and not mood: use_algo = True
        
        if use_algo:
             # Calculate Length
             length_bars = total_bars if total_bars and total_bars > 0 else 4
             # If total_bars is not set, we assume 4 chords by default for algo
             num_chords = int(length_bars * 4.0 / beats_per_chord)
             if num_chords < 1: num_chords = 4
             
             gen = ProgressionGenerator(key, scale)
             algo_data = gen.generate(length=num_chords, complexity=0.4)
             
             # algo_data is list of {'roman', 'notes', ...}
             # We can use the cached notes directly!
             chord_list = [d['roman'] for d in algo_data]
             precalculated_notes = [d['notes'] for d in algo_data]
             source_metadata = " (Algorithmic)"

        # If mood is provided, pick a random progression for that mood
        elif mood and not progression:
            # We need to access the mood map. 
            # chords.py provides get_progressions_by_mood
            # But wait, get_progressions_by_mood returns a list of progression DICTS.
            progs = get_progressions_by_mood(mood)
            if progs:
                selected = random.choice(progs)
                chord_list = selected['chords']
                source_metadata = f" (Mood: {mood}, Source: {selected.get('source', 'Unknown')})"
            else:
                return f"Error: No progressions found for mood '{mood}'"
        
        elif isinstance(progression, str):
            # Check presets first
            if progression in PROGRESSIONS:
                chord_list = PROGRESSIONS[progression]
            elif "|" in progression:
                # Bar Chart Parser
                parsed = parse_bar_chart(progression, root_midi, scale)
                chord_list = [p["chord"] for p in parsed]
                precalculated_notes = [p["tones"] for p in parsed]
                custom_durations = [p["duration"] for p in parsed]
                source_metadata = " (Custom Bar Chart)"
            elif "=" in progression: # Citations
                chord_list, moods, src = parse_progression(progression) # Updated parsing
                if src: source_metadata = f" (Source: {src})"
            else:
                # Raw string "IV V I"
                chord_list = progression.split()

        elif isinstance(progression, list):
            # List of dicts or strings
            if len(progression) > 0:
                if isinstance(progression[0], dict):
                    chord_list = [item["chord"] for item in progression]
                else:
                    chord_list = progression
        else:
            # Default
            chord_list = PROGRESSIONS["pop_1"]

        if not chord_list:
            return "Error: Could not resolve chord progression."
            
        # 2. Timing Calculation
        # If total_bars is set, distribute chords evenly
        if total_bars and total_bars > 0:
            total_beats = total_bars * 4.0
            beats_per_chord = total_beats / len(chord_list)
        
        if beats_per_chord < 0.001:
            return f"Error: beats_per_chord too small ({beats_per_chord})"
        
        # 3. Note Generation
        notes = []
        current_time = 0.0
        
        current_time = 0.0
        
        # Root note for key (Calculated above)
        # root_midi = key_to_midi(key, 3) 
        
        # Apply voice leading if requested
        # We need actual pitches for voice leading.
        # theory.voice_lead_progression takes (root_midi, scale, chord_names) -> list of lists of pitches
        
        if voice_lead:
            # 1. Generate all chords in root position first
            # Use precalculated notes if available to ensure modal correctness
            root_positioned_notes = []
            if precalculated_notes:
                 root_positioned_notes = precalculated_notes
            else:
                root_midi = key_to_midi(key, 3)
                for chord_name in chord_list:
                    root_positioned_notes.append(get_chord_notes(root_midi, scale, chord_name))
            
            # 2. Apply voice leading logic
            chord_voicings = voice_lead_progression(root_positioned_notes)
            
            for i, tones in enumerate(chord_voicings):
                # Duration logic
                beats_this = custom_durations[i] if custom_durations else beats_per_chord

                # RHYTHMIC STYLE HANDLING
                if rhythm_style:
                    # Get pattern (Support List for mixed styles)
                    if isinstance(rhythm_style, list):
                        style_name = rhythm_style[i] if i < len(rhythm_style) else rhythm_style[-1]
                    else:
                        style_name = rhythm_style
                        
                    pat_data = get_comp_pattern(style_name)
                    pat_groove = pat_data.get("humanize_profile", groove)
                    
                    # Generate pattern notes for this bar
                    comp_notes = generate_comp_notes(
                        chord_notes=tones,
                        pattern=pat_data["pattern"],
                        bar_offset=current_time,
                        base_velocity=velocity,
                        duration_beats=beats_this # Fix overlapping arpeggios
                    )
                    notes.extend(comp_notes)
                    
                    # Apply specific groove if needed (though global humanize happens later)
                    if groove == "straight" and pat_groove != "straight":
                        groove = pat_groove # Update global groove for this clip
                        
                else:
                    # Standard Block Chords
                    for pitch in tones:
                         notes.append({
                            "pitch": pitch,
                            "start_time": current_time,
                            "duration": beats_this,
                            "velocity": velocity
                        })
                current_time += beats_this
                
        else:
            # Standard generation (Root position / close voicing)
            # Standard generation (Root position / close voicing)
            for i, chord_name in enumerate(chord_list):
                if precalculated_notes:
                    chord_tones = precalculated_notes[i]
                else:
                    chord_tones = get_chord_notes(root_midi, scale, chord_name)
                
                # Duration logic for Non-Voice-Led path
                beats_this = custom_durations[i] if custom_durations else beats_per_chord

                if rhythm_style:
                    # Rhythmic Style Handling (Non-Voice Led)
                    if isinstance(rhythm_style, list):
                        style_name = rhythm_style[i] if i < len(rhythm_style) else rhythm_style[-1]
                    else:
                        style_name = rhythm_style
                        
                    pat_data = get_comp_pattern(style_name)
                    comp_notes = generate_comp_notes(
                        chord_notes=chord_tones,
                        pattern=pat_data["pattern"],
                        bar_offset=current_time,
                        base_velocity=velocity,
                        duration_beats=beats_this # Fix overlapping arpeggios
                    )
                    notes.extend(comp_notes)
                else:
                    # Block Chords
                    for pitch in chord_tones:
                        processed_start = current_time
                        processed_vel = velocity
                        
                        # Strumming
                        if strum > 0:
                            # TODO implement strum logic
                            pass 
                        
                        notes.append({
                            "pitch": pitch,
                            "start_time": processed_start,
                            "duration": beats_this,
                            "velocity": processed_vel
                        })
                current_time += beats_this

        # 4. Humanization (Post-process)
        if humanize > 0 or groove != "straight":
             profile = HumanizeProfile.get_preset(groove if groove else "human")
             # Override profile jitter if humanize is high?
             # Actually apply_humanization uses 'amount' to scale the profile.
             # So if humanize=0.5, we get 50% of the profile's jitter/velocity rng.
             apply_humanization(notes, profile, amount=humanize if humanize > 0 else 1.0)

        # 5. Send to Ableton
        clip_length = float(len(chord_list) * beats_per_chord)
        final_notes = finalize_notes(notes, clip_length)

        # Safe clip creation: delete if exists to avoid "Already has clip" error
        try:
            ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})
        except:
            pass
        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": clip_length})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": final_notes})
        
        # Label the clip with the progression
        label = f"{key_raw} {scale}: " + " - ".join(chord_list)
        if rhythm_style: label += f" ({rhythm_style})"
        try:
             ableton.send_command("set_clip_name", {"track_index": track_index, "clip_index": clip_index, "name": label})
        except:
             pass

        return f"Generated {len(chord_list)} chords ({key_raw} {scale}, {len(final_notes)} notes){source_metadata}"

    except Exception as e:
        logger.error(f"Error generating chords: {e}")
        return f"Error: {e}"


def generate_rhythmic_comp(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Union[str, List[str], List[Dict[str, Any]]] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "ska_skank",
    velocity: int = 85,
    octave: int = 4,
    humanize: float = 0.3,
    groove: str = "straight"
) -> str:
    """
    Generate rhythmic comping patterns (keys, guitar, organ, etc).
    
    Unlike sustained chord pads, this creates genre-specific rhythmic patterns
    with short, percussive chord hits.
    
    Args:
        track_index: Target track index
        clip_index: Target clip slot index
        key: Musical key (e.g., "C", "F#", "Bb")
        scale: Scale type ("major", "minor", "dorian", etc.)
        progression: Chord progression (preset name, list, or mood)
        mood: Alternative to progression - select by mood
        beats_per_chord: Duration of each chord in beats
        total_bars: Override total length in bars
        style: Comp style - "ska_skank", "funk_stabs", "house_piano", etc.
        velocity: Base velocity (1-127)
        octave: Base octave for chords
        humanize: Humanization amount (0.0-1.0)
        groove: Groove preset ("straight", "swing", "push", "pull", etc.)
    
    Available styles:
        - ska_skank: Classic Jamaican offbeat
        - reggae_skank: Laid-back reggae feel
        - funk_stabs: Syncopated funk
        - funk_clav: Clavinet-style pattern
        - house_piano: Classic house chords
        - disco_octaves: Driving eighth notes
        - gospel_comp: Soulful sustained
        - motown: Quarter-note feel
        - bossa_nova: Brazilian jazz
        - quarters: Simple quarter notes
        - ballad: Long sustained chords
    
    Returns:
        Status message describing what was generated
    """
    try:
        ableton = get_ableton_connection()
        ensure_track_exists(track_index, prefer="midi", allow_create=True)
        ensure_clip_slot(track_index, clip_index, allow_create=True)
        
        # Normalize inputs
        key_raw, key, scale = normalize_key_and_scale(key, scale)
        velocity = max(1, min(127, int(velocity)))
        humanize = max(0.0, min(1.0, float(humanize)))
        
        # Get the comp pattern
        pattern_data = get_comp_pattern(style)
        pattern = pattern_data["pattern"]
        pattern_groove = pattern_data.get("humanize_profile", "straight")
        
        # Use pattern's groove if user didn't specify
        if groove == "straight" and pattern_groove != "straight":
            groove = pattern_groove
        
        # Resolve chord progression
        chord_list = []
        if progression:
            resolved, _, _ = parse_progression(progression)
            if resolved:
                chord_list = resolved
        
        if not chord_list and mood:
            mood_progs = get_progressions_by_mood(mood)
            if mood_progs:
                prog_key = random.choice(mood_progs)
                resolved = parse_progression(key, scale, prog_key)
                if resolved:
                    chord_list = resolved
        
        if not chord_list:
            # Default to I-V-vi-IV
            chord_list = ["I", "V", "vi", "IV"]
        
        # Calculate clip length
        if total_bars and total_bars > 0:
            num_chords = int(total_bars * 4 / beats_per_chord)
            while len(chord_list) < num_chords:
                chord_list.extend(chord_list)
            chord_list = chord_list[:num_chords]
        
        clip_length = float(len(chord_list) * beats_per_chord)
        
        # Root MIDI note
        root_midi = 60  # C4 default
        if key in NOTE_NAMES:
            root_midi = 12 * octave + NOTE_NAMES.index(key)
        
        # Generate notes
        notes = []
        current_time = 0.0
        
        for chord_name in chord_list:
            chord_tones = get_chord_notes(root_midi, scale, chord_name)
            
            # Generate one bar of comp pattern
            bar_notes = generate_comp_notes(
                chord_notes=chord_tones,
                pattern=pattern,
                bar_offset=current_time,
                base_velocity=velocity
            )
            notes.extend(bar_notes)
            current_time += beats_per_chord
        
        # Apply humanization
        if humanize > 0 or groove != "straight":
            profile = HumanizeProfile.get_preset(groove if groove else "human")
            apply_humanization(notes, profile, amount=humanize if humanize > 0 else 1.0)
        
        # Finalize and send
        final_notes = finalize_notes(notes, clip_length)
        
        # Safe clip creation
        try:
            ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})
        except:
            pass
        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": clip_length})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": final_notes})
        
        # Label clip
        if chord_list:
             label = f"Comp: " + " - ".join(chord_list)
             try:
                 ableton.send_command("set_clip_name", {"track_index": track_index, "clip_index": clip_index, "name": label})
             except: pass
        
        style_desc = pattern_data.get("description", style)
        return f"Generated {style} comp: {len(chord_list)} chords, {len(final_notes)} notes ({key_raw} {scale}). Style: {style_desc}"
        
    except Exception as e:
        logger.error(f"Error generating rhythmic comp: {e}")
        return f"Error: {e}"


def generate_bassline(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    genre_progression: str = "pop_1",
    style: str = "walking",
    instrument_name: Optional[str] = None
) -> str:
    """
    Simple bassline generator using preset progressions.
    
    This is a simplified wrapper around generate_bassline_advanced_wrapper
    for backwards compatibility and ease of use.
    
    Args:
        track_index: Target track index
        clip_index: Target clip slot
        key: Musical key (e.g., "C", "Dm", "F#")
        scale: Scale type ("major" or "minor")
        genre_progression: Preset name like "pop_1", "jazz_1", etc.
        style: Bassline style ("walking", "rock", "funk", "reggae", etc.)
        instrument_name: Optional instrument to load
    """
    return generate_bassline_advanced_wrapper(
        track_index=track_index,
        clip_index=clip_index,
        key=key,
        scale=scale,
        progression=genre_progression,
        mood=None,
        beats_per_chord=4.0,
        style=style,
        velocity=100,
        octave=2,
        humanize=0.0,
        groove="straight",
        instrument_name=instrument_name
    )


def generate_bassline_advanced_wrapper(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Union[str, List[str], List[Dict[str, Any]]] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "walking",

    velocity: int = 100,
    octave: int = 2,
    humanize: float = 0.0,
    groove: str = "straight",
    instrument_name: Optional[str] = None
) -> str:
    """
    Advanced bassline generator using theory-based rules.
    
    style: "walking", "rock", "funk", "reggae", "country", "pulse", "root", "arpeggio"
    """
    try:
        ableton = get_ableton_connection()
        inst_msg = ""
        
        # Normalize Inputs
        mood = mood.lower().strip() if mood else None
        style = style.lower().strip() if style else style
        
        # Optional: Load instrument
        if instrument_name:
            result = load_device_by_name(track_index, instrument_name, "instruments")
            if result.get("loaded"):
                inst_msg = f" Loaded '{result.get('item_name')}'."
        
        # Resolve progression
        chord_list = None
        if mood:
            mood_progs = get_progressions_by_mood(mood)
            if mood_progs:
                selected = random.choice(mood_progs)
                chord_list = selected['chords']
            else:
                return f"Error: No progressions found for mood '{mood}'"
        elif isinstance(progression, str):
            if progression in PROGRESSIONS:
                chord_list = PROGRESSIONS[progression]
            elif "|" in progression:
                # Bar Chart Parser
                # We need key_root for parsing here
                root_midi = key_to_midi(key, octave)
                chord_list = parse_bar_chart(progression, root_midi, scale)
                # chord_list is now List[Dict]
            elif "=" in progression:
                chord_list, _, _ = parse_progression(progression)
            else:
                chord_list = progression.split()
        elif isinstance(progression, list):
             if len(progression) > 0:
                if isinstance(progression[0], dict):
                    chord_list = [item["chord"] for item in progression]
                else:
                    chord_list = progression
        else:
             chord_list = PROGRESSIONS["pop_1"]

        if not chord_list: return "Error: Could not resolve chords"

        # Resolve Style (Smart Detection)
        final_style = style
        if style == "follow" and (mood or progression):
             # Infer from mood
             context_str = (mood or str(progression)).lower()
             
             if any(x in context_str for x in ["jazz", "swing", "bebop"]):
                 final_style = "jazz"
             elif any(x in context_str for x in ["rock", "metal"]):
                 final_style = "rock"
             elif any(x in context_str for x in ["funk", "groove"]):
                 final_style = "funk"
             elif any(x in context_str for x in ["reggae", "dub"]):
                 final_style = "reggae"
             elif any(x in context_str for x in ["country", "folk"]):
                 final_style = "country"
        
        if final_style == "follow": final_style = "root" 

        # Validation after style inference (or before? Style logic uses mood/prog)
        key_raw, key, scale = normalize_key_and_scale(key, scale)

        # Generate (octave 2 usually good for bass)
        notes, clip_length = gen_bass_adv_logic(
            chords=chord_list,
            key=key,
            scale=scale,
            beats_per_chord=beats_per_chord,
            total_bars=total_bars,
            style=final_style,
            velocity=velocity,
            octave=octave
        )
        
        # Send to Ableton
        clip_length = float(clip_length)
        # Send to Ableton
        clip_length = float(clip_length)
        if humanize > 0 or groove != "straight":
             profile = HumanizeProfile.get_preset(groove if groove else "human")
             apply_humanization(notes, profile, amount=humanize if humanize > 0 else 1.0)
        final_notes = finalize_notes(notes, clip_length)
        
        # Safe clip creation
        try:
            ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})
        except:
            pass
        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": clip_length})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": final_notes})
        
        # Label clip
        if chord_list:
             label = f"Bass: " + " - ".join([str(c) for c in chord_list]) # chord_list might be dicts? no, handled above
             try:
                 ableton.send_command("set_clip_name", {"track_index": track_index, "clip_index": clip_index, "name": label})
             except: pass
        
        prog_name = mood if mood else (progression if isinstance(progression, str) else "custom")
        return f"Generated {final_style} bassline for {prog_name} ({len(chord_list)} chords, {len(final_notes)} notes) in {key_raw} {scale}.{inst_msg}"

    except Exception as e:
        logger.error(f"Error generating advanced bassline: {e}")
        return f"Error: {e}"


def generate_strings_advanced_wrapper(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Union[str, List[str], List[Dict[str, Any]]] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "pop",
    velocity: int = 90,
    octave: int = 4,
    instrument_name: Optional[str] = None,
    mode: str = "deterministic",
    humanize: float = 0.0,
    groove: str = "straight",
    expression: bool = False
) -> str:
    """
    Advanced strings generator using music theory to follow chords.
    
    style: "pop", "rock", "disco", "jazz", "reggae"
    """
    try:
        ableton = get_ableton_connection()
        inst_msg = ""
        
        if instrument_name:
            result = load_device_by_name(track_index, instrument_name, "instruments")
            if result.get("loaded"):
                inst_msg = f" Loaded '{result.get('item_name')}'."
        
        # Validation
        mode = mode.lower().strip()
        if mode not in ["deterministic", "probability"]: mode = "deterministic"
        
        # Robust Key Normalization
        key_raw, key, scale = normalize_key_and_scale(key, scale)
        
        # Resolve progression
        chord_list = None
        if mood:
            mood_progs = get_progressions_by_mood(mood)
            if mood_progs:
                selected = random.choice(mood_progs)
                chord_list = selected['chords']
            else:
                return f"Error: No progressions found for mood '{mood}'"
        elif isinstance(progression, str):
            if progression in PROGRESSIONS:
                chord_list = PROGRESSIONS[progression]
            elif "=" in progression:
                chord_list, _, _ = parse_progression(progression)
            else:
                chord_list = progression.split()
        elif isinstance(progression, list):
             if len(progression) > 0:
                if isinstance(progression[0], dict):
                    chord_list = [item["chord"] for item in progression]
                else:
                    chord_list = progression
        else:
             chord_list = PROGRESSIONS["pop_1"]

        if not chord_list: return "Error: Could not resolve chords"

        # Smart Style Detection
        final_style = style
        if style == "pop" and (mood or progression):
             context_str = (mood or str(progression)).lower()
             if any(x in context_str for x in ["jazz", "swing", "bebop"]):
                 final_style = "jazz"
             elif any(x in context_str for x in ["rock", "metal"]):
                 final_style = "rock"
             elif any(x in context_str for x in ["disco", "funk"]):
                 final_style = "disco"
             elif any(x in context_str for x in ["reggae", "dub"]):
                 final_style = "reggae"

        # Generate
        notes, clip_length = gen_strings_adv_logic(
            chords=chord_list,
            key=key,
            scale=scale,
            beats_per_chord=beats_per_chord,
            total_bars=total_bars,
            style=final_style,
            velocity=velocity,
            octave=octave,
            mode=mode
        )
        
        # Send to Ableton
        clip_length = float(clip_length)
        # Send to Ableton
        clip_length = float(clip_length)
        if humanize > 0 or groove != "straight":
             profile = HumanizeProfile.get_preset(groove if groove else "human")
             apply_humanization(notes, profile, amount=humanize if humanize > 0 else 1.0)
        final_notes = finalize_notes(notes, clip_length)

        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": clip_length})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": final_notes})

        # Expression CC Envelope
        cc_msg = ""
        if expression:
            envelope = generate_cc_envelope(clip_length, curve_type="swell", start_value=20, end_value=110)
            result = apply_cc_automation(track_index, clip_index, CC_EXPRESSION, envelope)
            cc_msg = f" {result}"

        prog_name = mood if mood else (progression if isinstance(progression, str) else "custom")
        return f"Generated {final_style} strings for {prog_name} ({len(chord_list)} chords, {len(final_notes)} notes) in {key_raw} {scale}.{inst_msg}{cc_msg}"

    except Exception as e:
        logger.error(f"Error generating advanced strings: {e}")
        return f"Error: {e}"


def generate_woodwinds_advanced_wrapper(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Union[str, List[str], List[Dict[str, Any]]] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "pop",
    velocity: int = 90,
    octave: int = 4,
    instrument_name: Optional[str] = None,
    mode: str = "deterministic",
    humanize: float = 0.0,
    groove: str = "straight",
    expression: bool = False
) -> str:
    """
    Advanced woodwinds generator using role-based orchestration.
    
    style: "pop", "classical", "jazz", "rock", "reggae"
    """
    try:
        ableton = get_ableton_connection()
        inst_msg = ""
        
        if instrument_name:
            result = load_device_by_name(track_index, instrument_name, "instruments")
            if result.get("loaded"):
                inst_msg = f" Loaded '{result.get('item_name')}'."
        
        # Validation
        mode = mode.lower().strip()
        if mode not in ["deterministic", "probability"]: mode = "deterministic"
        
        # Robust Key Normalization
        key_raw, key, scale = normalize_key_and_scale(key, scale)
        
        # Resolve progression
        chord_list = None
        if mood:
            mood_progs = get_progressions_by_mood(mood)
            if mood_progs:
                selected = random.choice(mood_progs)
                chord_list = selected['chords']
            else:
                return f"Error: No progressions found for mood '{mood}'"
        elif isinstance(progression, str):
            if progression in PROGRESSIONS:
                chord_list = PROGRESSIONS[progression]
            elif "=" in progression:
                chord_list, _, _ = parse_progression(progression)
            else:
                chord_list = progression.split()
        elif isinstance(progression, list):
             if len(progression) > 0:
                if isinstance(progression[0], dict):
                    chord_list = [item["chord"] for item in progression]
                else:
                    chord_list = progression
        else:
             chord_list = PROGRESSIONS["pop_1"]

        if not chord_list: return "Error: Could not resolve chords"

        # Smart Style Detection
        final_style = style
        if style == "pop" and (mood or progression):
             context_str = (mood or str(progression)).lower()
             if any(x in context_str for x in ["classical", "orchestral", "symphonic"]):
                 final_style = "classical"
             elif any(x in context_str for x in ["jazz", "swing", "bebop"]):
                 final_style = "jazz"
             elif any(x in context_str for x in ["rock", "metal"]):
                 final_style = "rock"
             elif any(x in context_str for x in ["reggae", "dub", "ska"]):
                 final_style = "reggae"
             elif any(x in context_str for x in ["edm", "trance", "house"]):
                 final_style = "edm"

        # Generate (octave 4 usually fine for winds)
        notes, clip_length = gen_winds_adv_logic(
            chords=chord_list,
            key=key,
            scale=scale,
            beats_per_chord=beats_per_chord,
            total_bars=total_bars,
            style=final_style,
            velocity=velocity,
            octave=octave,
            mode=mode
        )
        
        # Send to Ableton
        clip_length = float(clip_length)
        # Send to Ableton
        clip_length = float(clip_length)
        if humanize > 0 or groove != "straight":
             profile = HumanizeProfile.get_preset(groove if groove else "human")
             apply_humanization(notes, profile, amount=humanize if humanize > 0 else 1.0)
        final_notes = finalize_notes(notes, clip_length)

        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": clip_length})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": final_notes})

        cc_msg = ""
        if expression:
            envelope = generate_cc_envelope(clip_length, curve_type="attack_release", start_value=30, end_value=120)
            result = apply_cc_automation(track_index, clip_index, CC_EXPRESSION, envelope)
            cc_msg = f" {result}"

        prog_name = mood if mood else (progression if isinstance(progression, str) else "custom")
        return f"Generated {final_style} woodwinds for {prog_name} ({len(final_notes)} notes).{inst_msg}{cc_msg}"

    except Exception as e:
        logger.error(f"Error generating woodwinds: {e}")
        return f"Error: {e}"


def generate_brass_advanced_wrapper(
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Union[str, List[str], List[Dict[str, Any]]] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "pop",
    velocity: int = 100,
    octave: int = 3,
    instrument_name: Optional[str] = None,
    mode: str = "deterministic",
    humanize: float = 0.0,
    groove: str = "straight",
    expression: bool = False
) -> str:
    """
    Advanced brass generator using impact-first logic and genre profiles.
    
    style: "pop", "rock", "metal", "jazz", "ska", "reggae", "gospel", "edm", "classical"
    """
    try:
        ableton = get_ableton_connection()
        inst_msg = ""
        
        if instrument_name:
            # "brass" category? Or instruments?
            # load_device_by_name usually searches.
            result = load_device_by_name(track_index, instrument_name, "instruments")
            if result.get("loaded"):
                inst_msg = f" Loaded '{result.get('item_name')}'."
        
        # Validation
        mode = mode.lower().strip()
        if mode not in ["deterministic", "probability"]: mode = "deterministic"
        
        # Robust Key Normalization
        key_raw, key, scale = normalize_key_and_scale(key, scale)
        
        # Resolve progression
        chord_list = None
        if mood:
            mood_progs = get_progressions_by_mood(mood)
            if mood_progs:
                selected = random.choice(mood_progs)
                chord_list = selected['chords']
            else:
                return f"Error: No progressions found for mood '{mood}'"
        elif isinstance(progression, str):
            if progression in PROGRESSIONS:
                chord_list = PROGRESSIONS[progression]
            elif "=" in progression:
                chord_list, _, _ = parse_progression(progression)
            else:
                chord_list = progression.split()
        elif isinstance(progression, list):
             if len(progression) > 0:
                if isinstance(progression[0], dict):
                    chord_list = [item["chord"] for item in progression]
                else:
                    chord_list = progression
        else:
             chord_list = PROGRESSIONS["pop_1"]

        if not chord_list: return "Error: Could not resolve chords"

        # Smart Style Detection
        final_style = style
        if style == "pop" and (mood or progression):
             context_str = (mood or str(progression)).lower()
             if any(x in context_str for x in ["ska", "reggae"]):
                 final_style = "ska"
             elif any(x in context_str for x in ["rock", "metal", "punk"]):
                 final_style = "rock"
             elif any(x in context_str for x in ["jazz", "swing", "bebop"]):
                 final_style = "jazz"
             elif any(x in context_str for x in ["gospel", "soul", "church"]):
                 final_style = "gospel"
             elif any(x in context_str for x in ["edm", "techno", "trance", "house"]):
                 final_style = "edm"
             elif any(x in context_str for x in ["classical", "orchestral"]):
                 final_style = "classical"

        # Generate (octave 3 usually good for brass sections)
        notes, clip_length = gen_brass_adv_logic(
            chords=chord_list,
            key=key,
            scale=scale,
            beats_per_chord=beats_per_chord,
            total_bars=total_bars,
            style=final_style,
            velocity=velocity,
            octave=octave,
            mode=mode
        )
        
        # Send to Ableton
        clip_length = float(clip_length)
        # Send to Ableton
        clip_length = float(clip_length)
        if humanize > 0 or groove != "straight":
             profile = HumanizeProfile.get_preset(groove if groove else "human")
             apply_humanization(notes, profile, amount=humanize if humanize > 0 else 1.0)
        final_notes = finalize_notes(notes, clip_length)

        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": clip_length})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": final_notes})

        cc_msg = ""
        if expression:
            envelope = generate_cc_envelope(clip_length, curve_type="fade_in", start_value=40, end_value=127)
            result = apply_cc_automation(track_index, clip_index, CC_MODULATION, envelope)
            cc_msg = f" {result}"

        prog_name = mood if mood else (progression if isinstance(progression, str) else "custom")
        return f"Generated {final_style} brass for {prog_name} ({len(final_notes)} notes).{inst_msg}{cc_msg}"

    except Exception as e:
        logger.error(f"Error generating brass: {e}")
        return f"Error: {e}"


def add_basic_drum_pattern(
    track_index: int, 
    clip_index: int, 
    length_beats: float = 4.0, 
    velocity: int = 100, 
    style: str = "four_on_floor", 
    humanize: float = 0.0, 
    groove: str = "straight",
    ghost_notes: bool = True,
    ghost_density: float = 0.5
):
    """
    Add a basic drum pattern with optional ghost notes.
    
    Args:
        ghost_notes: Add ghost notes (quiet snare/hat hits) for more realistic feel
        ghost_density: How many ghost notes to add (0.0-1.0, where 1.0 is maximum)
    """
    try:
        ableton = get_ableton_connection()
        
        length_beats = float(length_beats)
        if length_beats <= 0: return "Error: length_beats must be > 0"
        style = (style or "").strip().lower()
        ghost_density = max(0.0, min(1.0, float(ghost_density)))

        notes = []
        KICK = 36; SNARE = 38; HAT_CLOSED = 42; HAT_OPEN = 46
        
        # Ghost note velocity (much quieter)
        ghost_vel = max(30, int(velocity * 0.35))
        
        if style == "four_on_floor":
            for i in range(int(length_beats)):
                # Main kick on every beat
                notes.append({"pitch": KICK, "start_time": float(i), "duration": 0.1, "velocity": 120})
                # Offbeat hi-hat
                notes.append({"pitch": HAT_CLOSED, "start_time": float(i)+0.5, "duration": 0.1, "velocity": 90})
                
            # Snare on 2 and 4
            for i in range(1, int(length_beats), 2):
                notes.append({"pitch": SNARE, "start_time": float(i), "duration": 0.1, "velocity": 110})
            
            # Ghost notes
            if ghost_notes and ghost_density > 0:
                # Add ghost snares before main snare hits
                for i in range(1, int(length_beats), 2):
                    # Ghost before the snare (on the "e" - 16th note before)
                    if ghost_density >= 0.3:
                        notes.append({"pitch": SNARE, "start_time": float(i) - 0.25, "duration": 0.08, "velocity": ghost_vel})
                    # Ghost after the snare (on the "a")
                    if ghost_density >= 0.6:
                        notes.append({"pitch": SNARE, "start_time": float(i) + 0.25, "duration": 0.08, "velocity": ghost_vel + 5})
                    # Additional ghost on the "a" before the kick
                    if ghost_density >= 0.8:
                        notes.append({"pitch": SNARE, "start_time": float(i) + 0.75, "duration": 0.08, "velocity": ghost_vel - 5})
                        
        elif style == "rock_basic":
            for i in range(int(length_beats)):
                if i % 2 == 0: 
                    notes.append({"pitch": KICK, "start_time": float(i), "duration": 0.1, "velocity": 120})
                else: 
                    notes.append({"pitch": SNARE, "start_time": float(i), "duration": 0.1, "velocity": 115})
                notes.append({"pitch": HAT_CLOSED, "start_time": float(i), "duration": 0.1, "velocity": 90})
                notes.append({"pitch": HAT_CLOSED, "start_time": float(i)+0.5, "duration": 0.1, "velocity": 85})
            
            # Rock ghost notes
            if ghost_notes and ghost_density > 0:
                for i in range(0, int(length_beats), 2):  # Between kick and snare
                    if ghost_density >= 0.4:
                        notes.append({"pitch": SNARE, "start_time": float(i) + 0.5, "duration": 0.08, "velocity": ghost_vel})
                    if ghost_density >= 0.7:
                        notes.append({"pitch": SNARE, "start_time": float(i) + 0.75, "duration": 0.08, "velocity": ghost_vel - 5})
                        
        elif style == "funk":
            # Syncopated funk pattern
            for i in range(int(length_beats)):
                if i % 2 == 0:
                    notes.append({"pitch": KICK, "start_time": float(i), "duration": 0.1, "velocity": 115})
                    if i % 4 != 0:  # Add kick on & of 2 in alternating bars
                        notes.append({"pitch": KICK, "start_time": float(i) + 0.5, "duration": 0.1, "velocity": 100})
                else:
                    notes.append({"pitch": SNARE, "start_time": float(i), "duration": 0.1, "velocity": 110})
                # Constant 16th hats
                for j in [0, 0.25, 0.5, 0.75]:
                    hat_vel = 80 if j in [0, 0.5] else 60
                    notes.append({"pitch": HAT_CLOSED, "start_time": float(i) + j, "duration": 0.05, "velocity": hat_vel})
            
            # Funk is ALL about ghost notes!
            if ghost_notes:
                for i in range(int(length_beats)):
                    # Ghost before snare
                    if i % 2 == 1:
                        notes.append({"pitch": SNARE, "start_time": float(i) - 0.25, "duration": 0.08, "velocity": ghost_vel})
                        notes.append({"pitch": SNARE, "start_time": float(i) + 0.25, "duration": 0.08, "velocity": ghost_vel + 5})
                    # Ghost on kicks
                    if i % 2 == 0 and ghost_density >= 0.5:
                        notes.append({"pitch": SNARE, "start_time": float(i) + 0.25, "duration": 0.08, "velocity": ghost_vel - 5})

        if humanize > 0 or groove != "straight":
             profile = HumanizeProfile.get_preset(groove if groove else "human")
             apply_humanization(notes, profile, amount=humanize if humanize > 0 else 1.0)

        final_notes = finalize_notes(notes, length_beats)

        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": length_beats})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": final_notes})
        
        ghost_msg = " (with ghost notes)" if ghost_notes else ""
        return f"Added drums ({style}){ghost_msg} ({len(final_notes)} notes)"
    except Exception as e:
        return f"Error adding drums: {e}"


def pattern_generator(track_index: int, clip_slot_index: int, pattern_type: str = "four_on_floor", bars: int = 1, root_note: int = 60, velocity: int = 100, swing: float = 0.0, humanize: float = 0.0, groove: str = "straight", fill: bool = False) -> str:
    try:
        ableton = get_ableton_connection()
        ensure_track_exists(track_index, prefer="midi", allow_create=True)
        ensure_clip_slot(track_index, clip_slot_index, allow_create=True)
        
        # Input Clamping
        velocity = max(1, min(127, int(velocity)))
        root_note = max(0, min(127, int(root_note)))
        swing = max(0.0, min(1.0, float(swing)))
        humanize = max(0.0, min(1.0, float(humanize)))

        if bars <= 0: return "Error: bars must be >= 1"

        beats = float(bars) * 4.0
        ptype = (pattern_type or "").strip().lower()
        base_notes = [] 
        if "four" in ptype:
            for i in range(int(beats)):
                 base_notes.append({"pitch": root_note, "start": float(i), "dur": 0.25, "vel": velocity})
        elif "trap" in ptype:
            for b in range(int(beats / 4)):
                base_start = b * 4.0
                base_notes.append({"pitch": root_note, "start": base_start + 0.0, "dur": 0.25, "vel": velocity})
                base_notes.append({"pitch": root_note, "start": base_start + 2.0, "dur": 0.25, "vel": max(1, min(127, int(velocity * 1.1)))})
                base_notes.append({"pitch": root_note, "start": base_start + 2.75, "dur": 0.25, "vel": velocity})
        elif "dnb" in ptype:
             for b in range(int(beats / 4)):
                base_start = b * 4.0
                base_notes.append({"pitch": root_note, "start": base_start + 0.0, "dur": 0.25, "vel": velocity})
                base_notes.append({"pitch": root_note, "start": base_start + 2.5, "dur": 0.25, "vel": velocity})
        else:
             for i in range(int(beats)):
                 base_notes.append({"pitch": root_note, "start": float(i), "dur": 0.25, "vel": velocity})

        if fill and bars >= 1:
            last_bar_start = (bars - 1) * 4.0
            fill_notes = []
            for n in base_notes:
                if n["start"] >= last_bar_start:
                    fill_notes.append({"pitch": n["pitch"], "start": n["start"] + 0.25, "dur": 0.125, "vel": max(1, min(127, int(n["vel"] * 0.8)))})
            base_notes.extend(fill_notes)

        # Convert to dict format
        processed_notes = []
        for n in base_notes:
             processed_notes.append({"pitch": n["pitch"], "start_time": n["start"], "duration": n["dur"], "velocity": n["vel"]})

        # Humanization
        # Map legacy 'swing' arg to groove if needed
        if swing > 0 and groove == "straight":
            groove = "swing"
        
        if humanize > 0 or groove != "straight" or swing > 0:
             profile = HumanizeProfile.get_preset(groove if groove else "human")
             if swing > 0:
                 profile.groove_amount = swing
             apply_humanization(processed_notes, profile, amount=humanize if humanize > 0 else 1.0)
             
        final_notes = finalize_notes(processed_notes, beats)
            
        # Safe clip creation
        try:
            ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_slot_index})
        except:
            pass
        ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_slot_index, "length": beats})
        ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_slot_index, "notes": final_notes})
        return f"Generated pattern {ptype} ({len(final_notes)} notes)"
    except Exception as e:
        return f"Error: {e}"