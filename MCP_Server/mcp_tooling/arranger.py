import random
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Section:
    name: str           # e.g., "Verse 1", "Chorus"
    bars: int           # Length in bars
    density: float      # 0.0 to 1.0 (How many elements are active? 1.0 = All)
    role: str           # "Groove", "Hook", "Build", "Break", "Outro"
    progression_ref: Optional[str] = None # Reference to a progression key (e.g. "Main", "Bridge")

class Arranger:
    def __init__(self, bpm: int = 120):
        self.bpm = bpm
    
    def _seconds_to_bars(self, seconds: float) -> int:
        beats = (seconds / 60.0) * self.bpm
        return int(beats / 4) # Assuming 4/4

    def generate_structure_rubin(self, total_seconds: float = 210) -> List[Section]:
        """
        Rick Rubin / Reductive Style:
        - Start STRONG (Groove/Hook immediately)
        - Strip elements away to create dynamics
        - Focus on "The Vibe" rather than formal V-C-V-C
        """
        total_bars = self._seconds_to_bars(total_seconds)
        sections = []
        
        # 1. The "Hook" / "Main Groove" (The core identity)
        # Rubin often establishes the beat immediately.
        # "Don't bore us, get to the chorus" (or at least the groove)
        
        # Structure Strategy:
        # A (Full) -> A (Reduced) -> B (Change) -> A (Full) -> C (Breakdown) -> A (Building) -> Outro
        
        # We define a "Main" progression and a "Change" progression.
        
        # Section 1: Intro / Establish Groove (High Density)
        sections.append(Section(name="Intro Groove", bars=8, density=0.8, role="Groove", progression_ref="Main"))
        
        # Section 2: The Verse/Vibe (Reduced Density - strip the guitar/keys, leave bass/drums)
        sections.append(Section(name="Verse 1", bars=16, density=0.4, role="Vibe", progression_ref="Main"))
        
        # Section 3: The Pre-Chorus / Build (Add elements back)
        sections.append(Section(name="Pre-Chorus", bars=8, density=0.7, role="Build", progression_ref="Main"))
        
        # Section 4: The Hook (Max Density)
        sections.append(Section(name="Hook 1", bars=16, density=1.0, role="Hook", progression_ref="Main"))
        
        # Section 5: Verse 2 (Different reduction - e.g. Bass cut, just Drums + Keys)
        sections.append(Section(name="Verse 2", bars=16, density=0.5, role="Vibe", progression_ref="Main"))
        
        # Section 6: Hook 2
        sections.append(Section(name="Hook 2", bars=16, density=1.0, role="Hook", progression_ref="Main"))
        
        # Section 7: The Change / Bridge (Different harmony, stripped down?)
        # Rubin might go purely rhythmic here or change the feel entirely.
        sections.append(Section(name="Bridge/Change", bars=16, density=0.6, role="Change", progression_ref="Bridge"))
        
        # Section 8: Breakdown (Minimalist - maybe just vocals/lead + kick)
        sections.append(Section(name="Breakdown", bars=8, density=0.2, role="Break", progression_ref="Main"))
        
        # Section 9: Final Outro (Groove out)
        sections.append(Section(name="Outro", bars=16, density=0.8, role="Groove", progression_ref="Main"))
        
        # Scale to fit total bars if needed?
        # current_bars = sum(s.bars for s in sections)
        # For now, this template is approx 120 bars -> ~4 mins at 120bpm. Acceptable.
        
        return sections

    def generate_structure_progressive(self, total_seconds: float = 210) -> List[Section]:
        """Through-composed journey."""
        # TODO implement if requested
        return []

    def print_plan(self, sections: List[Section]):
        print(f"--- Arrangement Plan ({sum(s.bars for s in sections)} bars) ---")
        for i, s in enumerate(sections):
            print(f"{i+1:02d}. [{s.role}] {s.name} ({s.bars} bars) - Density: {int(s.density*100)}%")

if __name__ == "__main__":
    # Test
    arr = Arranger(bpm=120)
    plan = arr.generate_structure_rubin(210)
    arr.print_plan(plan)
