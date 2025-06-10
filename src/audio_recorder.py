"""
Audio recording functionality for the Slide Audio Recorder.
"""

import io
import time
import wave
from typing import Optional, Tuple
import atexit
import os
import sys
from pydub import AudioSegment

import pyaudio

from . import config

class AudioRecorder:
    def __init__(self):
        """Initialize the audio recorder."""
        print("Initializing audio recorder...")  # Debug
        self.pyaudio = None
        self.stream = None
        self.frames = []
        self.recording = False
        self.start_time = 0
        self._is_cleaning_up = False
        self._initialize_pyaudio()
        atexit.register(self.cleanup)
        
    def _initialize_pyaudio(self):
        """Initialize or reinitialize PyAudio."""
        try:
            if self.stream:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.pyaudio:
                self.pyaudio.terminate()
            
            self.pyaudio = pyaudio.PyAudio()
        except Exception as e:
            print(f"Error initializing PyAudio: {e}", file=sys.stderr)
            self.pyaudio = None
            raise
        
    def start_recording(self) -> None:
        """Start recording audio."""
        if self.recording:
            return
            
        try:
            print("Starting recording...")  # Debug
            self._initialize_pyaudio()
            
            self.frames = []
            self.stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=config.CHANNELS,
                rate=config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=config.CHUNK_SIZE,
                stream_callback=None  # Ensure blocking mode
            )
            
            self.recording = True
            self.start_time = time.time()
            print("Recording started successfully")  # Debug
            
        except Exception as e:
            print(f"Error starting recording: {e}", file=sys.stderr)
            self.cleanup()
            raise
        
    def stop_recording(self) -> Tuple[bytes, float]:
        """Stop recording audio.
        
        Returns:
            Tuple containing:
            - The recorded audio data as WAV bytes
            - Duration of the recording in seconds
        """
        if not self.recording:
            return b'', 0.0
            
        try:
            print("Stopping recording...")  # Debug
            self.recording = False
            duration = time.time() - self.start_time
            
            print(f"Recorded {len(self.frames)} frames")  # Debug
            
            if self.stream:
                print("Stopping stream...")  # Debug
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                print("Stream closed")  # Debug
                
            print("Converting to WAV...")  # Debug
            # Convert directly to WAV format in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(config.CHANNELS)
                wav_file.setsampwidth(self.pyaudio.get_sample_size(pyaudio.paInt16))
                wav_file.setframerate(config.SAMPLE_RATE)
                wav_file.writeframes(b''.join(self.frames))
            
            print("WAV conversion complete")  # Debug
            return wav_buffer.getvalue(), duration
            
        except Exception as e:
            print(f"Error stopping recording: {e}", file=sys.stderr)
            return b'', 0.0
        finally:
            self._cleanup_stream()
            
    def convert_to_mp3(self, wav_data: bytes) -> bytes:
        """Convert WAV data to MP3 format.
        
        Args:
            wav_data: WAV audio data
            
        Returns:
            MP3 audio data
        """
        try:
            print("Converting to MP3...")  # Debug
            # Convert WAV to MP3 using pydub
            wav_buffer = io.BytesIO(wav_data)
            audio = AudioSegment.from_wav(wav_buffer)
            
            # Create buffer for MP3 data
            mp3_buffer = io.BytesIO()
            
            # Export with high quality settings
            audio.export(
                mp3_buffer,
                format="mp3",
                bitrate=config.BITRATE,
                parameters=[
                    "-codec:a", "libmp3lame",
                    "-qscale:a", "2",  # High quality setting
                    "-threads", "4"  # Use multiple threads for encoding
                ]
            )
            print("MP3 conversion complete")  # Debug
            return mp3_buffer.getvalue()
            
        except Exception as e:
            print(f"Error converting to MP3: {e}", file=sys.stderr)
            return wav_data  # Fallback to WAV data if conversion fails
            
    def play_recording(self, audio_data: bytes) -> None:
        """Play back a recording.
        
        Args:
            audio_data: The WAV audio data to play.
        """
        try:
            self._initialize_pyaudio()
            
            # Create a new stream for playback
            wav_buffer = io.BytesIO(audio_data)
            with wave.open(wav_buffer, 'rb') as wav_file:
                # Create an output stream
                stream = self.pyaudio.open(
                    format=self.pyaudio.get_format_from_width(wav_file.getsampwidth()),
                    channels=wav_file.getnchannels(),
                    rate=wav_file.getframerate(),
                    output=True
                )
                
                # Read and play the audio in chunks
                chunk_size = config.CHUNK_SIZE * wav_file.getnchannels()
                data = wav_file.readframes(chunk_size)
                while data:
                    stream.write(data)
                    data = wav_file.readframes(chunk_size)
                    
                # Clean up
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            print(f"Error playing recording: {e}", file=sys.stderr)
        finally:
            self._cleanup_stream()
        
    def record_chunk(self) -> bool:
        """Record a single chunk of audio data.
        
        Returns:
            True if recording should continue, False if max time exceeded.
        """
        if not self.recording or not self.stream:
            return False
            
        try:
            data = self.stream.read(config.CHUNK_SIZE, exception_on_overflow=False)
            self.frames.append(data)
            
            # Check if we've exceeded maximum recording time
            duration = time.time() - self.start_time
            return duration <= config.MAX_RECORDING_TIME
            
        except Exception as e:
            print(f"Error recording audio chunk: {e}", file=sys.stderr)
            self.cleanup()
            return False
            
    def _cleanup_stream(self):
        """Clean up just the audio stream."""
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            finally:
                self.stream = None
            
    def cleanup(self):
        """Clean up audio resources."""
        if self._is_cleaning_up:
            return
            
        self._is_cleaning_up = True
        try:
            self._cleanup_stream()
            if self.pyaudio:
                self.pyaudio.terminate()
                print("PyAudio terminated")  # Debug
                self.pyaudio = None
        except Exception as e:
            print(f"Error during cleanup: {e}", file=sys.stderr)
        finally:
            self._is_cleaning_up = False
            
    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()
        
    def get_input_devices(self) -> list:
        """Get a list of available input devices.
        
        Returns:
            List of (device_index, device_name) tuples.
        """
        devices = []
        for i in range(self.pyaudio.get_device_count()):
            device_info = self.pyaudio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append((i, device_info['name']))
        return devices
        
    def set_input_device(self, device_index: int) -> bool:
        """Set the input device to use for recording.
        
        Args:
            device_index: The index of the device to use.
            
        Returns:
            True if device was set successfully, False otherwise.
        """
        try:
            device_info = self.pyaudio.get_device_info_by_index(device_index)
            if device_info['maxInputChannels'] > 0:
                config.DEFAULT_INPUT_DEVICE = device_index
                return True
        except Exception:
            pass
        return False 