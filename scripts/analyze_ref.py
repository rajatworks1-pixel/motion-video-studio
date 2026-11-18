#!/usr/bin/env python3
"""
Reference video analysis script.
Analyzes a reference video for format, cuts, colors, audio, etc.
Run on Android (TermFold) or Colab.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent


def run_cmd(cmd: list, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=capture, text=True, check=False)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def probe_video(video_path: Path) -> Dict:
    """Get video info using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path)
    ]
    result = run_cmd(cmd, capture=True)
    return json.loads(result.stdout)


def extract_frames(video_path: Path, output_dir: Path, fps: float = 4, max_frames: int = 100):
    """Extract frames at specified FPS."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        "-vframes", str(max_frames),
        str(output_dir / "frame_%04d.jpg")
    ]
    run_cmd(cmd, check=False)
    return sorted(output_dir.glob("frame_*.jpg"))


def extract_audio(video_path: Path, output_path: Path):
    """Extract audio track as WAV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn", "-ac", "2", "-ar", "44100",
        str(output_path)
    ]
    run_cmd(cmd, check=False)
    return output_path


def detect_scenes(video_path: Path, threshold: float = 0.3) -> List[Dict]:
    """Detect scene cuts using ffmpeg scene detection."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-filter:v", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-"
    ]
    result = run_cmd(cmd, check=False, capture=True)

    cuts = []
    for line in result.stderr.split("\n"):
        if "pts_time:" in line:
            try:
                parts = line.split("pts_time:")
                time_str = parts[1].split()[0]
                cuts.append(float(time_str))
            except Exception:
                pass
    return [{"time": t, "type": "cut"} for t in cuts]


def analyze_color_palette(frames_dir: Path, num_colors: int = 8) -> List[str]:
    """Extract dominant colors from frames."""
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return []

    all_pixels = []
    for frame_file in frames_dir.glob("*.jpg"):
        try:
            img = Image.open(frame_file)
            img = img.resize((100, 100))
            pixels = np.array(img).reshape(-1, 3)
            all_pixels.append(pixels)
        except Exception:
            pass

    if not all_pixels:
        return []

    all_pixels = np.vstack(all_pixels)
    # Simple k-means-like quantization
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(all_pixels)
    colors = kmeans.cluster_centers_.astype(int)

    hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in colors]
    return hex_colors


def transcribe_audio(audio_path: Path) -> Dict:
    """Transcribe audio with word timestamps using faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("[analyze] faster-whisper not installed")
        return {}

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio_path), word_timestamps=True)

    words = []
    for segment in segments:
        for word in segment.words:
            words.append({
                "word": word.word,
                "start": word.start,
                "end": word.end,
                "confidence": word.probability
            })

    return {
        "language": info.language,
        "duration": info.duration,
        "words": words,
        "full_text": " ".join([w["word"] for w in words])
    }


def separate_stems(audio_path: Path, output_dir: Path) -> Dict[str, Path]:
    """Separate audio stems using Demucs."""
    try:
        import demucs.separate
    except ImportError:
        print("[analyze] Demucs not installed")
        return {}

    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "demucs",
        "-n", "htdemucs",
        "--two-stems=vocals",
        "-o", str(output_dir),
        str(audio_path)
    ]
    run_cmd(cmd, check=False)

    stems_dir = output_dir / "htdemucs" / audio_path.stem
    return {
        "vocals": stems_dir / "vocals.wav",
        "no_vocals": stems_dir / "no_vocals.wav"
    }


def generate_report(video_path: Path, output_dir: Path) -> Dict:
    """Generate complete analysis report."""
    print(f"[analyze] Analyzing: {video_path.name}")

    # Probe video
    probe = probe_video(video_path)
    video_stream = next((s for s in probe["streams"] if s["codec_type"] == "video"), {})
    audio_stream = next((s for s in probe["streams"] if s["codec_type"] == "audio"), {})

    format_info = probe.get("format", {})
    duration = float(format_info.get("duration", 0))
    width = video_stream.get("width", 0)
    height = video_stream.get("height", 0)
    fps_str = video_stream.get("r_frame_rate", "0/1")
    fps = eval(fps_str) if "/" in fps_str else float(fps_str)

    print(f"  Format: {width}x{height} @ {fps:.2f}fps, {duration:.1f}s")

    # Extract frames
    frames_dir = output_dir / "frames"
    frames = extract_frames(video_path, frames_dir, fps=4, max_frames=60)

    # Detect cuts
    cuts = detect_scenes(video_path)
    print(f"  Cuts detected: {len(cuts)}")

    # Color palette
    colors = analyze_color_palette(frames_dir)
    print(f"  Dominant colors: {colors}")

    # Audio analysis
    audio_path = output_dir / "audio.wav"
    extract_audio(video_path, audio_path)

    transcript = transcribe_audio(audio_path)
    print(f"  Transcript: {transcript.get('full_text', '')[:100]}...")

    # Stem separation
    stems_dir = output_dir / "stems"
    stems = separate_stems(audio_path, stems_dir)

    report = {
        "video": {
            "path": str(video_path),
            "duration": duration,
            "width": width,
            "height": height,
            "fps": fps,
            "aspect": f"{width}:{height}",
            "codec": video_stream.get("codec_name"),
            "format": format_info.get("format_name"),
        },
        "cuts": cuts,
        "colors": colors,
        "audio": {
            "duration": transcript.get("duration"),
            "language": transcript.get("language"),
            "transcript": transcript.get("full_text"),
            "words": transcript.get("words", []),
            "stems": {k: str(v) for k, v in stems.items() if v.exists()}
        },
        "frames": [str(f) for f in frames]
    }

    report_path = output_dir / "analysis_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"[analyze] Report saved to {report_path}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Analyze reference video")
    parser.add_argument("video", type=str, help="Path to reference video")
    parser.add_argument("--output", type=str, default="cache/ref_analysis", help="Output directory")
    parser.add_argument("--max-duration", type=float, default=15, help="Max duration to analyze (seconds)")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"[analyze] Video not found: {video_path}")
        sys.exit(1)

    output_dir = PROJECT_ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    # Trim video if longer than max_duration
    probe = probe_video(video_path)
    duration = float(probe["format"].get("duration", 0))
    if duration > args.max_duration:
        trimmed_path = output_dir / f"trimmed_{video_path.name}"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-t", str(args.max_duration),
            "-c", "copy",
            str(trimmed_path)
        ]
        run_cmd(cmd, check=False)
        video_path = trimmed_path
        print(f"[analyze] Trimmed to {args.max_duration}s: {trimmed_path}")

    report = generate_report(video_path, output_dir)

    print("\n[analyze] Summary:")
    print(f"  Resolution: {report['video']['width']}x{report['video']['height']}")
    print(f"  Duration: {report['video']['duration']:.1f}s")
    print(f"  FPS: {report['video']['fps']:.2f}")
    print(f"  Cuts: {len(report['cuts'])}")
    print(f"  Colors: {report['colors'][:5]}")
    print(f"  Language: {report['audio']['language']}")
    print(f"  Stems: {list(report['audio']['stems'].keys())}")


if __name__ == "__main__":
    main()