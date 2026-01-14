import logging
import sys
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_safety")

def test_safety_logic():
    print("Testing Safety Logic...")
    
    # We need to mock get_ableton_connection from mcp_tooling.connection
    # because we might not have a running Live instance or want to act on it.
    
    with patch("mcp_tooling.safe_mode.get_ableton_connection") as mock_get_conn:
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        from mcp_tooling.safe_mode import Target, SafetyError
        
        # Scenario 1: Existing "Safe" track
        print("\n[Test 1] Existing 'Scratchpad' Track")
        mock_conn.send_command.return_value = {"name": "My Scratchpad", "color": 123}
        t1 = Target(track_index=1)
        try:
            allowed = t1.allow_creation()
            print(f"PASS: allow_creation() returned {allowed} for 'Scratchpad'")
        except SafetyError as e:
            print(f"FAIL: Should allow scratchpad. Error: {e}")

        # Scenario 2: Existing "Protected" track
        print("\n[Test 2] Existing 'Kick' Track")
        mock_conn.send_command.return_value = {"name": "Kick", "color": 123}
        t2 = Target(track_index=2)
        try:
            t2.allow_creation()
            print("FAIL: Should have raised SafetyError for 'Kick'")
        except SafetyError as e:
            print(f"PASS: Correctly blocked 'Kick'. Error: {e}")
            
        # Scenario 3: Non-existent track
        print("\n[Test 3] Non-existent Track (Index 99)")
        mock_conn.send_command.side_effect = Exception("Index out of range")
        t3 = Target(track_index=99)
        # For non-existent, allow_creation should be True (we can create there)
        try:
            allowed = t3.allow_creation()
            print(f"PASS: allow_creation() returned {allowed} for empty slot")
        except SafetyError as e:
            print(f"FAIL: Should allow empty slot. Error: {e}")
            
        print("\nSafety Verification Complete.")

if __name__ == "__main__":
    test_safety_logic()
