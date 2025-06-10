"""
Main application entry point for the Slide Audio Recorder.
"""

import os
import signal
import sys
from pathlib import Path
from typing import Optional

from . import config
from .audio_recorder import AudioRecorder
from .cli_interface import CLIInterface
from .file_manager import FileManager

class SlideRecorder:
    def __init__(self, output_dir: Optional[str] = None, audio_quality: str = 'high',
                 enable_keyboard_hooks: bool = True):
        """Initialize the Slide Audio Recorder application.
        
        Args:
            output_dir: Optional custom output directory for recordings
            audio_quality: Audio quality setting ('low', 'medium', 'high')
            enable_keyboard_hooks: Whether to enable keyboard hooks (for testing)
        """
        # Set up output directory
        if output_dir:
            config.DEFAULT_OUTPUT_DIR = Path(output_dir)
            
        # Set up audio quality
        if audio_quality == 'low':
            config.BITRATE = '64k'
        elif audio_quality == 'medium':
            config.BITRATE = '96k'
        else:  # high
            config.BITRATE = '128k'
            
        # Initialize components
        self.file_manager = FileManager()
        self.audio_recorder = AudioRecorder()
        self.cli = CLIInterface(config, enable_keyboard_hooks=enable_keyboard_hooks)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        
    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signal (Ctrl+C)."""
        print("\nGracefully shutting down...")
        self.cleanup()
        sys.exit(0)
        
    def cleanup(self):
        """Clean up resources before exit."""
        self.audio_recorder.cleanup()
        
    def record_slide(self, slide_number: int) -> bool:
        """Record audio for a slide.
        
        Args:
            slide_number: The slide number to record.
            
        Returns:
            True if recording was saved, False if discarded.
        """
        while True:
            # Display status first
            self.cli.display_recording_status(slide_number)
            
            # Start recording
            self.audio_recorder.start_recording()
            
            # Record until stopped by spacebar
            while self.cli.recording and self.audio_recorder.record_chunk():
                pass
                
            # Get the recording
            audio_data, duration = self.audio_recorder.stop_recording()
            
            # Check minimum duration
            if duration < config.MIN_RECORDING_TIME:
                self.cli.display_error(f"Recording too short (minimum {config.MIN_RECORDING_TIME}s)")
                if not self.cli.confirm_action("try again"):
                    return False
                continue
                
            # Handle post-recording options
            while True:
                choice = self.cli.display_post_recording_options()
                
                if choice == 'p':
                    self.audio_recorder.play_recording(audio_data)
                elif choice == 'r':
                    break  # Re-record
                elif choice == 's':
                    self.file_manager.save_recording(audio_data, slide_number)
                    self.cli.display_success(f"Saved recording for slide {slide_number}")
                    return True
                    
            if choice == 'r':
                continue  # Re-record
                
        return False
        
    def revisit_recording(self, slide_number: int) -> None:
        """Handle revisiting an existing recording.
        
        Args:
            slide_number: The slide number to revisit.
        """
        while True:
            choice = self.cli.display_revisit_options()
            
            if choice == 'b':
                break
                
            elif choice == 'p':
                # Read the file and play it
                with open(config.get_recording_path(slide_number), 'rb') as f:
                    audio_data = f.read()
                self.audio_recorder.play_recording(audio_data)
                
            elif choice == 'r':
                # Make backup and re-record
                self.file_manager.backup_recording(slide_number)
                if self.record_slide(slide_number):
                    self.cli.display_success(f"Updated recording for slide {slide_number}")
                    break
                    
            elif choice == 'd':
                if self.cli.confirm_action("delete this recording"):
                    self.file_manager.delete_recording(slide_number)
                    self.cli.display_success(f"Deleted recording for slide {slide_number}")
                    break
                    
            self.cli.wait_for_key()
            
    def run(self):
        """Run the main application loop."""
        while True:
            choice = self.cli.display_main_menu()
            
            if choice == "1":  # Record Next Slide
                next_slide = self.file_manager.get_next_slide_number()
                self.record_slide(next_slide)
                
            elif choice == "2":  # Revisit Existing Recording
                recordings = self.file_manager.get_recording_list()
                if not recordings:
                    self.cli.display_error("No recordings found")
                    self.cli.wait_for_key()
                    continue
                    
                slide_number = self.cli.display_existing_recordings(
                    [config.FILENAME_PATTERN.format(n) for n in recordings]
                )
                
                if slide_number is not None and slide_number in recordings:
                    self.revisit_recording(slide_number)
                    
            elif choice == "3":  # Exit
                break
                
        self.cleanup()

def main(output_dir: Optional[str] = None, audio_quality: str = 'high',
         enable_keyboard_hooks: bool = True):
    """Main entry point for the application.
    
    Args:
        output_dir: Optional custom output directory for recordings
        audio_quality: Audio quality setting ('low', 'medium', 'high')
        enable_keyboard_hooks: Whether to enable keyboard hooks
    """
    app = SlideRecorder(output_dir, audio_quality, enable_keyboard_hooks)
    try:
        app.run()
    except Exception as e:
        print(f"\nError: {e}")
        app.cleanup()
        sys.exit(1)
    finally:
        app.cleanup() 