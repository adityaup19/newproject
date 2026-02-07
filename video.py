"""
Video rendering module.

Picks a random stock background clip from video/<style>/, then uses FFmpeg to:
  1. Scale / crop the clip to 9:16 (1080×1920).
  2. Loop or trim the clip to match the audio duration.
  3. Mix in the voiceover audio.
  4. Burn in SRT subtitles with style-specific formatting.
  5. Output the final MP4.
"""

import json
import random
import subprocess
from pathlib import Path

import config


def get_audio_duration(audio_path: Path) -> float:
    """Return the duration of an audio file in seconds via ffprobe."""
    cmd = [
        config.FFPROBE_BIN,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def pick_background_video(style_name: str) -> Path:
    """
    Select a random .mp4 from video/<style_name>/.
    Raises FileNotFoundError if no clips are available.
    """
    style_dir = config.VIDEO_DIR / style_name
    clips = list(style_dir.glob("*.mp4"))
    if not clips:
        raise FileNotFoundError(
            f"No .mp4 files found in {style_dir}. "
            f"Add stock footage for the '{style_name}' style."
        )
    return random.choice(clips)


def _subtitle_filter(subtitle_path: Path, style: dict) -> str:
    """
    Build the FFmpeg subtitles filter string with style-specific formatting.
    """
    # Escape colons and backslashes in the path for the filtergraph
    escaped = str(subtitle_path).replace("\\", "\\\\").replace(":", "\\:")

    font_size = style.get("subtitle_font_size", 56)
    color = style.get("subtitle_color", "&H00FFFFFF")
    outline_color = style.get("subtitle_outline_color", "&H00000000")
    outline_width = style.get("subtitle_outline_width", 3)

    position = style.get("subtitle_position", "center")
    if position == "bottom":
        alignment = 2   # ASS: bottom-center
        margin_v = 80
    else:
        alignment = 5   # ASS: middle-center
        margin_v = 0

    force_style = (
        f"FontSize={font_size},"
        f"PrimaryColour={color},"
        f"OutlineColour={outline_color},"
        f"Outline={outline_width},"
        f"Alignment={alignment},"
        f"MarginV={margin_v},"
        f"FontName=Arial,"
        f"Bold=1"
    )

    return f"subtitles={escaped}:force_style='{force_style}'"


def render_reel(
    audio_path: Path,
    subtitle_path: Path,
    style_name: str,
    style: dict,
    output_path: Path,
) -> Path:
    """
    Compose the final 9:16 reel and write it to *output_path*.

    Steps:
      - Pick a background clip for the style.
      - Scale+crop to 1080×1920, looping if shorter than the audio.
      - Overlay voiceover audio.
      - Burn in subtitles.
    """
    bg_video = pick_background_video(style_name)
    duration = get_audio_duration(audio_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Video filter: scale to fill 1080×1920 then center-crop
    vf_scale_crop = (
        f"scale={config.OUTPUT_WIDTH}:{config.OUTPUT_HEIGHT}:"
        f"force_original_aspect_ratio=increase,"
        f"crop={config.OUTPUT_WIDTH}:{config.OUTPUT_HEIGHT}"
    )

    sub_filter = _subtitle_filter(subtitle_path, style)
    vf = f"{vf_scale_crop},{sub_filter}"

    cmd = [
        config.FFMPEG_BIN,
        "-y",
        # Loop the background video so it covers the full audio duration
        "-stream_loop", "-1",
        "-i", str(bg_video),
        "-i", str(audio_path),
        # End when the audio track ends
        "-t", str(duration),
        "-filter_complex",
        f"[0:v]{vf}[vout]",
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-r", "30",
        str(output_path),
    ]

    subprocess.run(cmd, check=True)
    return output_path
