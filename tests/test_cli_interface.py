"""
Tests for the CLI interface module.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.cli_interface import CLIInterface
from rich.console import Console
from rich.prompt import Prompt

class MockConfig:
    """Mock configuration for testing."""
    def __init__(self):
        self.STOP_KEY = 'space'
        self.SAVE_KEY = 's'
        self.RERECORD_KEY = 'r'
        self.PLAYBACK_KEY = 'p'
        self.BACK_KEY = 'b'
        self.DELETE_KEY = 'd'

class TestCLIInterface(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = MockConfig()
        
        # Patch keyboard module
        self.keyboard_patcher = patch('keyboard.on_press_key')
        self.mock_keyboard = self.keyboard_patcher.start()
        
        # Patch keyboard.read_event
        self.read_event_patcher = patch('keyboard.read_event')
        self.mock_read_event = self.read_event_patcher.start()
        
        # Create CLI interface with mocked console
        self.cli = CLIInterface(self.config)
        self.cli.console = MagicMock(spec=Console)
        
    def tearDown(self):
        """Clean up after each test method."""
        self.keyboard_patcher.stop()
        self.read_event_patcher.stop()
        
    def test_init(self):
        """Test initialization of CLIInterface."""
        self.assertFalse(self.cli.recording)
        self.mock_keyboard.assert_called_once_with(
            self.config.STOP_KEY,
            self.cli._stop_recording_callback
        )
        
    @patch.object(Prompt, 'ask')
    def test_display_main_menu(self, mock_ask):
        """Test main menu display and selection."""
        # Test each valid option
        for option in ['1', '2', '3']:
            mock_ask.return_value = option
            result = self.cli.display_main_menu()
            self.assertEqual(result, option)
            
        # Verify console interactions
        self.cli.console.clear.assert_called()
        self.cli.console.print.assert_called()
        
    def test_display_recording_status(self):
        """Test recording status display."""
        # Mock console.status to simulate recording
        mock_status = MagicMock()
        self.cli.console.status.return_value.__enter__.return_value = mock_status
        
        # Mock the status context manager to stop recording when entered
        def stop_after_delay(*args, **kwargs):
            self.cli.recording = False
            return mock_status
            
        self.cli.console.status.return_value.__enter__.side_effect = stop_after_delay
        
        # Run the recording status display
        self.cli.display_recording_status(1)
        
        # Verify console interactions
        self.cli.console.status.assert_called_once()
        status_message = self.cli.console.status.call_args[0][0]
        self.assertIn("Recording slide_001", status_message)
        self.assertIn(self.config.STOP_KEY, status_message)
        self.assertFalse(self.cli.recording)
        
    @patch.object(Prompt, 'ask')
    def test_display_post_recording_options(self, mock_ask):
        """Test post-recording options display."""
        # Test each valid option
        for option in ['s', 'r', 'p']:
            mock_ask.return_value = option
            result = self.cli.display_post_recording_options()
            self.assertEqual(result, option)
            
        # Verify console interactions
        self.cli.console.print.assert_called()
        
    @patch.object(Prompt, 'ask')
    def test_display_existing_recordings_empty(self, mock_ask):
        """Test display of empty recordings list."""
        result = self.cli.display_existing_recordings([])
        self.assertIsNone(result)
        self.cli.console.print.assert_called_with("[yellow]No existing recordings found.[/yellow]")
        
    @patch.object(Prompt, 'ask')
    def test_display_existing_recordings_with_data(self, mock_ask):
        """Test display of recordings list with data."""
        recordings = ["slide_001.mp3", "slide_002.mp3"]
        
        # Test valid selection
        mock_ask.return_value = "1"
        result = self.cli.display_existing_recordings(recordings)
        self.assertEqual(result, 1)
        
        # Test back option
        mock_ask.return_value = "back"
        result = self.cli.display_existing_recordings(recordings)
        self.assertIsNone(result)
        
        # Test invalid input
        mock_ask.return_value = "invalid"
        result = self.cli.display_existing_recordings(recordings)
        self.assertIsNone(result)
        
    @patch.object(Prompt, 'ask')
    def test_display_revisit_options(self, mock_ask):
        """Test revisit options display."""
        # Test each valid option
        for option in ['p', 'r', 'd', 'b']:
            mock_ask.return_value = option
            result = self.cli.display_revisit_options()
            self.assertEqual(result, option)
            
        # Verify console interactions
        self.cli.console.print.assert_called()
        
    def test_display_error(self):
        """Test error message display."""
        error_msg = "Test error"
        self.cli.display_error(error_msg)
        self.cli.console.print.assert_called_with(f"[red]Error: {error_msg}[/red]")
        
    def test_display_success(self):
        """Test success message display."""
        success_msg = "Test success"
        self.cli.display_success(success_msg)
        self.cli.console.print.assert_called_with(f"[green]{success_msg}[/green]")
        
    @patch.object(Prompt, 'ask')
    def test_confirm_action(self, mock_ask):
        """Test action confirmation."""
        # Test confirmation
        mock_ask.return_value = "y"
        self.assertTrue(self.cli.confirm_action("test action"))
        
        # Test rejection
        mock_ask.return_value = "n"
        self.assertFalse(self.cli.confirm_action("test action"))
        
    @patch('keyboard.read_event')
    def test_wait_for_key(self, mock_read_event):
        """Test waiting for key press."""
        self.cli.wait_for_key()
        self.cli.console.print.assert_called_with("\nPress any key to continue...")
        mock_read_event.assert_called_once_with(suppress=True)
        
    def test_stop_recording_callback(self):
        """Test stop recording callback."""
        # Test when recording
        self.cli.recording = True
        self.cli._stop_recording_callback(None)
        self.assertFalse(self.cli.recording)
        
        # Test when not recording
        self.cli.recording = False
        self.cli._stop_recording_callback(None)
        self.assertFalse(self.cli.recording)

if __name__ == '__main__':
    unittest.main() 