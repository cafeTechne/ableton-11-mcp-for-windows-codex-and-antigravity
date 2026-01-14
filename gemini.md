# AbletonMCP

AI-to-Ableton-Live bridge with 220+ MCP tools for absolute session control.

## Architecture
```
Remote Script (Ableton) ←→ Socket ←→ MCP Server (Python) ←→ AI Agent
```

## Environment Setup

```bash
# Prerequisites
- Python 3.10+
- Ableton Live 11/12 with Remote Script installed
- UV package manager (recommended)

# Installation
cd MCP_Server
uv venv && .venv\Scripts\activate  # Windows
uv sync

# Verify connection
python tests/verify_all_commands.py
```

## Commands

### File-Scoped (Preferred - Fast)
```bash
python tests/verify_all_commands.py          # API verification
python -c "from mcp_tooling.connection import get_ableton_connection; print(get_ableton_connection().send_command('get_song_context', {}))"
```

### Full Test Suite
```bash
cd MCP_Server
python -m pytest tests/
```

## ⚠️ Remote Script Deployment

> **CRITICAL**: After modifying ANY file in `AbletonMCP_Remote_Script/`, you MUST:
>
> **Step 1: Deploy**
> ```bash
> python scripts/deploy.py --clean
> ```
>
> **Step 2: Reload in Ableton (FULL RESTART REQUIRED)**
> 1. Go to Preferences → Link/MIDI → Set Control Surface to **"None"**
> 2. **Close Ableton completely**
> 3. **Restart Ableton**
> 4. Go to Preferences → Link/MIDI → Set Control Surface back to **"AbletonMCP_Remote_Script"**
>
> ⚠️ Simply toggling the Control Surface without restarting Ableton does NOT reload the script!

## Critical Implementation Notes

### Audio Humanization
- **NOT SUPPORTED / NOT REQUIRED**.
- Do not attempt to implement audio humanization via pitch envelopes or transposition automation.
- Focusing on MIDI humanization is sufficient.

### MIDI Constants
- **Velocity Deviation**: Recommended range is **10-30%** (up from 5-15%).
- **Probability**: 95-100% recommended for subtle humanization.

