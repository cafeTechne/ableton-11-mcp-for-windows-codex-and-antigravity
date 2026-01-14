import random
from typing import List, Dict, Optional
from mcp_tooling.theory import Mode, key_to_midi, get_chord_notes

# Functional Harmony Groups (simplification)
TONIC = ['I', 'vi', 'iii']
SUBDOMINANT = ['IV', 'ii']
DOMINANT = ['V', 'vii_dim']

# Transitions (Markov-chain style weights)
TRANSITIONS = {
    'TONIC': {'TONIC': 0.3, 'SUBDOMINANT': 0.4, 'DOMINANT': 0.3},
    'SUBDOMINANT': {'TONIC': 0.2, 'SUBDOMINANT': 0.3, 'DOMINANT': 0.5},
    'DOMINANT': {'TONIC': 0.8, 'SUBDOMINANT': 0.1, 'DOMINANT': 0.1}
}

class ProgressionGenerator:
    def __init__(self, key: str = "C", mode_name: str = "ionian"):
        self.key_root = key_to_midi(key)
        self.mode = Mode(mode_name, self.key_root)
        self.mode_name = mode_name.lower()
        
    def _get_function_group(self, degree_roma: str) -> str:
        # Very rough estimation for Major keys
        # For minor/other modes, this needs mapping, but let's stick to functional concepts
        d = degree_roma.lower().replace("dim", "").replace("+", "").replace("7", "").replace("v", "V") # preserve V case? no
        
        # Normalize for lookup
        # Simple functional map for Ionian
        if degree_roma in ['I', 'vi', 'iii', 'i', 'III', 'VI']: return 'TONIC'
        if degree_roma in ['IV', 'ii', 'iv', 'II']: return 'SUBDOMINANT'
        if degree_roma in ['V', 'vii', 'v', 'VII']: return 'DOMINANT'
        return 'TONIC' # Default

    def generate(self, length: int = 4, complexity: float = 0.3, start_degree: Optional[int] = None) -> List[Dict]:
        """
        Generate a chord progression using functional harmony logic.
        
        Args:
            length: Number of chords
            complexity: 0.0 to 1.0 (chance of non-diatonic chords)
            start_degree: Force the first chord to be this scale degree (1-based)
        """
        progression = []
        
        # Initialize State
        current_degree = start_degree if start_degree else 1
        current_function = self._get_function_group(self.mode.get_roman_numeral(current_degree))
        
        for i in range(length):
            if i == 0 and start_degree:
                chosen_degree = start_degree
            else:
                # 1. Determine Next Function (T -> S -> D -> T)
                # Get transition probabilities from current function
                probs = TRANSITIONS.get(current_function, TRANSITIONS['TONIC'])
                next_func = random.choices(list(probs.keys()), weights=list(probs.values()), k=1)[0]
                
                # 2. Pick Degree from Function Group
                # We need a reverse lookup map or just candidate filtering
                candidates = []
                # Simple Diatonic Degree Map (1-7)
                for d in range(1, 8):
                    rn = self.mode.get_roman_numeral(d)
                    if self._get_function_group(rn) == next_func:
                        candidates.append(d)
                
                # Fallback if empty (shouldn't happen with standard definitions)
                if not candidates: candidates = [1, 4, 5]
                
                chosen_degree = random.choice(candidates)
                
                # Cadence Logic override for last chord?
                if i == length - 1:
                    # higher chance to resolve or turnaround
                    if random.random() > 0.4:
                        chosen_degree = 5 # Turnaround
                    elif random.random() > 0.7:
                        chosen_degree = 1 # Resolve
            
            # 2b. Update State
            current_degree = chosen_degree
            current_function = self._get_function_group(self.mode.get_roman_numeral(chosen_degree))

            # 3. Get Chord and Apply Rules
            notes = self.mode.get_chord(chosen_degree, extensions="7")
            rn = self.mode.get_roman_numeral(chosen_degree)
            tags = ["Diatonic"]
            
            # Rule: Secondary Dominant
            if complexity > 0.5 and random.random() < 0.2:
                if (notes[1] - notes[0]) == 3: # Minor 3rd
                     notes[1] += 1 # Make Major
                     rn += "(SecDom)"
                     tags.append("SecondaryDominant")
            
            # Rule: Modal Interchange
            if complexity > 0.3 and self.mode_name == 'ionian' and random.random() < 0.2:
                 parallel_minor = Mode("aeolian", self.key_root)
                 borrow_opts = [3, 6, 7]
                 borrow_deg = random.choice(borrow_opts)
                 notes = parallel_minor.get_chord(borrow_deg, extensions="7")
                 rn = f"b{self.mode.get_roman_numeral(borrow_deg).upper()}"
                 tags.append("ModalInterchange")
            
            progression.append({
                "degree": chosen_degree,
                "roman": rn,
                "notes": notes,
                "tags": tags
            })
            
        return progression

def generate_progression_midi(key="C", mode="ionian", length=4) -> List[List[int]]:
    """Helper to just get list of list of MIDI notes."""
    gen = ProgressionGenerator(key, mode)
    prog = gen.generate(length)
    return [p["notes"] for p in prog]

if __name__ == "__main__":
    # Test
    g = ProgressionGenerator("C", "ionian")
    p = g.generate(8, complexity=0.6)
    print("Generated C Major (Complex):")
    for ch in p:
        print(f"{ch['roman']} - {ch['notes']} - {ch['tags']}")

    print("\nGenerated C Dorian:")
    g_dor = ProgressionGenerator("C", "dorian")
    p_dor = g_dor.generate(4)
    for ch in p_dor:
        print(f"{ch['roman']} - {ch['notes']}")
