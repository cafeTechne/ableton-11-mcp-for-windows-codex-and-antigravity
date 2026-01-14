from mcp_tooling.theory import Mode
from mcp_tooling.progression_generator import ProgressionGenerator

def verify_harmony():
    print("Verifying Harmonic Engine Refactor...")
    
    # TEST 1: Mode Logic (C Dorian)
    # C Dorian: C D Eb F G A Bb
    # Intervals: 0 2 3 5 7 9 10
    print("\n[Test 1] C Dorian Logic")
    c_dorian = Mode("dorian", 60) # C3
    notes = c_dorian.get_scale_notes()
    # Expected: 60, 62, 63, 65, 67, 69, 70
    expected = [60, 62, 63, 65, 67, 69, 70]
    
    print(f"Scale Notes: {notes}")
    if notes == expected:
        print("PASS: C Dorian scale notes correct.")
    else:
        print(f"FAIL: Expected {expected}, got {notes}")

    # TEST 2: Dorian ii Chord
    # ii of C Dorian starts on D (62).
    # Chords in Dorian: i(min), ii(min), III(maj), IV(maj), v(min), vi(dim), VII(maj)
    # Wait, simple theory check:
    # 1(C) 3(Eb) 5(G) 7(Bb) = Cm7 (i)
    # 2(D) 4(F) 6(A) 8(C) = Dm7 (ii)  <-- Check this
    # 3(Eb) 5(G) 7(Bb) 9(D) = EbMaj7 (III)
    
    ii_chord = c_dorian.get_chord(2, extensions="7")
    print(f"ii Chord (Notes): {ii_chord}")
    # D3(62), F3(65), A3(69), C4(72)
    expected_ii = [62, 65, 69, 72]
    
    if ii_chord == expected_ii:
        print("PASS: Dorian ii chord is Dm7 (correct).")
    else:
        print(f"FAIL: Expected {expected_ii}, got {ii_chord}")

    # TEST 3: Generator Rules
    print("\n[Test 3] Progression Generator (C Major + Complexity)")
    gen = ProgressionGenerator("C", "ionian")
    
    # We force high complexity to trigger rules
    # But since it's random, we loop until we find one or give up
    found_complex = False
    
    for _ in range(5):
        prog = gen.generate(length=8, complexity=1.0)
        for ch in prog:
            if "SecondaryDominant" in ch["tags"] or "ModalInterchange" in ch["tags"]:
                print(f"Found complex chord: {ch['roman']} ({ch['tags']}) -> {ch['notes']}")
                found_complex = True
                break
        if found_complex: break
        
    if found_complex:
        print("PASS: Generator successfully created non-diatonic chords via rules.")
    else:
        print("WARN: Generator didn't trigger complex rules in 5 runs (might be bad luck or bug).")

if __name__ == "__main__":
    verify_harmony()
