"""
Configuration settings for the Slide Audio Recorder application.
"""

import os
from pathlib import Path

# Audio settings
SAMPLE_RATE = 44100  # Standard CD quality
CHANNELS = 1  # Mono recording
CHUNK_SIZE = 1024  # Smaller chunks for more responsive handling
FORMAT = 'mp3'  # Output format
BITRATE = '192k'  # High quality MP3 encoding

# Performance settings
BUFFER_SIZE = 262144  # 256KB buffer for better I/O performance
USE_MEMORY_BUFFER = True  # Use memory buffering for temp files

# Voice Activity Detection settings
SILENCE_THRESHOLD = 300  # RMS threshold for silence detection (adjusted for typical voice levels)
SILENCE_DURATION = 3.0  # Seconds of silence before stopping
MIN_VOICE_DURATION = 1.0  # Minimum duration of voice activity required

# File settings
DEFAULT_OUTPUT_DIR = Path('recordings')
FILENAME_PATTERN = 'slide_{:03d}.mp3'  # Pattern for slide recordings (e.g., slide_001.mp3)

# Keyboard controls
STOP_KEY = 'space'  # Key to stop recording
SAVE_KEY = 's'  # Save recording
RERECORD_KEY = 'r'  # Discard and re-record
PLAYBACK_KEY = 'p'  # Play current recording
BACK_KEY = 'b'  # Return to previous menu
DELETE_KEY = 'd'  # Delete recording (in revisit mode)

# Audio device settings
DEFAULT_INPUT_DEVICE = None  # Will be set to system default

# Application settings
DEBUG = True  # Enable debug logging
MAX_RECORDING_TIME = 300  # Maximum recording time in seconds (5 minutes)
MIN_RECORDING_TIME = 1  # Minimum recording time in seconds

def init():
    """Initialize configuration and create necessary directories."""
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

def get_recording_path(slide_number: int) -> Path:
    """Get the full path for a slide recording file.
    
    Args:
        slide_number: The slide number to generate the path for.
        
    Returns:
        Path object for the recording file.
    """
    filename = FILENAME_PATTERN.format(slide_number)
    return DEFAULT_OUTPUT_DIR / filename

def get_next_slide_number() -> int:
    """Get the next available slide number.
    
    Returns:
        The next available slide number.
    """
    existing_files = list(DEFAULT_OUTPUT_DIR.glob('slide_*.mp3'))
    if not existing_files:
        return 1
        
    numbers = [int(f.stem.split('_')[1]) for f in existing_files]
    return max(numbers) + 1 