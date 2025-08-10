import argparse
import os
import sys

from utils import transcribe_audio, generate_srt, burn_subtitles


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(PROJECT_DIR, "input_videos")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output_videos")
SUB_DIR = os.path.join(PROJECT_DIR, "subtitles")

# Ensure default folders exist
for _dir in (INPUT_DIR, OUTPUT_DIR, SUB_DIR):
    os.makedirs(_dir, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate dynamic subtitles for short videos using OpenAI Whisper and ffmpeg."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the input video (e.g. input_videos/my_clip.mp4)",
    )
    parser.add_argument(
        "--model",
        default="base",
        help="Whisper model size (tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--no-burn",
        action="store_true",
        help="Only generate the .srt file without burning subtitles into the video",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    video_path = args.file

    if not os.path.isfile(video_path):
        sys.exit(f"❌ File not found: {video_path}")

    video_stem = os.path.splitext(os.path.basename(video_path))[0]
    srt_path = os.path.join(SUB_DIR, f"{video_stem}.srt")

    print("🔊 Transcribing audio with Whisper... (this may take a while)")
    segments = transcribe_audio(video_path, model_size=args.model)
    generate_srt(segments, srt_path)
    print(f"✅ Transcript saved to {srt_path}")

    if args.no_burn:
        print("⚠️ Skipping subtitle burn-in as per --no-burn flag.")
        return

    output_path = os.path.join(OUTPUT_DIR, f"{video_stem}_subtitled.mp4")
    print("🎬 Burning subtitles into video...")
    burn_subtitles(video_path, srt_path, output_path)
    print(f"🚀 Done! Subtitled video saved to {output_path}")


if __name__ == "__main__":
    main() 