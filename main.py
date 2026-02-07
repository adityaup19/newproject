#!/usr/bin/env python3
"""
Instagram Reels Generator
─────────────────────────
Takes a text prompt + style template and produces a vertical 9:16 MP4
with voiceover and stock background video.

Usage:
    python main.py "Your script text here" --style brainrot
    python main.py "Your script text here" --style deep_rizz --tts elevenlabs
"""

import argparse
import sys
import time
from pathlib import Path

from config import AUDIO_DIR, OUTPUT_DIR, get_style
from voice import generate_voice
from video import render_reel


def generate_reel(
    text: str,
    style_name: str,
    tts_provider: str | None = None,
) -> Path:
    """
    End-to-end reel generation pipeline.

    Args:
        text:         The script / narration text.
        style_name:   One of the keys in config.STYLE_TEMPLATES.
        tts_provider: Override for TTS backend ("openai" or "elevenlabs").

    Returns:
        Path to the rendered MP4 in the output/ directory.
    """
    style = get_style(style_name)
    timestamp = int(time.time())

    # ── 1. Voice ─────────────────────────────────────────────────────────
    print(f"[1/3] Generating voiceover ({tts_provider or 'default'})...")
    audio_path = generate_voice(
        text=text,
        style=style,
        provider=tts_provider,
        output_path=AUDIO_DIR / f"{timestamp}.mp3",
    )
    print(f"       Audio saved → {audio_path}")

    # ── 2. Pick background video + Render ─────────────────────────────────
    output_path = OUTPUT_DIR / f"{timestamp}.mp4"
    print("[2/3] Combining with background video...")
    render_reel(
        audio_path=audio_path,
        style_name=style_name,
        output_path=output_path,
    )

    # ── 3. Done ──────────────────────────────────────────────────────────
    print(f"[3/3] Saving final reel to output/...")
    print(f"       Reel saved → {output_path}")
    return output_path


# ── CLI ──────────────────────────────────────────────────────────────────────

def cli() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an Instagram Reel from a text prompt.",
    )
    parser.add_argument("text", help="The narration / script text.")
    parser.add_argument(
        "--style", "-s",
        default="brainrot",
        help="Style template name (default: brainrot).",
    )
    parser.add_argument(
        "--tts", "-t",
        default=None,
        choices=["openai", "elevenlabs"],
        help="TTS provider override (default: uses TTS_PROVIDER env var).",
    )
    args = parser.parse_args()

    try:
        output = generate_reel(args.text, args.style, args.tts)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone! Output file: {output}")


if __name__ == "__main__":
    cli()
