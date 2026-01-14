
# Note name to MIDI offset lookup
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Musical Scales
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    # Aliases
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "natural_minor": [0, 2, 3, 5, 7, 8, 10],
    "ionian": [0, 2, 4, 5, 7, 9, 11]
}

# Common Progressions
PROGRESSIONS = {
    # Pop/Rock Standards
    "pop_1": ["I", "V", "vi", "IV"],
    "pop_2": ["vi", "IV", "I", "V"],
    "pop_3": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],  # Pachelbel-ish
    "pop_4": ["I", "I", "IV", "V"],
    "emotional": ["vi", "IV", "I", "V"],
    "fifties_rock": ["I", "IV", "V", "IV"],
    "fifties_doo_wop": ["I", "vi", "IV", "V"],
    
    # Jazz
    "jazz_251": ["ii", "V", "I"],
    "jazz_minor": ["i7", "ii7dim", "V7", "i7"],
    "blues": ["I7", "IV7", "I7", "V7", "IV7", "I7"],
    
    # Electronic
    "trap_dark": ["i", "VI", "i", "VI"],
    "house_deep": ["i7", "v7", "i7", "VI7"],
    
    # =========================================================================
    # CHIPTUNE PROGRESSIONS
    # Drawn from classic NES, Game Boy, SNES, and modern chip-rock
    # =========================================================================
    
    # Adventure/Heroic (Major key, uplifting)
    "chip_adventure": ["I", "IV", "V", "I"],           # Zelda overworld feel
    "chip_heroic": ["I", "V", "vi", "IV"],             # Mega Man stage select
    "chip_triumph": ["I", "IV", "I", "V"],             # Level complete
    "chip_fanfare": ["I", "IV", "V", "V", "I"],        # Victory jingle
    
    # Action/Driving (Energetic, forward motion)
    "chip_action": ["I", "bVII", "IV", "I"],           # Mixolydian power
    "chip_chase": ["i", "bVII", "bVI", "bVII"],        # Intense pursuit
    "chip_boss_intro": ["i", "i", "bVI", "bVII"],      # Boss appears
    "chip_stage": ["I", "V", "IV", "V"],               # Classic stage loop
    
    # Dark/Gothic (Minor key, Castlevania style)
    "chip_gothic": ["i", "bVI", "bVII", "i"],          # Castlevania classic
    "chip_dungeon": ["i", "iv", "bVI", "V"],           # Underground
    "chip_ominous": ["i", "bII", "i", "bVII"],         # Phrygian darkness
    "chip_castle": ["i", "bVII", "bVI", "V"],          # Haunted castle
    "chip_vampire": ["i", "V", "bVI", "bVII"],         # Bloody Tears feel
    
    # Emotional/Melancholy
    "chip_sad": ["vi", "IV", "I", "V"],                # Emotional cutscene
    "chip_nostalgia": ["I", "iii", "vi", "IV"],        # Bittersweet
    "chip_farewell": ["I", "V", "vi", "iii", "IV"],    # Ending theme
    "chip_memory": ["vi", "V", "IV", "V"],             # Flashback
    
    # Playful/Bouncy (Mario style)
    "chip_bouncy": ["I", "I", "IV", "IV", "V", "V", "I", "I"],  # SMB world 1-1
    "chip_playful": ["I", "vi", "ii", "V"],            # Lighthearted
    "chip_underground": ["i", "i", "iv", "iv"],        # SMB underground
    "chip_water": ["I", "iii", "IV", "ii"],            # Water level
    
    # Power/Punk (Anamanaguchi style)
    "chip_power": ["I", "V", "I", "V"],                # Power chord punk
    "chip_anthem": ["I", "IV", "vi", "V"],             # Anthem build
    "chip_drive": ["I", "bVII", "I", "bVII"],          # Driving punk
    "chip_rage": ["i", "i", "bVII", "bVII"],           # Aggressive
    
    # Dance/Trance (Chipzel style)
    "chip_dance": ["i", "bVII", "bVI", "bVII"],        # Dance minor
    "chip_trance": ["i", "i", "bVI", "bVII"],          # Hypnotic loop
    "chip_rave": ["i", "bVI", "bVII", "i"],            # Rave energy
    
    # Space/Sci-Fi (Metroid style)
    "chip_space": ["i", "bII", "bVII", "i"],           # Alien atmosphere
    "chip_tech": ["i", "v", "bVI", "bVII"],            # High-tech lab
    "chip_void": ["i", "i", "bVI", "bVI"],             # Empty space
    
    # Boss Battles
    "chip_boss_major": ["I", "bVII", "bVI", "bVII"],   # Epic boss (major)
    "chip_boss_minor": ["i", "bVI", "bVII", "V"],      # Dark boss (minor)
    "chip_final_boss": ["i", "bII", "V", "i"],         # Final confrontation
    
    # Menu/Title
    "chip_menu": ["I", "IV", "I", "V"],                # Simple menu loop
    "chip_title": ["I", "V", "IV", "V", "I"],          # Title screen
    
    # Credits/Ending
    "chip_credits": ["I", "V", "vi", "IV", "I", "V", "I"],  # Roll credits
    "chip_ending": ["I", "IV", "vi", "V", "I"],        # Happy ending
}

