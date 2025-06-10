"""
CLI interface for the Slide Audio Recorder.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
import keyboard
from typing import Optional
import sys
import tty
import termios

class CLIInterface:
    def __init__(self, config, enable_keyboard_hooks=True):
        """Initialize the CLI interface.
        
        Args:
            config: Application configuration
            enable_keyboard_hooks: Whether to enable keyboard hooks (for testing)
        """
        self.config = config
        self.console = Console()
        self.recording = False
        self.waiting_for_start = False
        if enable_keyboard_hooks:
            self._setup_keyboard_hooks()

    def _setup_keyboard_hooks(self):
        """Set up keyboard event hooks for recording control."""
        keyboard.on_press_key(self.config.STOP_KEY, self._space_key_callback)

    def _space_key_callback(self, _):
        """Callback for space key press."""
        if self.waiting_for_start:
            self.waiting_for_start = False
            self.start_pressed = True
        elif self.recording:
            self.recording = False
            # Print processing message immediately using rich console
            self.console.print("\n[bold yellow]Processing recording... please wait[/bold yellow]")

    def _getch(self):
        """Read a single character from stdin."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def display_main_menu(self) -> str:
        """Display the main menu and return the user's selection."""
        self.console.clear()
        menu_panel = Panel(
            "[bold cyan]Slide Audio Recorder[/bold cyan]\n\n"
            "[green]Press SPACE to start recording next slide[/green]\n"
            "2. [yellow]Revisit Existing Recording[/yellow]\n"
            "3. [red]Exit Application[/red]",
            title="Main Menu",
            box=box.ROUNDED
        )
        self.console.print(menu_panel)
        
        while True:
            event = keyboard.read_event()
            if event.event_type == 'down':
                if event.name == 'space':
                    return "1"
                elif event.name in ['2', '3']:
                    return event.name

    def display_recording_status(self, slide_number: int):
        """Display the current recording status."""
        self.recording = True  # Reset recording state
        self.console.print(f"\n[bold green]Recording slide_{slide_number:03d}... Press {self.config.STOP_KEY} to stop[/bold green]")

    def display_post_recording_options(self) -> str:
        """Display options after recording and return user's choice."""
        self.console.print("\n[green]Recording processed successfully![/green]\n")
        options_panel = Panel(
            "[S]ave    [R]erecord    [P]layback",
            title="Post Recording Options",
            box=box.ROUNDED
        )
        self.console.print(options_panel)
        
        valid_keys = {'s', 'r', 'p'}
        while True:
            ch = self._getch().lower()
            if ch in valid_keys:
                return ch

    def display_existing_recordings(self, recordings: list[str]) -> Optional[int]:
        """Display list of existing recordings and return selected slide number."""
        if not recordings:
            self.console.print("[yellow]No existing recordings found.[/yellow]")
            return None

        table = Table(title="Existing Recordings", box=box.ROUNDED)
        table.add_column("Slide #", style="cyan")
        table.add_column("Filename", style="green")
        
        for recording in recordings:
            slide_num = recording.split("_")[1].split(".")[0]
            table.add_row(slide_num, recording)
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "Enter slide number to select (or 'back' to return)",
            default="back"
        )
        
        if choice.lower() == "back":
            return None
            
        try:
            return int(choice)
        except ValueError:
            self.console.print("[red]Invalid slide number.[/red]")
            return None

    def display_revisit_options(self) -> str:
        """Display options for revisiting a recording."""
        options_panel = Panel(
            "[P]layback    [R]erecord    [D]elete    [B]ack",
            title="Revisit Options",
            box=box.ROUNDED
        )
        self.console.print(options_panel)
        
        valid_keys = {'p', 'r', 'd', 'b'}
        while True:
            ch = self._getch().lower()
            if ch in valid_keys:
                return ch

    def display_error(self, message: str):
        """Display an error message."""
        self.console.print(f"\n[bold red]Error: {message}[/bold red]")

    def display_success(self, message: str):
        """Display a success message."""
        self.console.print(f"\n[bold green]{message}[/bold green]")

    def confirm_action(self, action: str) -> bool:
        """Ask for confirmation of an action."""
        return Prompt.ask(
            f"Do you want to {action}?",
            choices=["y", "n"],
            default="n"
        ).lower() == "y"

    def wait_for_key(self):
        """Wait for any key press."""
        self.console.print("\nPress any key to continue...")
        self._getch() 