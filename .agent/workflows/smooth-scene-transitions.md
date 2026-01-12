---
description: How to smooth scene transitions using ramps, staggering, fills, and transition scenes
---

# Smooth Scene Transitions Workflow

Use the `transitions.py` tools to make scene changes less jarring.

## Prerequisites
- Session View with clips organized into scenes
- Return tracks with Reverb/Delay for "throws"

---

## Strategy 1: Parameter Ramps (Filter Sweeps)

Apply automation at the end of clips to smoothly transition.

```python
from mcp_tooling.transitions import apply_parameter_ramp

# Low-pass filter sweep down at end of scene
apply_parameter_ramp(
    track_index=0,
    clip_index=3,  # Scene 4
    parameter_name="Filter Freq",  # Fuzzy matched
    start_value=127,
    end_value=20,
    duration_beats=8.0,
    curve_type="exponential_out",
    offset_beats=24.0  # Start 24 beats in (for a 32-beat clip)
)
```

**Curve types**: `linear`, `exponential_in`, `exponential_out`, `fade_in`, `fade_out`

---

## Strategy 2: Staggered Clip Launch

Use different launch quantizations per clip for organic handoffs.

```python
from mcp_tooling.transitions import configure_clip_launch

# Pads trigger late (2 bars) while drums fire on 1 bar
configure_clip_launch(track_index=2, clip_index=0, quantization="2_bars")
configure_clip_launch(track_index=0, clip_index=0, quantization="1_bar")
```

**Quantization values**: `none`, `8_bars`, `4_bars`, `2_bars`, `1_bar`, `half`, `quarter`, `eighth`, `sixteenth`

---

## Strategy 3: Transition Scenes

Insert a dedicated scene between sections.

```python
from mcp_tooling.transitions import insert_transition_scene

# Insert after Scene 3, stripping drums but keeping pads
insert_transition_scene(after_scene_index=3, strategy="sustain_pads")
```

**Strategies**:
- `empty`: Blank scene for manual FX
- `copy_all`: Duplicate everything from previous scene
- `sustain_pads`: Copy pads/synths, strip drums

---

## Strategy 4: Micro-Fills

Add rhythmic "punctuation" before transitions.

```python
from mcp_tooling.transitions import generate_micro_fill

# Remove last beat (drop-out effect)
generate_micro_fill(track_index=1, clip_index=3, fill_type="drop_out")

# Add a snare roll
generate_micro_fill(track_index=1, clip_index=3, fill_type="snare_roll")
```

**Fill types**: `drop_out`, `snare_roll`, `crash`, `reverse_hit`

---

## Strategy 5: Reverb Throws

Swell a send level to create tail overlap.

```python
from mcp_tooling.transitions import apply_reverb_throw

# Throw to Send A (reverb) peaking at scene end
apply_reverb_throw(
    track_index=0,
    clip_index=3,
    send_index=0,  # Send A
    duration_beats=8.0,
    peak_value=0.8
)
```

---

## Recommended Workflow

1. **Identify problem transitions**: Listen for jarring cuts
2. **Add parameter ramps**: Filter or volume fades on 1-2 tracks
3. **Configure staggering**: Let pads or FX lag behind rhythm
4. **Add micro-fills**: Drop-out or roll on drums
5. **Insert transition scenes**: For major section changes
6. **Apply reverb throws**: For atmospheric continuity

## Common Patterns

| Transition Type | Recommended Tools |
|-----------------|-------------------|
| Verse → Chorus | Filter ramp up, crash, reverb throw |
| Chorus → Breakdown | Drop-out, sustain_pads scene |
| Build-up → Drop | Snare roll, filter sweep, staggered launch |
| Outro | Fade-out ramps, reverb throw |
