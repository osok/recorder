"""
File management functionality for the Slide Audio Recorder.
"""

import os
from pathlib import Path
from typing import List, Optional
import shutil

from . import config

class FileManager:
    def __init__(self):
        """Initialize the file manager."""
        config.init()  # Ensure output directory exists
        
    def save_recording(self, audio_data: bytes, slide_number: int) -> Path:
        """Save a recording to disk.
        
        Args:
            audio_data: The audio data to save (WAV format).
            slide_number: The slide number to save as.
            
        Returns:
            Path to the saved file.
        """
        from .audio_recorder import AudioRecorder  # Import here to avoid circular dependency
        
        # Convert WAV to MP3 before saving
        recorder = AudioRecorder()
        mp3_data = recorder.convert_to_mp3(audio_data)
        
        output_path = config.get_recording_path(slide_number)
        with open(output_path, 'wb') as f:
            f.write(mp3_data)
        return output_path
    
    def delete_recording(self, slide_number: int) -> bool:
        """Delete a recording.
        
        Args:
            slide_number: The slide number to delete.
            
        Returns:
            True if the file was deleted, False if it didn't exist.
        """
        file_path = config.get_recording_path(slide_number)
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False
            
    def get_recording_list(self) -> List[int]:
        """Get a list of all recorded slide numbers.
        
        Returns:
            List of slide numbers that have been recorded.
        """
        files = config.DEFAULT_OUTPUT_DIR.glob('slide_*.mp3')
        return sorted([int(f.stem.split('_')[1]) for f in files])
        
    def recording_exists(self, slide_number: int) -> bool:
        """Check if a recording exists for a slide number.
        
        Args:
            slide_number: The slide number to check.
            
        Returns:
            True if the recording exists, False otherwise.
        """
        return config.get_recording_path(slide_number).exists()
        
    def backup_recording(self, slide_number: int) -> Optional[Path]:
        """Create a backup of a recording.
        
        Args:
            slide_number: The slide number to backup.
            
        Returns:
            Path to the backup file if successful, None if original doesn't exist.
        """
        source_path = config.get_recording_path(slide_number)
        if not source_path.exists():
            return None
            
        backup_path = source_path.with_name(f"slide_{slide_number:03d}_backup.mp3")
        shutil.copy2(source_path, backup_path)
        return backup_path
        
    def get_next_slide_number(self) -> int:
        """Get the next available slide number.
        
        Returns:
            The next available slide number.
        """
        return config.get_next_slide_number()
        
    def ensure_directory_exists(self):
        """Ensure the recordings directory exists."""
        config.init() 