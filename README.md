# Slide Audio Recorder

A command-line tool for recording audio narration for presentation slides. This tool provides a simple interface to record, manage, and review audio files for individual slides.

## Features

- Record audio narration for slides with automatic file naming
- Review and re-record existing slide narrations
- High-quality audio recording with MP3 output
- Simple command-line interface with keyboard shortcuts
- Optimized for Apple M3 Ultra systems

## Requirements

- Python 3.9 or higher
- macOS (optimized for Apple Silicon)
- 512GB available memory (optimized for high-memory systems)
- Audio input device (microphone)
- PortAudio (required for audio recording)
- ffmpeg (required for audio processing)

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd slide-recorder
   ```

2. Install system dependencies:
   ```bash
   # On macOS using Homebrew
   brew install portaudio ffmpeg

   # On Linux (Ubuntu/Debian)
   sudo apt-get install portaudio19-dev ffmpeg
   ```

3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

4. Install Python dependencies:
   ```bash
   # Upgrade pip to latest version
   pip install --upgrade pip

   # Install dependencies
   pip install -r requirements.txt
   ```

   If you encounter any issues with PyAudio installation:
   - Make sure PortAudio is installed first
   - On macOS, you might need to install PyAudio using:
     ```bash
     pip install --global-option='build_ext' --global-option='-I/opt/homebrew/include' --global-option='-L/opt/homebrew/lib' pyaudio
     ```

## Usage

1. Start the recorder:
   ```bash
   python run_recorder.py
   ```

2. Optional command-line arguments:
   ```bash
   python run_recorder.py --output-dir /path/to/recordings --audio-quality high
   ```

### Basic Controls

- Press SPACEBAR to stop recording
- Use number keys for menu navigation
- Single letter shortcuts for quick actions:
  - [S] Save recording
  - [R] Re-record
  - [P] Playback
  - [D] Delete (in revisit mode)
  - [B] Back to main menu

## Project Structure

```
slide-recorder/
├── venv/                  # Virtual environment
├── src/                   # Source code
├── recordings/           # Default output directory
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Configuration

The application can be configured through command-line arguments or by modifying the settings in `src/config.py`.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 