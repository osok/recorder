"""
Tests for the audio recording module.
"""

import io
import time
import unittest
from unittest.mock import MagicMock, patch
from src.audio_recorder import AudioRecorder
from src import config
import pyaudio

class MockPyAudio:
    def __init__(self):
        self.format = None
        self.channels = None
        self.rate = None
        self.input = None
        self.frames_per_buffer = None
        self.stream = MagicMock()
        self._device_count = 2
        self._devices = [
            {'maxInputChannels': 2, 'name': 'Test Device 1'},
            {'maxInputChannels': 0, 'name': 'Test Device 2'},
            {'maxInputChannels': 1, 'name': 'Test Device 3'}
        ]
        
    def open(self, format=None, channels=None, rate=None, input=None, 
             frames_per_buffer=None, output=None):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.input = input
        self.frames_per_buffer = frames_per_buffer
        return self.stream
        
    def get_sample_size(self, format):
        return 2
        
    def get_format_from_width(self, width):
        return pyaudio.paInt16
        
    def get_device_count(self):
        return len(self._devices)
        
    def get_device_info_by_index(self, index):
        return self._devices[index]
        
    def terminate(self):
        pass

class TestAudioRecorder(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_pyaudio = MockPyAudio()
        self.patcher = patch('pyaudio.PyAudio', return_value=self.mock_pyaudio)
        self.patcher.start()
        self.recorder = AudioRecorder()
        
    def tearDown(self):
        """Clean up after each test method."""
        self.patcher.stop()
        
    def test_init(self):
        """Test initialization of AudioRecorder."""
        self.assertIsNone(self.recorder.stream)
        self.assertEqual(self.recorder.frames, [])
        self.assertFalse(self.recorder.recording)
        self.assertEqual(self.recorder.start_time, 0)
        
    def test_start_recording(self):
        """Test starting a recording."""
        self.recorder.start_recording()
        
        # Verify stream was opened with correct parameters
        self.assertTrue(self.recorder.recording)
        self.assertGreater(self.recorder.start_time, 0)
        self.assertEqual(self.mock_pyaudio.channels, config.CHANNELS)
        self.assertEqual(self.mock_pyaudio.rate, config.SAMPLE_RATE)
        self.assertEqual(self.mock_pyaudio.frames_per_buffer, config.CHUNK_SIZE)
        self.assertTrue(self.mock_pyaudio.input)
        
    def test_stop_recording_when_not_recording(self):
        """Test stopping when no recording is in progress."""
        data, duration = self.recorder.stop_recording()
        self.assertEqual(data, b'')
        self.assertEqual(duration, 0.0)
        
    @patch('pydub.AudioSegment.from_wav')
    def test_stop_recording(self, mock_from_wav):
        """Test stopping a recording."""
        # Setup mock audio segment
        mock_audio = MagicMock()
        mock_buffer = io.BytesIO()
        mock_buffer.write(b'test mp3 data')
        mock_buffer.seek(0)  # Reset position to start
        
        def mock_export(output, format, bitrate):
            output.write(mock_buffer.getvalue())
            return output
            
        mock_audio.export.side_effect = mock_export
        mock_from_wav.return_value = mock_audio
        
        # Start and stop recording with actual test audio data
        self.recorder.start_recording()
        self.recorder.frames = [b'test audio data' * 100]  # Add sufficient test data
        self.recorder.start_time = time.time() - 1.0  # Set a specific duration
        data, duration = self.recorder.stop_recording()
        
        # Verify recording stopped and data was processed
        self.assertFalse(self.recorder.recording)
        self.assertIsNone(self.recorder.stream)
        self.assertAlmostEqual(duration, 1.0, delta=0.1)
        self.assertEqual(data, b'test mp3 data')
        
        # Verify the mock was called correctly
        mock_from_wav.assert_called_once()
        mock_audio.export.assert_called_once()
        
        # Verify the WAV data was written correctly
        wav_data = mock_from_wav.call_args[0][0].getvalue()
        self.assertIn(b'test audio data', wav_data)
        
    def test_record_chunk(self):
        """Test recording a single chunk."""
        # Setup mock stream to return test data
        self.mock_pyaudio.stream.read.return_value = b'test chunk data'
        
        # Start recording and record a chunk
        self.recorder.start_recording()
        result = self.recorder.record_chunk()
        
        # Verify chunk was recorded
        self.assertTrue(result)
        self.assertEqual(len(self.recorder.frames), 1)
        self.assertEqual(self.recorder.frames[0], b'test chunk data')
        
    def test_record_chunk_max_time_exceeded(self):
        """Test recording chunk when max time exceeded."""
        self.recorder.start_recording()
        self.recorder.start_time = time.time() - (config.MAX_RECORDING_TIME + 1)
        
        result = self.recorder.record_chunk()
        self.assertFalse(result)
        
    def test_record_chunk_error(self):
        """Test recording chunk with error."""
        self.mock_pyaudio.stream.read.side_effect = Exception("Test error")
        
        self.recorder.start_recording()
        result = self.recorder.record_chunk()
        self.assertFalse(result)
        
    @patch('pydub.AudioSegment.from_mp3')
    def test_play_recording(self, mock_from_mp3):
        """Test playing a recording."""
        # Setup mock audio segment with specific test data
        test_audio_data = b'test audio data' * 100
        mock_audio = MagicMock()
        mock_audio.channels = config.CHANNELS
        mock_audio.frame_rate = config.SAMPLE_RATE
        mock_audio.sample_width = 2
        mock_audio.raw_data = test_audio_data
        mock_from_mp3.return_value = mock_audio
        
        # Create a mock stream for verification
        mock_stream = MagicMock()
        self.mock_pyaudio.stream = mock_stream
        
        # Play test recording
        test_mp3_data = b'test mp3 data'
        self.recorder.play_recording(test_mp3_data)
        
        # Verify playback setup - compare BytesIO contents
        call_args = mock_from_mp3.call_args[0][0]
        self.assertIsInstance(call_args, io.BytesIO)
        self.assertEqual(call_args.getvalue(), test_mp3_data)
        
        # Verify stream operations
        self.assertTrue(mock_stream.write.called)
        self.assertTrue(mock_stream.stop_stream.called)
        self.assertTrue(mock_stream.close.called)
        
        # Verify the audio data was written correctly
        write_calls = mock_stream.write.call_args_list
        written_data = b''.join(call.args[0] for call in write_calls)
        self.assertEqual(written_data, test_audio_data)
        
    def test_get_input_devices(self):
        """Test getting list of input devices."""
        devices = self.recorder.get_input_devices()
        
        # Should only get devices with input channels
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0], (0, 'Test Device 1'))
        self.assertEqual(devices[1], (2, 'Test Device 3'))
        
    def test_set_input_device_valid(self):
        """Test setting valid input device."""
        result = self.recorder.set_input_device(0)
        self.assertTrue(result)
        self.assertEqual(config.DEFAULT_INPUT_DEVICE, 0)
        
    def test_set_input_device_invalid(self):
        """Test setting invalid input device."""
        # Test device with no input channels
        result = self.recorder.set_input_device(1)
        self.assertFalse(result)
        
        # Test non-existent device
        result = self.recorder.set_input_device(99)
        self.assertFalse(result)
        
    def test_cleanup(self):
        """Test cleanup of audio resources."""
        self.recorder.start_recording()
        self.recorder.cleanup()
        
        self.assertTrue(self.mock_pyaudio.stream.close.called)

 