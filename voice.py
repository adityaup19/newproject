"""
Voice generation module.

Supports two backends:
  - OpenAI TTS  (default)
  - ElevenLabs

The backend is chosen via config.TTS_PROVIDER or overridden per-call.
"""

from pathlib import Path

import config


def generate_voice(
    text: str,
    style: dict,
    output_path: Path,
    provider: str | None = None,
) -> Path:
    """
    Synthesise speech from *text* using the selected TTS provider and
    style-specific voice settings.  Writes an MP3 to *output_path*.

    Returns the resolved output path.
    """
    provider = provider or config.TTS_PROVIDER

    if provider == "openai":
        return _generate_openai(text, style, output_path)
    elif provider == "elevenlabs":
        return _generate_elevenlabs(text, style, output_path)
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")


# ── OpenAI TTS ───────────────────────────────────────────────────────────────

def _generate_openai(text: str, style: dict, output_path: Path) -> Path:
    """Generate speech via the OpenAI TTS API."""
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = client.audio.speech.create(
        model=config.OPENAI_TTS_MODEL,
        voice=style["openai_voice"],
        speed=style.get("openai_speed", 1.0),
        input=text,
        response_format="mp3",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    response.stream_to_file(str(output_path))
    return output_path


# ── ElevenLabs ───────────────────────────────────────────────────────────────

def _generate_elevenlabs(text: str, style: dict, output_path: Path) -> Path:
    """Generate speech via the ElevenLabs API."""
    import requests

    voice_id = style["elevenlabs_voice_id"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": style.get("elevenlabs_stability", 0.5),
            "similarity_boost": style.get("elevenlabs_similarity", 0.75),
        },
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(resp.content)
    return output_path
