"""
Configuration and style templates for Instagram Reels generator.
"""

import os
from pathlib import Path

# ── Directories ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
VIDEO_DIR = BASE_DIR / "video"
OUTPUT_DIR = BASE_DIR / "output"

# ── TTS provider: "openai" or "elevenlabs" ───────────────────────────────────
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "openai")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_TTS_MODEL = "tts-1"

# ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# ── FFmpeg ───────────────────────────────────────────────────────────────────
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "ffprobe")

# Output dimensions (9:16 vertical)
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920

# ── Style Templates ─────────────────────────────────────────────────────────
# Each template defines voice settings and subtitle styling.
# Add stock .mp4 files to video/<style_name>/ for background footage.
STYLE_TEMPLATES = {
    "brainrot": {
        "description": "Fast-paced, chaotic, meme-heavy narration",
        "openai_voice": "onyx",
        "openai_speed": 1.15,
        "elevenlabs_voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam
        "elevenlabs_stability": 0.3,
        "elevenlabs_similarity": 0.8,
        "subtitle_font_size": 64,
        "subtitle_color": "&H00FFFFFF",     # white (ASS BGR)
        "subtitle_outline_color": "&H00000000",
        "subtitle_outline_width": 4,
        "subtitle_position": "center",
    },
    "deep_rizz": {
        "description": "Smooth, confident, low-pitched motivational tone",
        "openai_voice": "echo",
        "openai_speed": 0.92,
        "elevenlabs_voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold
        "elevenlabs_stability": 0.6,
        "elevenlabs_similarity": 0.75,
        "subtitle_font_size": 58,
        "subtitle_color": "&H0000FFFF",     # yellow
        "subtitle_outline_color": "&H00000000",
        "subtitle_outline_width": 3,
        "subtitle_position": "center",
    },
    "fake_podcast": {
        "description": "Casual, conversational, two-host energy (single voice)",
        "openai_voice": "fable",
        "openai_speed": 1.0,
        "elevenlabs_voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella
        "elevenlabs_stability": 0.5,
        "elevenlabs_similarity": 0.7,
        "subtitle_font_size": 52,
        "subtitle_color": "&H00FFFFFF",
        "subtitle_outline_color": "&H00000000",
        "subtitle_outline_width": 3,
        "subtitle_position": "bottom",
    },
}


def get_style(name: str) -> dict:
    """Return a style template by name, raising ValueError if unknown."""
    if name not in STYLE_TEMPLATES:
        available = ", ".join(STYLE_TEMPLATES)
        raise ValueError(f"Unknown style '{name}'. Available: {available}")
    return STYLE_TEMPLATES[name]
