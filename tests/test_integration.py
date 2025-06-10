"""
Integration tests for the Slide Audio Recorder application.
"""

import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.main import SlideRecorder
from src import config

class TestSlideRecorderIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Save original config values
        self.original_output_dir = config.DEFAULT_OUTPUT_DIR
        self.original_bitrate = config.BITRATE
        
        # Create a temporary test directory
        self.test_output_dir = Path('test_recordings')
        config.DEFAULT_OUTPUT_DIR = self.test_output_dir
        
        # Patch keyboard module
        self.keyboard_patcher = patch('keyboard.on_press_key')
        self.mock_keyboard = self.keyboard_patcher.start()
        
        # Patch keyboard.read_event
        self.read_event_patcher = patch('keyboard.read_event')
        self.mock_read_event = self.read_event_patcher.start()
        
        # Create recorder with mocked components
        self.recorder = SlideRecorder(enable_keyboard_hooks=False)
        
        # Setup mock for rich.prompt.Prompt
        self.prompt_patcher = patch('rich.prompt.Prompt.ask')
        self.mock_prompt = self.prompt_patcher.start()
        
    def tearDown(self):
        """Clean up after each test method."""
        # Restore original config values
        config.DEFAULT_OUTPUT_DIR = self.original_output_dir
        config.BITRATE = self.original_bitrate
        
        # Stop patches
        self.keyboard_patcher.stop()
        self.read_event_patcher.stop()
        self.prompt_patcher.stop()
        
        # Clean up test directory
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
            
        # Clean up any custom directories
        if hasattr(self, 'custom_dir') and self.custom_dir.exists():
            shutil.rmtree(self.custom_dir)
        
    def test_complete_recording_workflow(self):
        """Test the complete recording workflow."""
        # Mock audio data and user responses
        test_audio = b'test audio data'
        self.recorder.audio_recorder.record_chunk = MagicMock(side_effect=[True, True, False])
        self.recorder.audio_recorder.stop_recording = MagicMock(
            return_value=(test_audio, config.MIN_RECORDING_TIME + 1)
        )
        
        # Mock user choosing to save the recording
        self.mock_prompt.side_effect = ['s']
        
        # Mock the recording status to stop immediately
        def mock_display_recording_status(slide_number):
            self.recorder.cli.recording = False
            
        self.recorder.cli.display_recording_status = MagicMock(side_effect=mock_display_recording_status)
        
        # Record slide 1
        result = self.recorder.record_slide(1)
        self.assertTrue(result)
        
        # Verify recording was saved
        recording_path = config.get_recording_path(1)
        self.assertTrue(recording_path.exists())
        with open(recording_path, 'rb') as f:
            saved_data = f.read()
        self.assertEqual(saved_data, test_audio)
        
    def test_revisit_workflow(self):
        """Test the revisit workflow."""
        # Create a test recording
        test_audio = b'test audio data'
        self.recorder.file_manager.save_recording(test_audio, 1)
        
        # Mock user responses for playback, re-record, and exit
        self.mock_prompt.side_effect = ['p', 'b']
        
        # Setup mock for audio playback
        self.recorder.audio_recorder.play_recording = MagicMock()
        
        # Mock wait_for_key to do nothing
        self.recorder.cli.wait_for_key = MagicMock()
        
        # Revisit the recording
        self.recorder.revisit_recording(1)
        
        # Verify playback was called
        self.recorder.audio_recorder.play_recording.assert_called_once_with(test_audio)
        
    def test_rerecord_workflow(self):
        """Test the re-recording workflow."""
        # Create initial recording
        initial_audio = b'initial audio'
        new_audio = b'new audio'
        self.recorder.file_manager.save_recording(initial_audio, 1)
        
        # Mock recording process
        self.recorder.audio_recorder.record_chunk = MagicMock(side_effect=[True, False])
        self.recorder.audio_recorder.stop_recording = MagicMock(
            return_value=(new_audio, config.MIN_RECORDING_TIME + 1)
        )
        
        # Mock user choosing to re-record and save
        self.mock_prompt.side_effect = ['r', 's']
        
        # Mock the recording status to stop immediately
        def mock_display_recording_status(slide_number):
            self.recorder.cli.recording = False
            
        self.recorder.cli.display_recording_status = MagicMock(side_effect=mock_display_recording_status)
        
        # Re-record slide 1
        self.recorder.revisit_recording(1)
        
        # Verify new recording was saved
        recording_path = config.get_recording_path(1)
        self.assertTrue(recording_path.exists())
        with open(recording_path, 'rb') as f:
            saved_data = f.read()
        self.assertEqual(saved_data, new_audio)
        
        # Verify backup was created
        backup_path = recording_path.with_name(f"slide_001_backup.mp3")
        self.assertTrue(backup_path.exists())
        with open(backup_path, 'rb') as f:
            backup_data = f.read()
        self.assertEqual(backup_data, initial_audio)
        
    def test_delete_workflow(self):
        """Test the delete workflow."""
        # Create a test recording
        test_audio = b'test audio data'
        self.recorder.file_manager.save_recording(test_audio, 1)
        
        # Mock user choosing to delete and confirm
        self.mock_prompt.side_effect = ['d', 'y']
        
        # Delete the recording
        self.recorder.revisit_recording(1)
        
        # Verify recording was deleted
        self.assertFalse(config.get_recording_path(1).exists())
        
    def test_main_menu_workflow(self):
        """Test the main menu workflow."""
        # Create some test recordings
        test_audio = b'test audio data'
        self.recorder.file_manager.save_recording(test_audio, 1)
        self.recorder.file_manager.save_recording(test_audio, 2)
        
        # Mock user responses: view recordings, select recording 1, play, back to menu, exit
        self.mock_prompt.side_effect = ['2', '1', 'p', 'b', '3']
        
        # Setup mock for audio playback
        self.recorder.audio_recorder.play_recording = MagicMock()
        
        # Mock wait_for_key to do nothing
        self.recorder.cli.wait_for_key = MagicMock()
        
        # Run the application
        self.recorder.run()
        
        # Verify playback was called
        self.recorder.audio_recorder.play_recording.assert_called_once_with(test_audio)
        
    def test_error_handling_short_recording(self):
        """Test error handling for recordings that are too short."""
        # Mock recording process with short duration
        self.recorder.audio_recorder.record_chunk = MagicMock(side_effect=[True, False])
        self.recorder.audio_recorder.stop_recording = MagicMock(
            return_value=(b'short audio', config.MIN_RECORDING_TIME - 1)
        )
        
        # Mock user choosing not to retry
        self.mock_prompt.side_effect = ['n']
        
        # Mock the recording status to stop immediately
        def mock_display_recording_status(slide_number):
            self.recorder.cli.recording = False
            
        self.recorder.cli.display_recording_status = MagicMock(side_effect=mock_display_recording_status)
        
        # Attempt to record
        result = self.recorder.record_slide(1)
        
        # Verify recording failed and no file was created
        self.assertFalse(result)
        self.assertFalse(config.get_recording_path(1).exists())
        
    def test_audio_quality_settings(self):
        """Test different audio quality settings."""
        # Test low quality
        recorder_low = SlideRecorder(audio_quality='low', enable_keyboard_hooks=False)
        self.assertEqual(config.BITRATE, '64k')
        
        # Test medium quality
        recorder_med = SlideRecorder(audio_quality='medium', enable_keyboard_hooks=False)
        self.assertEqual(config.BITRATE, '96k')
        
        # Test high quality
        recorder_high = SlideRecorder(audio_quality='high', enable_keyboard_hooks=False)
        self.assertEqual(config.BITRATE, '128k')
        
    def test_custom_output_directory(self):
        """Test using a custom output directory."""
        self.custom_dir = Path('custom_test_dir')
        recorder = SlideRecorder(output_dir=str(self.custom_dir), enable_keyboard_hooks=False)
        self.assertEqual(config.DEFAULT_OUTPUT_DIR, self.custom_dir)
        self.assertTrue(self.custom_dir.exists())

if __name__ == '__main__':
    unittest.main() 