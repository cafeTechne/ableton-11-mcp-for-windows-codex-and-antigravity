---
description: How to generate music using custom bar-delimited chord progressions (e.g. | i | IV V |)
---

# Generative Workflow: Custom Chord Progressions

This workflow describes how to create music using specific, user-defined chord progressions with precise timing control using the "Bar Chart" syntax.

## 1. Syntax Overview

The syntax uses pipe characters `|` to represent bar lines (measures). Chords within a bar are spaced evenly.

**Format**: `| Chord1 | Chord2 Chord3 | ... |`

### Examples
- **One chord per bar**: `| i | IV | V | i |` (4 bars, 4 beats each)
- **Split bars**: `| i | IV V |` (Bar 1: i for 4 beats. Bar 2: IV for 2 beats, V for 2 beats).
- **Complex split**: `| i | ii V I |` (Bar 2 has 3 chords? Note: The logic splits evenly. `4/3` beats each).
- **Roman Numerals**: Supports `i`, `IV`, `bVII`, `ii°`, `V7`, `iii`, etc.
    - **Note**: Ensure strictly correct capitalization/case for the intended scale (e.g. `iii` in Major = Minor 3rd chord. `III` in Major = Major 3rd chord).

## 2. Using with Tools

You can pass this string directly to the `progression` argument of any generation tool.

### via Chat
Simply tell the assistant:
> "Generate a house piano track in F Minor using the progression: `| i | VI | III | bVII |`"

### via CLI / Scripts
When using `generate_track`, `generate_bass_track`, `generate_comp_track`, pass the string:

```python
generate_comp_track(
    track_index=1,
    key="F",
    scale="minor",
    progression="| i | VI | III | bVII |",
    style="house_piano"
)
```

## 3. Best Practices

- **Explicit Bars**: Always start and end with `|` for clarity, though internal pipes are what trigger the parsing.
- **Diatonic Consistency**: Ensure your Roman Numerals match the `scale` you provide (e.g. `aeolian` vs `minor`). Using `natural_minor` or `aeolian` ensures `III` is treated as the diatonic relative major, whereas in standard Major keys `III` is the major mediant.
- **Duration**: The parser assumes 4/4 time signature (4 beats per bar).

## 4. Supported Generative Styles
This feature works with ALL generative styles:
- **Bass**: `ska`, `walking`, `disco`, `house`, `reggae`.
- **Keys/Comp**: `ska_skank`, `house_piano`, `funk_stabs`.
- **Strings/Brass**: All orchestral generators support this syntax.