### Live API Quirks
- **`apply_note_modifications`**: STRICTLY requires a `MidiNoteVector` object (C++ handle).
  - ❌ Do NOT pass a Python `list` or `tuple`.
  - ✅ Pass the original vector object returned by `get_notes_extended` (after modifying its elements' properties).


| Problem | ❌ Wrong | ✅ Correct |
|:---|:---|:---|
| EQ Frequency | `freq=180` (Hz) | `freq=0.299` (normalized) |
| EQ Gain | `gain=-3` (dB) | `gain=0.4` (normalized) |
| Volume | N/A | `0.0-1.0` (0.85 = 0dB) |
| Panning | N/A | `-1.0` to `1.0` |
| Track detection | Hardcoded indices | Use `get_song_context` |
| Group Tracks | `get_track_info(group_idx)` | `get_song_context` + blind ops / `search_and_load` |

> ⚠️ **API LIMITATION**: `get_track_info` fails on **Group Tracks** with "Master and Return Tracks have no 'Arm' state!". Use `get_song_context` to identify tracks, and use blind operations (e.g. `set_device_parameter` or `search_and_load_device`) which do not trigger this error.


## Conversion Formulas

```python
# EQ Frequency (10 Hz - 22 kHz, logarithmic)
norm = log(freq_hz / 10) / log(2200)

# EQ Gain (-15 dB to +15 dB, linear)
norm = (db + 15) / 30

# Use helper functions from server.py
from server import hz_to_normalized, db_to_normalized
```

## Tool Categories

| Category | Count | Key Tools |
|:---|:---|:---|
| Mixer | 25 | `set_master_volume`, `set_return_volume`, `set_track_send`, `set_crossfader` |
| Transport | 15 | `tap_tempo`, `nudge_tempo`, `jump_by`, `set_loop`, `set_swing_amount` |
| Scene | 15 | `fire_scene_by_name`, `move_scene`, `get_scene_info`, `fire_scene_by_index` |
| Clip | 30 | `create_clip_in_slot`, `duplicate_loop`, `set_clip_markers`, `transpose_clip`, `apply_legato` |
| MIDI/Notes | 15 | `add_notes_to_clip_tool`, `select_all_notes`, `get_notes_extended`, `update_notes` |
| Device | 25 | `get_specialized_device_info`, `set_eq8_band`, `set_compressor_sidechain`, `get_rack_macros` |
| Drum Rack | 10 | `get_drum_rack_info`, `copy_drum_pad`, `set_drum_pad_choke_group`, `mute_drum_pad` |
| Simpler | 12 | `reverse_simpler_sample`, `crop_simpler_sample`, `set_simpler_playback_mode` |
| Browser | 10 | `get_browser_category`, `filter_browser`, `toggle_browser`, `preview_item_by_uri` |
| Application | 15 | `focus_view`, `zoom_view`, `scroll_view`, `get_application_overview` |
| Track | 15 | `fold_group`, `set_track_color`, `create_midi_track`, `set_track_monitor` |
| Arrangement | 10 | `get_arrangement_info`, `create_cue_point`, `set_arrangement_loop`, `set_song_time` |
| Generator | 15 | `generate_chord_progression_advanced`, `pattern_generator` |


## Workflows

Detailed patterns in `.agent/workflows/`:

| Workflow | Command | Purpose |
|:---|:---|:---|
| Load Device | `/load-device` | Load EQ, Compressor, instruments |
| Audio FX Reference | `/audio-effects-reference` | Built-in Audio Effects overview |
| Configure EQ | `/configure-eq` | EQ with normalized values |
| Mixer Ops | `/mixer-operations` | Track/Master/Return volume, pan, sends |
| Generate Chords | `/generate-chords` | Chord progressions with theory |
| Generate MIDI | `/generate-midi` | MIDI clip creation |
| Arpeggiator | `/arpeggiator` | Arpeggiator device control |
| Track Info | `/get-track-info` | Track inspection |
| Track Management | `/track-management` | Create/Find tracks, Groups, Folding |
| Rack Management | `/rack-management` | Parallel chains, Zones, Macros |
| Scene Operations | `/scene-operations` | Advanced Scene/Fire-by-name |
| Transport Control | `/transport-control` | Tempo, Nudge, Jump, Loops |
| Song Blueprint | `/song-blueprint` | Full song generation |
| Automation | `/automation` | Parameter automation ramps |
| Perf. Recording | `/automation-performance` | Capture MIDI, Overdub, Session Rec |
| Humanization | `/humanization` | Per-note probability and deviation |
| Sample Loading | `/sample-loading` | Load/Edit samples in Simpler/Sampler |
| Drum Patterns | `/drum-patterns` | Generate drum patterns |
| Drum Racks | `/drum-rack-management` | Pad controls, Choke groups, Solos |
| MIDI Editing | `/midi-editing` | Selection, Humanization, Bulk updates |
| Conversions | `/conversions` | Audio-to-MIDI, Slicing, Flattening |
| Groove Pool | `/groove-and-timing` | Swing, Groove amount, Clip grooves |
| Browser Nav | `/browser-navigation` | Deep search, Filtering, Previews |
| Creative | `/creative-sound-design` | Unlinked envelopes, Sample scrambling |
| Orchestration | `/orchestration` | Strings, brass, woodwinds |
| Custom Progressions | `/custom-progressions` | Generate music from bar charts (e.g. \| i \| IV \|) |
| Apply Melody | `/apply-melody` | Mood-driven melodies from chords |
| VST Support | `/vst-support` | How to use VST/AU plugins |
| Application Views | `/application-view` | Zoom, Scroll, Focus control |
| Specialized Devices | `/specialized-devices` | EQ8 and Compressor surgical control |
| Performance | `/performance-optimization` | CPU optimization, Latency, Buffers |

## Key Helper Functions

These are available in `mcp_tooling/` for user scripts:

```python
from mcp_tooling.devices import search_and_load_device
from mcp_tooling.ableton_helpers import ensure_track_exists, load_sample_to_simpler
from mcp_tooling.generators import generate_chord_progression_advanced
from mcp_tooling.melody import generate_melody_from_progression, MOOD_PROFILES
```

| Function | Module | Purpose |
|:---|:---|:---|
| `search_and_load_device()` | devices | Search + load device by name |
| `ensure_track_exists()` | ableton_helpers | Create track if needed |
| `load_sample_to_simpler()` | ableton_helpers | Load audio into Simpler |
| `generate_melody_from_progression()` | melody | Mood-driven melody from chords |

## Track Detection Pattern

**Always verify tracks exist before operations:**

```python
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# Get all tracks
context = conn.send_command("get_song_context", {"include_clips": False})
tracks = context.get("tracks", [])

# Find track by name
for track in tracks:
    if "Bass" in track.get("name", ""):
        bass_idx = track["index"]
```

## Code Patterns

### ✅ Good Patterns
- `MCP_Server/server.py` - Tool definitions with docstrings
- `MCP_Server/user_scripts/configure_session_eqs.py` - Correct EQ with normalized values
- `MCP_Server/mcp_tooling/chords.py` - Music theory library

### ❌ Avoid
- Sending raw Hz/dB values to EQ (causes silence)
- Hardcoded track indices without verification
- Not waiting after device load operations
- Using deprecated `get_session_info` (use `get_song_context`)

## Project Structure

```
MCP_Server/
├── server.py              # All 220+ MCP tools
├── mcp_tooling/           # Music generation library
│   ├── devices.py         # Device loading helpers
│   ├── ableton_helpers.py # Track/clip utilities
│   ├── generators.py      # MIDI generators
│   ├── chords.py          # Chord/scale theory
│   └── connection.py      # Ableton socket connection
├── tests/                 # Test scripts
├── examples/              # Demo scripts
└── user_scripts/          # Custom automation (13 scripts)

AbletonMCP_Remote_Script/
├── interface.py           # Command dispatch
└── handlers/              # API handlers
    ├── device.py          # Device operations
    ├── specialized.py     # EQ8, Compressor
    └── track.py           # Track operations
```

## Permissions

### Allowed Without Prompting
- Read track/device info (`get_song_context`, `get_track_info`)
- Run verification scripts
- Generate MIDI patterns (creates clips, non-destructive)

### Require Approval
- `delete_track`, `delete_clip`, `delete_scene`
- Bulk operations (>5 tracks)
- `start_playback` in untested sessions
- Package installations

## Troubleshooting

### Connection Failed
1. Verify Ableton is running
2. Check Remote Script is selected in Preferences → Link/MIDI
3. Restart Ableton (Remote Script loads on startup)

### Device Not Found
```python
# Always check track info first
info = conn.send_command("get_track_info", {"track_index": 0})
print(info["devices"])  # Check class_name
```

### EQ Silence Issue
You sent raw Hz values. Use normalized:
```python
# Wrong: freq=180
# Right: freq=hz_to_normalized(180)  # Returns 0.299
```

## Testing

```bash
# Quick API check
python tests/verify_all_commands.py

# Test specific category
python -c "
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()
print(conn.send_command('get_song_context', {'include_clips': False}))
"
```

## Additional Resources
- Workflows: `.agent/workflows/`
- Examples: `MCP_Server/examples/`
- User scripts: `MCP_Server/user_scripts/`
- Test scripts: `MCP_Server/tests/`

## Live 11 API Reference

The `live_api_docs_download/` folder contains Live 11 API documentation:

| File | Purpose |
|:---|:---|
| `live_api_11.pretty.xml` | **Primary reference** - full Live Object Model with all classes, methods, properties |
| `live_api_11.strings.txt` | **Quick lookup** - alphabetized list of all API names/descriptions |

**Key modules for advanced features:**
- `Live.Conversions` - Audio-to-MIDI, slice-to-drum-rack conversions
- `RackDevice` - Macro control (`macros` property), chain management
- `SimplerDevice` - Slicing, playback modes, sample control
- `DrumPad` - Drum rack pad manipulation

**Example grep searches:**
```bash
grep -i "macro" live_api_11.pretty.xml
grep -i "slice" live_api_11.pretty.xml
grep "RackDevice" live_api_11.strings.txt
```
