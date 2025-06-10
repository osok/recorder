#!/usr/bin/env python3
"""
Slide Audio Recorder - Main executable script
"""

import click
from src.main import main

@click.command()
@click.option('--output-dir', default='recordings',
              help='Directory where recordings will be saved')
@click.option('--audio-quality', default='high',
              type=click.Choice(['low', 'medium', 'high']),
              help='Audio recording quality')
@click.option('--debug', is_flag=True, default=False,
              help='Run in debug mode with minimal keyboard hooks')
def run(output_dir: str, audio_quality: str, debug: bool):
    """Start the Slide Audio Recorder application."""
    main(output_dir=output_dir, audio_quality=audio_quality, enable_keyboard_hooks=not debug)

if __name__ == '__main__':
    run() 