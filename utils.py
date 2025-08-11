import os
import subprocess
import tempfile
from typing import List, Dict

import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


def extract_audio(video_path: str, audio_output_path: str | None = None) -> str:
    """Extract the audio track from *video_path* to *audio_output_path* (wav, pcm_s16le)."""
    if audio_output_path is None:
        fd, audio_output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_output_path, codec="pcm_s16le")
    clip.close()
    return audio_output_path


def transcribe_audio(video_path: str, model_size: str = "base") -> List[Dict]:
    """Transcribe *video_path* with OpenAI Whisper and return segments."""
    model = whisper.load_model(model_size)
    audio_path = extract_audio(video_path)
    result = model.transcribe(audio_path)
    # cleanup temporary audio
    if audio_path.startswith(tempfile.gettempdir()):
        try:
            os.remove(audio_path)
        except OSError:
            pass
    return result["segments"]


def _format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(segments: List[Dict], srt_path: str) -> str:
    """Write *segments* to *srt_path* in SRT format and return the path."""
    with open(srt_path, "w", encoding="utf-8") as fp:
        for idx, seg in enumerate(segments, start=1):
            start = _format_timestamp(seg["start"])
            end = _format_timestamp(seg["end"])
            text = seg["text"].strip()
            fp.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
    return srt_path


def burn_subtitles(video_path: str, srt_path: str, output_path: str) -> None:
    """Use ffmpeg to burn the subtitles at *srt_path* into *video_path*, saving to *output_path*."""
    # ffmpeg expects backslashes and colons in Windows paths to be escaped inside the subtitles filter.
    # Since we pass arguments as a list (no shell), we do not need surrounding quotes.
    filter_path = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i", video_path,
        "-vf", f"subtitles={filter_path}",
        "-c:a", "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True)


# --- Stylized subtitle rendering -------------------------------------------------

def render_subtitles_moviepy(video_path: str, segments: List[Dict], output_path: str, *, style: dict | None = None) -> None:
    """Render styled subtitles with MoviePy directly on the video.

    Basic behaviour:
    • Uses a default style (white text, black stroke).
    • Words TYPED IN ALL CAPS are highlighted with *highlight_color*.
    • Simple fade-in / fade-out at segment boundaries.

    Feel free to tweak *style* dict to change font, colours, etc.
    """
    if style is None:
        style = {
            "font": "Arial-Bold",
            "fontsize": 60,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 2,
            "position": ("center", "bottom"),  # (x, y)
            "highlight_color": "yellow",
        }

    video = VideoFileClip(video_path)
    text_clips = []

    for seg in segments:
        # Highlight ALL-CAPS words
        words = [
            f"<font color='{style['highlight_color']}'>{w}</font>" if w.isupper() else w
            for w in seg["text"].strip().split()
        ]
        styled_text = " ".join(words)

        # Try with Pillow backend first to avoid ImageMagick dependency
        try:
            txt_clip = TextClip(
                styled_text,
                font=style["font"],
                fontsize=style["fontsize"],
                color=style["color"],
                stroke_color=style["stroke_color"],
                stroke_width=style["stroke_width"],
                method="pillow",
                size=(int(video.w * 0.9), None),  # wrap to 90% video width
            )
        except Exception:
            # Pillow backend not available in some MoviePy versions – fallback to caption (needs ImageMagick)
            print("⚠️ Pillow backend failed, falling back to ImageMagick. Make sure ImageMagick is installed and in PATH.")
            txt_clip = TextClip(
                styled_text,
                font=style["font"],
                fontsize=style["fontsize"],
                color=style["color"],
                stroke_color=style["stroke_color"],
                stroke_width=style["stroke_width"],
                method="caption",
                size=(int(video.w * 0.9), None),
            )

        txt_clip = (
            txt_clip.set_position(style["position"])
            .set_start(seg["start"])
            .set_end(seg["end"])
            .crossfadein(0.15)
            .crossfadeout(0.15)
        )
        text_clips.append(txt_clip)

    composite = CompositeVideoClip([video, *text_clips])
    composite.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Cleanup
    composite.close()
    video.close() 