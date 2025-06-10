"""
Tests for the file management module.
"""

import os
import shutil
import unittest
from pathlib import Path
from src.file_manager import FileManager
from src import config

class TestFileManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary test directory
        self.test_output_dir = Path('test_recordings')
        config.DEFAULT_OUTPUT_DIR = self.test_output_dir
        self.file_manager = FileManager()
        
    def tearDown(self):
        """Clean up after each test method."""
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
            
    def test_init_creates_directory(self):
        """Test that initialization creates the output directory."""
        self.assertTrue(self.test_output_dir.exists())
        self.assertTrue(self.test_output_dir.is_dir())
        
    def test_save_recording(self):
        """Test saving a recording to disk."""
        test_data = b'test audio data'
        slide_number = 1
        
        # Save the recording
        output_path = self.file_manager.save_recording(test_data, slide_number)
        
        # Verify the file exists and contains correct data
        self.assertTrue(output_path.exists())
        with open(output_path, 'rb') as f:
            saved_data = f.read()
        self.assertEqual(test_data, saved_data)
        
    def test_delete_recording(self):
        """Test deleting a recording."""
        # Create a test recording
        test_data = b'test audio data'
        slide_number = 1
        self.file_manager.save_recording(test_data, slide_number)
        
        # Test successful deletion
        self.assertTrue(self.file_manager.delete_recording(slide_number))
        self.assertFalse(config.get_recording_path(slide_number).exists())
        
        # Test deletion of non-existent file
        self.assertFalse(self.file_manager.delete_recording(999))
        
    def test_get_recording_list(self):
        """Test getting list of recorded slides."""
        # Create some test recordings
        test_data = b'test audio data'
        test_slides = [1, 3, 5]
        
        for slide in test_slides:
            self.file_manager.save_recording(test_data, slide)
            
        # Get the list and verify
        recorded_slides = self.file_manager.get_recording_list()
        self.assertEqual(test_slides, recorded_slides)
        
    def test_recording_exists(self):
        """Test checking if a recording exists."""
        test_data = b'test audio data'
        slide_number = 1
        
        # Test non-existent recording
        self.assertFalse(self.file_manager.recording_exists(slide_number))
        
        # Create recording and test again
        self.file_manager.save_recording(test_data, slide_number)
        self.assertTrue(self.file_manager.recording_exists(slide_number))
        
    def test_backup_recording(self):
        """Test backing up a recording."""
        test_data = b'test audio data'
        slide_number = 1
        
        # Test backup of non-existent file
        self.assertIsNone(self.file_manager.backup_recording(slide_number))
        
        # Create a recording and backup
        self.file_manager.save_recording(test_data, slide_number)
        backup_path = self.file_manager.backup_recording(slide_number)
        
        # Verify backup exists and contains correct data
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        with open(backup_path, 'rb') as f:
            backup_data = f.read()
        self.assertEqual(test_data, backup_data)
        
    def test_get_next_slide_number(self):
        """Test getting next available slide number."""
        # Test with empty directory
        self.assertEqual(1, self.file_manager.get_next_slide_number())
        
        # Create some recordings and test
        test_data = b'test audio data'
        test_slides = [1, 2, 3]
        for slide in test_slides:
            self.file_manager.save_recording(test_data, slide)
            
        self.assertEqual(4, self.file_manager.get_next_slide_number())
        
    def test_ensure_directory_exists(self):
        """Test ensuring directory exists."""
        # Remove directory and verify it's gone
        shutil.rmtree(self.test_output_dir)
        self.assertFalse(self.test_output_dir.exists())
        
        # Ensure directory exists and verify
        self.file_manager.ensure_directory_exists()
        self.assertTrue(self.test_output_dir.exists())
        self.assertTrue(self.test_output_dir.is_dir())

if __name__ == '__main__':
    unittest.main() 