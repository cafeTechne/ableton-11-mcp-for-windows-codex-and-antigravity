
try:
    from mcp_tooling.melody import generate_melody_from_progression
    print("Import successful")
    
    notes = generate_melody_from_progression(
        chords=["i", "IV"],
        key="C",
        scale="dorian",
        mood="horn_section",
        seed=123
    )
    print(f"Generated {len(notes)} notes")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
