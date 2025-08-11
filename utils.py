import os
import subprocess
import tempfile
from typing import List, Dict

import whisper
from moviepy.editor import VideoFileClip


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