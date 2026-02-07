"""
Streamlit UI for the Instagram Reels Generator.

Run with:
    streamlit run app.py
"""

import streamlit as st
from pathlib import Path

from config import STYLE_TEMPLATES
from main import generate_reel

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Reels Generator",
    page_icon="🎬",
    layout="centered",
)

st.title("Instagram Reels Generator")
st.caption("Turn any text into a vertical video reel with voiceover and subtitles.")

# ── Sidebar controls ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")

    style_name = st.selectbox(
        "Style template",
        options=list(STYLE_TEMPLATES.keys()),
        format_func=lambda s: f"{s}  —  {STYLE_TEMPLATES[s]['description']}",
    )

    tts_provider = st.radio(
        "TTS engine",
        options=["openai", "elevenlabs"],
        horizontal=True,
    )

    st.divider()
    st.markdown(
        "**Setup checklist**\n"
        "- Set `OPENAI_API_KEY` or `ELEVENLABS_API_KEY` env var\n"
        "- Drop stock `.mp4` clips into `video/<style>/`\n"
        "- Install FFmpeg on your system"
    )

# ── Main input area ──────────────────────────────────────────────────────────
text = st.text_area(
    "Your script / caption / quote",
    placeholder="e.g. Ohio is the most sigma state, no cap on a stack fr fr",
    height=150,
)

generate_btn = st.button("Generate Reel", type="primary", use_container_width=True)

# ── Generation pipeline ─────────────────────────────────────────────────────
if generate_btn:
    if not text.strip():
        st.warning("Please enter some text before generating.")
    else:
        try:
            with st.spinner("Generating your reel — this may take a minute..."):
                output_path: Path = generate_reel(
                    text=text.strip(),
                    style_name=style_name,
                    tts_provider=tts_provider,
                )

            st.success(f"Reel generated successfully!")

            # ── Video preview ────────────────────────────────────────────
            video_bytes = output_path.read_bytes()
            st.video(video_bytes, format="video/mp4")

            # ── Download button ──────────────────────────────────────────
            st.download_button(
                label="Download MP4",
                data=video_bytes,
                file_name=output_path.name,
                mime="video/mp4",
                use_container_width=True,
            )

        except FileNotFoundError as exc:
            st.error(str(exc))
            st.info(
                "Make sure you have stock video clips in the "
                f"`video/{style_name}/` folder."
            )
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
