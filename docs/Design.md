# Slide Audio Recorder - Design Document

## Project Overview
A command-line tool for recording audio narration for presentation slides. The tool provides a simple interface to record, manage, and review audio files for individual slides.

## Technical Requirements
- **Platform**: Apple M3 Ultra (ARM64 architecture)
- **Python Version**: 3.9+
- **Environment**: Virtual environment (venv)
- **Audio Format**: MP3 output files
- **Memory**: Optimized for high-memory systems (512GB available)

## Project Structure
```
slide-recorder/
├── venv/                          # Virtual environment
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point and CLI interface
│   ├── audio_recorder.py          # Audio recording logic
│   ├── file_manager.py            # File operations and naming
│   ├── cli_interface.py           # User interface and menu system
│   └── config.py                  # Configuration and settings
├── recordings/                    # Default output directory
├── requirements.txt
├── README.md
├── setup.py                       # Optional: for package installation
└── run_recorder.py                # Main executable script
```

## Core Components

### 1. Main Application (main.py)
- **Purpose**: Entry point and application orchestration
- **Responsibilities**:
  - Initialize application settings
  - Handle command-line arguments (output directory)
  - Coordinate between different modules
  - Main application loop

### 2. Audio Recorder (audio_recorder.py)
- **Purpose**: Handle all audio recording functionality
- **Responsibilities**:
  - Initialize microphone input
  - Start/stop recording on keyboard input
  - Real-time audio capture and buffering
  - Convert recorded audio to MP3 format
  - Handle audio device selection and configuration

### 3. File Manager (file_manager.py)
- **Purpose**: Manage file operations and naming conventions
- **Responsibilities**:
  - Generate sequential filenames (slide_001.mp3, slide_002.mp3)
  - Handle file saving and overwriting
  - Directory management and validation
  - File existence checking for revisiting recordings

### 4. CLI Interface (cli_interface.py)
- **Purpose**: User interaction and menu system
- **Responsibilities**:
  - Display main menu options
  - Handle user input and navigation
  - Show recording status and feedback
  - Manage post-recording options (Save, Rerecord, Playback)
  - Display available slides for revisiting

### 5. Configuration (config.py)
- **Purpose**: Application settings and constants
- **Responsibilities**:
  - Default output directory settings
  - Audio quality/format settings
  - Keyboard shortcuts configuration
  - File naming patterns

## User Flow

### Main Menu Options
1. **Record Next Slide**
   - Automatically determine next slide number
   - Start recording immediately
   - Wait for stop key press
   - Present post-recording options

2. **Revisit Existing Recording**
   - Display list of existing recordings
   - Allow selection by slide number
   - Load existing recording for playback/rerecording

3. **Exit Application**
   - Clean shutdown of audio resources
   - Save any configuration changes

### Recording Workflow
1. User selects "Record Next Slide"
2. System displays "Recording slide_XXX... Press [SPACEBAR] to stop"
3. Audio recording begins immediately
4. User speaks their narration
5. User presses designated key to stop recording
6. System presents options: [S]ave, [R]erecord, [P]layback
7. Based on selection:
   - Save: Write MP3 file and return to main menu
   - Rerecord: Discard current recording and start over
   - Playback: Play current recording, then show options again

### Revisit Workflow
1. User selects "Revisit Existing Recording"
2. System displays numbered list of existing recordings
3. User enters slide number or 'back' to return
4. System loads existing recording
5. Present options: [P]layback, [R]erecord, [D]elete, [B]ack
6. Handle selected action

## Technical Specifications

### Recommended Libraries (requirements.txt)
```
pyaudio==0.2.11          # Audio input/output
pydub==0.25.1            # Audio processing and MP3 conversion
keyboard==0.13.5         # Keyboard event handling
click==8.1.7             # CLI framework and argument parsing
colorama==0.4.6          # Cross-platform colored terminal output
rich==13.7.0             # Rich text and progress indicators
```

### Audio Configuration
- **Sample Rate**: 44100 Hz (CD quality)
- **Channels**: Mono (1 channel) for voice recording
- **Bit Depth**: 16-bit
- **Format**: MP3 with 128 kbps bitrate (configurable)
- **Chunk Size**: 1024 frames for low latency

### Keyboard Controls
- **Stop Recording**: Spacebar (configurable)
- **Menu Navigation**: Number keys + Enter
- **Quick Actions**: Single letter shortcuts (S, R, P, etc.)

## Error Handling

### Audio Device Issues
- Detect available microphones on startup
- Graceful fallback to system default
- Clear error messages for device problems

### File System Issues
- Validate output directory permissions
- Handle disk space limitations
- Prevent overwriting without confirmation

### User Input Validation
- Validate slide numbers for revisiting
- Handle invalid menu selections
- Provide clear feedback for all actions

## Performance Considerations

### Memory Management
- Use streaming audio processing to minimize RAM usage
- Implement proper cleanup of audio resources
- Buffer management for real-time recording

### M3 Ultra Optimizations
- Utilize ARM64 optimized audio libraries
- Take advantage of high memory for audio buffering
- Efficient MP3 encoding using available cores

## Configuration Options

### Command Line Arguments
```bash
python run_recorder.py --output-dir /path/to/recordings --audio-quality high
```

### Runtime Configuration
- Microphone selection
- Audio quality settings
- Keyboard shortcut customization
- File naming pattern modification

## Installation and Setup

### Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### First Run
```bash
python run_recorder.py
```

## Future Enhancements (Optional)
- Waveform visualization during recording
- Audio level monitoring
- Batch export functionality
- Integration with presentation software
- Cloud storage integration
- Audio editing capabilities (trim, normalize)

## Testing Strategy
- Unit tests for each module
- Integration tests for audio recording pipeline
- Manual testing on M3 Ultra hardware
- Error condition testing (no microphone, full disk, etc.)

## Security Considerations
- Microphone permission handling
- File system access permissions
- Safe handling of audio data in memory
- Secure temporary file management