# Song Templates (Blueprints)
GENRE_TEMPLATES = {
    "pop": {
        "structure": ["Intro", "Verse 1", "Chorus", "Verse 2", "Chorus", "Bridge", "Chorus", "Outro"],
        "progression_map": {
            "Intro": "pop_1", "Verse 1": "pop_1", "Chorus": "pop_4", 
            "Verse 2": "pop_1", "Bridge": "pop_3", "Outro": "pop_1"
        },
        "tracks": [
            {"name": "Drums", "type": "drums", "instrument": "808 Core Kit"},
            {"name": "Chords", "type": "chords", "instrument": "Grand Piano"},
            {"name": "Bass", "type": "bass", "instrument": "Bass-Hip-Hop Sub"}
        ]
    },
    "house": {
        "structure": ["Intro", "Build", "Drop", "Break", "Drop", "Outro"],
        "progression_map": {
            "Intro": "emotional", "Build": "emotional", "Drop": "pop_4", 
            "Break": "emotional", "Outro": "emotional"
        },
        "tracks": [
            {"name": "Drums", "type": "drums", "instrument": "909 Core Kit"},
            {"name": "Chords", "type": "chords", "instrument": "Pad-Analog"},
            {"name": "Bass", "type": "bass", "instrument": "Bass-Analog"}
        ]
    },
    "jazz": {
        "structure": ["Head", "Solo 1", "Solo 2", "Head"],
        "progression_map": {
            "Head": "jazz_minor", "Solo 1": "jazz_minor", "Solo 2": "jazz_minor"
        },
        "tracks": [
            {"name": "Drums", "type": "drums", "instrument": "Jazz Kit"},
            {"name": "Piano", "type": "chords", "instrument": "Grand Piano"},
            {"name": "Bass", "type": "bass", "instrument": "Upright Bass"}
        ]
    },
    "chiptune": {
        "structure": ["Intro", "Theme A", "Theme B", "Theme A", "Bridge", "Theme A", "Outro"],
        "progression_map": {
            "Intro": "chip_fanfare", 
            "Theme A": "chip_heroic", 
            "Theme B": "chip_action",
            "Bridge": "chip_anthem", 
            "Outro": "chip_triumph"
        },
        "tracks": [
            {"name": "Lead", "type": "melody", "instrument": "Operator"},
            {"name": "Arp", "type": "chords", "instrument": "Operator"},
            {"name": "Bass", "type": "bass", "instrument": "Operator"},
            {"name": "Drums", "type": "drums", "instrument": "606 Core Kit"}
        ]
    },
    "chiptune_dark": {
        "structure": ["Intro", "Verse", "Chorus", "Verse", "Bridge", "Chorus", "Outro"],
        "progression_map": {
            "Intro": "chip_ominous",
            "Verse": "chip_gothic",
            "Chorus": "chip_boss_minor",
            "Bridge": "chip_vampire",
            "Outro": "chip_castle"
        },
        "tracks": [
            {"name": "Lead", "type": "melody", "instrument": "Operator"},
            {"name": "Arp", "type": "chords", "instrument": "Operator"},
            {"name": "Bass", "type": "bass", "instrument": "Operator"},
            {"name": "Drums", "type": "drums", "instrument": "606 Core Kit"}
        ]
    },
    "chiptune_punk": {
        "structure": ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Bridge", "Chorus", "Outro"],
        "progression_map": {
            "Intro": "chip_drive",
            "Verse": "chip_power",
            "Chorus": "chip_anthem",
            "Bridge": "chip_rage",
            "Outro": "chip_drive"
        },
        "tracks": [
            {"name": "Lead", "type": "melody", "instrument": "Operator"},
            {"name": "Power Chords", "type": "chords", "instrument": "Operator"},
            {"name": "Bass", "type": "bass", "instrument": "Operator"},
            {"name": "Drums", "type": "drums", "instrument": "606 Core Kit"}
        ]
    }
}

