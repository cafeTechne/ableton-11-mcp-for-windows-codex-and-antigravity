---
description: How to generate mood-driven melodies from chord progressions
---

# Apply Melody with Motifs

Generates mood-driven melodies from existing chord progressions. Each run produces a non-deterministic variation, allowing rapid A/B comparison of different moods.

## Prerequisites

- A chord track with clips containing MIDI chords
- By default, uses Track 2 (index 2) as the chord source
- Default key: F# Mixolydian

## Usage

### Basic Usage

```bash
cd MCP_Server
python -m mcp_tooling.apply_melody_with_motifs allegro
```

### Available Moods (21 Italian Terms)

| Category | Moods |
|:---------|:------|
| ☀️ Bright/Energetic | `allegro`, `vivace`, `giocoso`, `brillante`, `leggiero`, `con_brio` |
| ⚔️ Boss/Dark | `agitato`, `furioso`, `tenebroso`, `minaccioso`, `inesorabile`, `incisivo`, `ostinato` |
| 🌙 Mysterious | `misterioso`, `oscuro`, `sospeso`, `etereo` |
| ❤️ Emotional | `dolce`, `tenero`, `cantabile` |
| 🎵 Sustained/Legato | `sostenuto` |

### Example Workflow

```python
# Run multiple times with different moods to compare
python -m mcp_tooling.apply_melody_with_motifs allegro
python -m mcp_tooling.apply_melody_with_motifs furioso
python -m mcp_tooling.apply_melody_with_motifs misterioso

# For legato passages with long held notes:
python -m mcp_tooling.apply_melody_with_motifs sostenuto

# Each creates a track named after the mood for easy A/B comparison
```

### Analyze Existing Tracks

You can analyze the MIDI from any instrument track (e.g., generated keys/piano) to infer the progression and generate a melody.

```bash
# Analyze a specific track by name
python -m mcp_tooling.apply_melody_with_motifs giocoso --chord-track-name "Ska Keys Final" --key Ab --scale aeolian
```

## How It Works

1. **Chord Analysis**:
   - Default: Reads clips from Track 0/2 ("Chords").
   - **New**: Can read from any track via `--chord-track-name` or `--chord-track-index`.
   - Infers chords from polyphonic MIDI or arpeggios (`robust_infer_chord`).
2. **Roman Numeral Inference**: Maps notes to the specified Key/Scale.
3. **Melody Generation**: Generates diatonically-correct pitches.
4. **Track Creation**: Creates a new track (e.g., `allegro`) with the result.

## Mood Profile Parameters

Each mood profile controls:

| Parameter | Description |
|:----------|:------------|
| `density` | Note density (0.0-1.0), higher = more notes |
| `durations` | Available note lengths in beats (e.g., `[0.25, 0.5, 1.0, 2.0, 4.0]`) |
| `velocity` | Range `(min, max)` for velocity randomization |
| `leap` | Probability of melodic leaps vs stepwise motion |
| `rest` | Probability of inserting rests |
| `sustain` | Note length multiplier (0.6-1.0), higher = more legato |
| `prefer_long` | Duration weighting toward longer notes (0.0-0.8) |
| `motif_chance` | **NEW** Probability of using motif patterns (default: 0.35) |
| `contour` | **NEW** Phrase shape: `arch`, `wave`, `ascending`, `descending`, `static` |

## Configuration

To change the chord source track or key, edit `apply_melody_with_motifs.py`:

```python
# Line 60-62
CHORD_TRACK_IDX = 2   # Change to your chord track index
KEY_ROOT = 66         # 66 = F#, 60 = C, 62 = D, etc.
SCALE = "mixolydian"  # Options: major, minor, dorian, phrygian, mixolydian, etc.
```

## API Reference

### `generate_melody(mood="allegro")`

Main function that orchestrates melody generation.

**Args:**
- `mood`: Italian mood term (default: "allegro")

### `generate_melody_from_progression()` (from `mcp_tooling.melody`)

Core generator used internally.

**Args:**
- `chords`: List of Roman numerals (e.g., `["I", "IV", "V", "I"]`)
- `key`: Key root (e.g., "F#")
- `scale`: Scale name (e.g., "mixolydian")
- `beats_per_chord`: Duration per chord in beats
- `velocity`: Base velocity
- `octave`: Starting octave
- `mood`: Mood profile name

**Returns:**
- `(notes, total_length)`: List of note dicts and total length in beats

## Tips

- **Rapid Iteration**: Run the same mood multiple times - each run is non-deterministic
- **Track Naming**: Tracks are named after moods, making A/B comparison trivial
- **Cleanup**: Delete unused mood tracks after deciding on a variation
- **Key Changes**: Modify `KEY_ROOT` in the script for different keys
