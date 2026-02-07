"""
Subtitle generation module.

Splits the narration text into timed SRT segments aligned to the audio
duration.  Two strategies are available:

  1. Whisper-based (default when OpenAI key is set):
     Transcribes the generated audio with word-level timestamps for
     accurate subtitle timing.

  2. Estimate-based (fallback):
     Splits text into short chunks and distributes them evenly across
     the audio duration.
"""

import re
from pathlib import Path

import config


def generate_subtitles(
    text: str,
    audio_path: Path,
    output_path: Path,
    use_whisper: bool | None = None,
) -> Path:
    """
    Create an SRT subtitle file for *text* aligned to *audio_path*.

    When *use_whisper* is None the function auto-detects: it uses Whisper
    if an OpenAI API key is configured, otherwise falls back to estimation.
    """
    if use_whisper is None:
        use_whisper = bool(config.OPENAI_API_KEY)

    if use_whisper:
        return _generate_with_whisper(audio_path, output_path)
    else:
        return _generate_estimated(text, audio_path, output_path)


# ── Whisper-based subtitles ──────────────────────────────────────────────────

def _generate_with_whisper(audio_path: Path, output_path: Path) -> Path:
    """Transcribe audio with Whisper and write word-level SRT."""
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    segments = transcript.segments or []
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for idx, seg in enumerate(segments, start=1):
        start = _format_srt_time(seg["start"])
        end = _format_srt_time(seg["end"])
        lines.append(f"{idx}")
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"].strip())
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


# ── Estimation-based subtitles ───────────────────────────────────────────────

def _generate_estimated(
    text: str,
    audio_path: Path,
    output_path: Path,
    max_words_per_chunk: int = 6,
) -> Path:
    """
    Split *text* into short chunks and space them evenly across the audio
    duration.  Good enough for styles where exact lip-sync isn't critical.
    """
    from video import get_audio_duration

    duration = get_audio_duration(audio_path)
    chunks = _split_text(text, max_words_per_chunk)

    if not chunks:
        output_path.write_text("", encoding="utf-8")
        return output_path

    chunk_dur = duration / len(chunks)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for idx, chunk in enumerate(chunks):
        start = idx * chunk_dur
        end = start + chunk_dur
        lines.append(f"{idx + 1}")
        lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        lines.append(chunk)
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


# ── Helpers ──────────────────────────────────────────────────────────────────

def _split_text(text: str, max_words: int = 6) -> list[str]:
    """
    Split text into chunks of at most *max_words* words, preferring to
    break at sentence boundaries when possible.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks: list[str] = []

    for sentence in sentences:
        words = sentence.split()
        while words:
            chunk = words[:max_words]
            chunks.append(" ".join(chunk))
            words = words[max_words:]

    return chunks


def _format_srt_time(seconds: float) -> str:
    """Convert a float of seconds to SRT timestamp format HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"
