---
description: How to create and manage tracks safely
---

# Track Management

Tracks can change between prompts. **Always verify before operations.**

> [!CAUTION]
> **NEVER DELETE TRACKS UNLESS EXPLICITLY ASKED.**
> This project uses an **Ableton Template** where tracks come pre-loaded with specific devices, instruments, and sound designs (e.g., "1bs_phasesynth_x64", "Magical8bitPlug2").
> 
> **Deleting a track destroys this sound design.**
> 
> If you encounter a track type mismatch (e.g., expecting MIDI but finding Audio/Group), **STOP** and ask the user or try to work around it generally. DO NOT assume you can delete and recreate it.


## Get All Tracks

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

context = conn.send_command("get_song_context", {"include_clips": False})
tracks = context.get("tracks", [])

for track in tracks:
    print(f"{track['index']}: {track['name']} ({'MIDI' if track.get('is_midi_track') else 'Audio'})")
```

## Find Track by Name

```python
def find_track_by_name(conn, name):
    context = conn.send_command("get_song_context", {"include_clips": False})
    for track in context.get("tracks", []):
        if name.lower() in track.get("name", "").lower():
            return track.get("index")
    return -1

# Usage
bass_idx = find_track_by_name(conn, "Bass")
if bass_idx == -1:
    print("Bass track not found!")
```

## Create Tracks

```python
# MIDI track (for instruments)
result = conn.send_command("create_midi_track", {"index": -1})  # -1 = append
new_idx = result.get("index")

# Audio track (for recording/samples)
result = conn.send_command("create_audio_track", {"index": -1})

# Name the track
conn.send_command("set_track_name", {"track_index": new_idx, "name": "Lead Synth"})
```

## Ensure Track Exists (Safe Pattern)

```python
from mcp_tooling.ableton_helpers import ensure_track_exists

# Returns existing track index or creates new one
track_idx = ensure_track_exists(None, prefer="midi", allow_create=True)
```

## Delete Tracks (Use Caution)

> [!CRITICAL]
> **DO NOT DELETE TRACKS TO "FIX" THEM.**
> If a track has a different type than expected, it is likely a template decision. Deleting it erases the user's sound design.
> **Only use this command if the user has explicitly requested to remove a track.**

```python
# Verify before deleting
info = conn.send_command("get_track_info", {"track_index": idx})
print(f"Deleting: {info['name']}")

conn.send_command("delete_track", {"track_index": idx})
```

# Get group structure
groups = conn.send_command("get_track_groups", {})
```

## Advanced Group Behavior

### Submix vs. Folder Tracks
- **Submix (Default)**: Tracks in a group route their audio to the Group Track. This allows for collective processing (e.g., Drum Bus).
- **Folder Mode**: Tracks are grouped for organization but route their entries individually (e.g., to Master). 

### Nesting and Structure
Groups can be nested within other groups to create complex orchestral or drum hierarchies.

```python
# Group a pair of existing Groups
conn.send_command("group_tracks", {"track_indices": [0, 4]}) 
```

### Color Propagation
Assigning a color to a Group Track can be propagated to all contained tracks and clips for visual organization.

```python
# Set group color and propagate
conn.send_command("set_track_color", {"track_index": 0, "color": 12})
conn.send_command("assign_group_color_to_children", {"track_index": 0})
```

## Track Aesthetics

```python
# Set track color (Ableton color index 0-69)
conn.send_command("set_track_color", {"track_index": idx, "color": 12})
```

## Common Patterns

### Setup Session from Scratch
```python
tracks = [
    ("Drums", "midi"),
    ("Bass", "midi"),
    ("Keys", "midi"),
    ("Vocals", "audio"),
]

for name, track_type in tracks:
    cmd = "create_midi_track" if track_type == "midi" else "create_audio_track"
    result = conn.send_command(cmd, {"index": -1})
    idx = result.get("index")
    conn.send_command("set_track_name", {"track_index": idx, "name": name})
```

### Load Instrument on Track
```python
from mcp_tooling.devices import search_and_load_device
import time

# Create track
result = conn.send_command("create_midi_track", {"index": -1})
idx = result.get("index")
conn.send_command("set_track_name", {"track_index": idx, "name": "Piano"})

# Load instrument
search_and_load_device(idx, "Grand Piano", "instruments")
time.sleep(1.0)  # Wait for device to load
```
