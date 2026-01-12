
import unittest
from unittest.mock import MagicMock, patch
import logging

# Ensure we can import from the parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tooling.transitions import (
    apply_parameter_ramp,
    configure_clip_launch,
    insert_transition_scene,
    generate_micro_fill,
    apply_reverb_throw
)

# Disable logging for tests
logging.disable(logging.CRITICAL)

class TestTransitions(unittest.TestCase):
    
    @patch('mcp_tooling.transitions.get_ableton_connection')
    def test_apply_parameter_ramp(self, mock_get_conn):
        # Setup mock
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        # Mock responses
        mock_conn.send_command.side_effect = [
            # 1. get_track_info -> returns devices
            {"devices": [{"index": 0, "name": "Auto Filter"}]},
            # 2. get_device_parameters -> returns parameters
            {"parameters": [{"name": "Frequency", "original_name": "Cutoff"}]},
            # 3. set_clip_envelope -> success
            {"status": "success"}
        ]
        
        result = apply_parameter_ramp(
            track_index=0,
            clip_index=1,
            parameter_name="Freq",
            start_value=127,
            end_value=20,
            duration_beats=4.0
        )
        
        self.assertIn("Ramp applied", result)
        self.assertIn("Frequency", result)
        
        # Verify envelope generation calls
        # We expect 3 calls (get_info, get_params, set_envelope)
        self.assertEqual(mock_conn.send_command.call_count, 3)
        
        # Check arguments of the last call (set_clip_envelope)
        args, kwargs = mock_conn.send_command.call_args
        cmd, params = args
        self.assertEqual(cmd, "set_clip_envelope")
        self.assertEqual(params["parameter_name"], "Frequency")
        self.assertEqual(len(params["points"]), 33) # 4 beats * 8 pts/beat + 1

    @patch('mcp_tooling.transitions.get_ableton_connection')
    def test_configure_clip_launch(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = configure_clip_launch(
            track_index=0,
            clip_index=1,
            quantization="2_bars",
            legato=True
        )
        
        self.assertIn("configured", result)
        # Should initiate 2 calls (set_clip_property x2)
        self.assertEqual(mock_conn.send_command.call_count, 2)
        
        calls = mock_conn.send_command.call_args_list
        self.assertEqual(calls[0][0][0], "set_clip_property")
        self.assertEqual(calls[0][0][1]["property_name"], "launch_quantization")
        self.assertEqual(calls[0][0][1]["value"], 3) # 2_bars = 3 in map
        
        self.assertEqual(calls[1][0][0], "set_clip_property")
        self.assertEqual(calls[1][0][1]["property_name"], "legato")
        self.assertEqual(calls[1][0][1]["value"], True)

    @patch('mcp_tooling.transitions.get_ableton_connection')
    def test_insert_transition_scene_empty(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = insert_transition_scene(after_scene_index=2, strategy="empty")
        
        self.assertIn("Inserted empty transition scene", result)
        # 1. create_scene, 2. set_scene_name
        self.assertEqual(mock_conn.send_command.call_count, 2)
        
        # Check create_scene
        calls = mock_conn.send_command.call_args_list
        self.assertEqual(calls[0][0][0], "create_scene")
        self.assertEqual(calls[0][0][1]["scene_index"], 3) # 2 + 1

    @patch('mcp_tooling.transitions.get_ableton_connection')
    def test_generate_micro_fill_dropout(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        mock_conn.send_command.side_effect = [
            # 1. get_clip_info
            {"length": 4.0, "notes": [{"pitch": 36, "start_time": 3.5}]},
            # 2. remove_notes_from_clip (if notes found)
            {}
        ]
        
        result = generate_micro_fill(track_index=0, clip_index=0, fill_type="drop_out")
        
        self.assertIn("Drop-out applied", result)
        self.assertEqual(mock_conn.send_command.call_count, 2)
        
        args, _ = mock_conn.send_command.call_args
        cmd, params = args
        self.assertEqual(cmd, "remove_notes_from_clip")
        self.assertEqual(params["start_time"], 3.0) # 4.0 - 1.0

    @patch('mcp_tooling.transitions.get_ableton_connection')
    def test_apply_reverb_throw(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        mock_conn.send_command.side_effect = [
            # 1. get_clip_info (to get length)
            {"length": 8.0},
            # 2. set_clip_send_envelope
            {"status": "success"}
        ]
        
        result = apply_reverb_throw(
            track_index=1, 
            clip_index=1, 
            send_index=0, 
            duration_beats=4.0, 
            peak_value=0.5
        )
        
        self.assertIn("Reverb throw applied", result)
        self.assertEqual(mock_conn.send_command.call_count, 2)
        
        args, _ = mock_conn.send_command.call_args
        cmd, params = args
        self.assertEqual(cmd, "set_clip_send_envelope")
        points = params["points"]
        # Duration is 4 beats, resolution 0.25 -> 16 + 1 points
        self.assertEqual(len(points), 17) 
        # Check start time of first point: length 8, duration 4 -> start at 4
        self.assertEqual(points[0][0], 4.0)

if __name__ == '__main__':
    unittest.main()
