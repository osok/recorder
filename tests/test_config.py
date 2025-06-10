"""
Tests for the configuration module.
"""

import os
import shutil
import unittest
from pathlib import Path
from src import config

class TestConfig(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary test directory
        self.test_output_dir = Path('test_recordings')
        config.DEFAULT_OUTPUT_DIR = self.test_output_dir
        
    def tearDown(self):
        """Clean up after each test method."""
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
            
    def test_init_creates_directory(self):
        """Test that init() creates the output directory."""
        config.init()
        self.assertTrue(self.test_output_dir.exists())
        self.assertTrue(self.test_output_dir.is_dir())
        
    def test_get_recording_path(self):
        """Test that get_recording_path returns correct paths."""
        expected_path = self.test_output_dir / 'slide_001.mp3'
        actual_path = config.get_recording_path(1)
        self.assertEqual(expected_path, actual_path)
        
        expected_path = self.test_output_dir / 'slide_042.mp3'
        actual_path = config.get_recording_path(42)
        self.assertEqual(expected_path, actual_path)
        
    def test_get_next_slide_number_empty_dir(self):
        """Test get_next_slide_number with empty directory."""
        config.init()
        self.assertEqual(1, config.get_next_slide_number())
        
    def test_get_next_slide_number_existing_files(self):
        """Test get_next_slide_number with existing files."""
        config.init()
        # Create some dummy files
        (self.test_output_dir / 'slide_001.mp3').touch()
        (self.test_output_dir / 'slide_002.mp3').touch()
        self.assertEqual(3, config.get_next_slide_number())
        
    def test_audio_settings_valid(self):
        """Test that audio settings are within acceptable ranges."""
        self.assertGreater(config.SAMPLE_RATE, 0)
        self.assertIn(config.CHANNELS, [1, 2])  # Mono or stereo
        self.assertGreater(config.CHUNK_SIZE, 0)
        self.assertEqual(config.FORMAT, 'mp3')
        self.assertTrue(config.BITRATE.endswith('k'))
        
    def test_recording_time_limits(self):
        """Test that recording time limits are valid."""
        self.assertGreater(config.MAX_RECORDING_TIME, config.MIN_RECORDING_TIME)
        self.assertGreater(config.MIN_RECORDING_TIME, 0)
        
    def test_keyboard_controls_unique(self):
        """Test that all keyboard controls are unique."""
        controls = [
            config.STOP_KEY,
            config.SAVE_KEY,
            config.RERECORD_KEY,
            config.PLAYBACK_KEY,
            config.BACK_KEY,
            config.DELETE_KEY
        ]
        self.assertEqual(len(controls), len(set(controls)), 
                        "Keyboard controls must be unique")

if __name__ == '__main__':
    unittest.main() 