#!/usr/bin/env python3
"""
Main render script for Google Colab.
Supports preview (fast, low-res) and final (full quality) modes.
Implements chunked rendering for long videos.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
MANIFEST_PATH = PROJECT_ROOT / "manifest.json"
BEATS_PATH = PROJECT_ROOT / "beats.json"

sys.path.insert(0, str(SRC_DIR))


def run_cmd(cmd: list, check: bool = True, capture: bool = False, env: dict = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"[render] $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture, text=True, check=False, env=env or os.environ)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr and result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def load_manifest() -> Dict:
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)


def load_beats() -> Dict:
    with open(BEATS_PATH, "r") as f:
        return json.load(f)


def get_render_config(mode: str) -> Dict:
    """Get render configuration for mode."""
    manifest = load_manifest()
    return manifest.get("render", {}).get(mode, {})


def render_frames_python(
    from_sec: float,
    to_sec: float,
    fps: int,
    scale: float,
    out_dir: Path,
    seed: int = 42,
    target_scene: str = None,
    use_jpg: bool = False
) -> List[Path]:
    """Render frames using Python PIL renderer (src/render.py)."""
    cmd = [
        sys.executable, str(SRC_DIR / "render.py"),
        "--from", str(from_sec),
        "--to", str(to_sec),
        "--fps", str(fps),
        "--scale", str(scale),
        "--out", str(out_dir),
        "--seed", str(seed),
    ]
    if target_scene:
        cmd.extend(["--scene", target_scene])
    if use_jpg:
        cmd.append("--jpg")

    run_cmd(cmd)
    frames = sorted(out_dir.glob("frame_*.png")) + sorted(out_dir.glob("frame_*.jpg"))
    return frames


def render_frames_node(
    from_sec: float,
    to_sec: float,
    fps: int,
    scale: float,
    out_dir: Path,
    seed: int = 42,
    target_scene: str = None,
    use_jpg: bool = False
) -> List[Path]:
    """Render frames using Node.js renderer (src/render.js)."""
    cmd = [
        "node", str(SRC_DIR / "render.js"),
        "--from", str(from_sec),
        "--to", str(to_sec),
        "--fps", str(fps),
        "--scale", str(scale),
        "--out", str(out_dir),
        "--seed", str(seed),
    ]
    if target_scene:
        cmd.extend(["--scene", target_scene])
    if use_jpg:
        cmd.append("--jpg")

    run_cmd(cmd)
    frames = sorted(out_dir.glob("frame_*.png")) + sorted(out_dir.glob("frame_*.jpg"))
    return frames


def create_contact_sheet(frames_dir: Path, output_path: Path, cols: int = 6, thumb_width: int = 180):
    """Create a contact sheet from rendered frames."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[render] Pillow not available for contact sheet")
        return

    frame_files = sorted(frames_dir.glob("frame_*.png")) + sorted(frames_dir.glob("frame_*.jpg"))
    if not frame_files:
        return

    rows = (len(frame_files) + cols - 1) // cols
    thumb_height = int(thumb_width * 1920 / 1080)
    sheet_width = cols * thumb_width
    sheet_height = rows * (thumb_height + 30)

    sheet = Image.new("RGB", (sheet_width, sheet_height), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except Exception:
        font = ImageFont.load_default()

    for idx, frame_file in enumerate(frame_files):
        col = idx % cols
        row = idx // cols
        x = col * thumb_width
        y = row * (thumb_height + 30)

        try:
            frame_img = Image.open(frame_file)
            frame_img.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            sheet.paste(frame_img, (x, y))

            frame_num = int(frame_file.stem.split("_")[1])
            t = frame_num / 30.0
            draw.text((x + 2, y + thumb_height + 2), f"{t:.1f}s", font=font, fill=(200, 200, 200))
        except Exception as e:
            print(f"[contact-sheet] Failed to add {frame_file}: {e}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, "JPEG", quality=85)
    print(f"[contact-sheet] Saved to {output_path}")


def encode_video_ffmpeg(
    frames_dir: Path,
    output_path: Path,
    fps: int,
    crf: int = 18,
    preset: str = "slow",
    pix_fmt: str = "yuv420p",
    audio_path: Path = None,
    audio_codec: str = "aac",
    audio_bitrate: str = "192k",
    audio_sample_rate: int = 48000,
    loudnorm: Dict = None,
    start_number: int = 0
):
    """Encode frames to video using ffmpeg."""
    frame_pattern = frames_dir / "frame_%06d.png"
    if not (frames_dir / "frame_000000.png").exists():
        frame_pattern = frames_dir / "frame_%06d.jpg"

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-start_number", str(start_number),
        "-i", str(frame_pattern),
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-pix_fmt", pix_fmt,
        "-movflags", "+faststart",
    ]

    if audio_path and audio_path.exists():
        cmd.extend([
            "-i", str(audio_path),
            "-c:a", audio_codec,
            "-b:a", audio_bitrate,
            "-ar", str(audio_sample_rate),
        ])

        if loudnorm:
            af = f"loudnorm=I={loudnorm.get('I', -14)}:TP={loudnorm.get('TP', -1.5)}:LRA={loudnorm.get('LRA', 11)}:print_format=summary"
            cmd.extend(["-af", af])

    cmd.append(str(output_path))

    run_cmd(cmd)


def mix_audio_tracks(
    vo_path: Path,
    music_path: Path = None,
    sfx_paths: List[Path] = None,
    beats: Dict = None,
    output_path: Path = None,
    vo_gain_db: float = 0,
    music_gain_db: float = -15,
    sfx_gain_db: float = -6
) -> Path:
    """Mix VO, music, and SFX into a single audio track."""
    if output_path is None:
        output_path = PROJECT_ROOT / "cache" / "mixed_audio.wav"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    inputs = []
    filter_parts = []

    # VO (primary)
    inputs.extend(["-i", str(vo_path)])
    filter_parts.append(f"[0:a]volume={vo_gain_db}dB[vo]")

    input_idx = 1

    # Music
    if music_path and music_path.exists():
        inputs.extend(["-i", str(music_path)])
        filter_parts.append(f"[{input_idx}:a]volume={music_gain_db}dB,aloop=loop=-1:size=2e+09[music]")
        input_idx += 1

    # SFX
    sfx_filters = []
    if sfx_paths and beats:
        for i, beat in enumerate(beats.get("beats", [])):
            sfx_name = beat.get("sfx", [])
            if not sfx_name:
                continue
            for sfx in sfx_name:
                sfx_path = ASSETS_DIR / "sfx" / f"{sfx}.wav"
                if not sfx_path.exists():
                    continue
                inputs.extend(["-i", str(sfx_path)])
                delay_ms = int(beat["start"] * 1000)
                sfx_filters.append(f"[{input_idx}:a]volume={sfx_gain_db}dB,adelay={delay_ms}|{delay_ms}[sfx{i}]")
                input_idx += 1

    if sfx_filters:
        filter_parts.extend(sfx_filters)
        all_inputs = "[vo]"
        if music_path and music_path.exists():
            all_inputs += "[music]"
        for i in range(len(sfx_filters)):
            all_inputs += f"[sfx{i}]"
        filter_parts.append(f"{all_inputs}amix=inputs={1 + (1 if music_path else 0) + len(sfx_filters)}:duration=first:dropout_transition=0[mixed]")
        filter_complex = ";".join(filter_parts)
        cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[mixed]", str(output_path)]
    elif music_path and music_path.exists():
        filter_parts.append("[vo][music]amix=inputs=2:duration=first:dropout_transition=0[mixed]")
        filter_complex = ";".join(filter_parts)
        cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[mixed]", str(output_path)]
    else:
        # Just VO
        cmd = ["ffmpeg", "-y", "-i", str(vo_path), "-af", f"volume={vo_gain_db}dB", str(output_path)]

    run_cmd(cmd)
    return output_path


def render_chunk(
    chunk_id: int,
    from_sec: float,
    to_sec: float,
    config: Dict,
    work_dir: Path,
    seed: int = 42,
    target_scene: str = None
) -> Path:
    """Render a single chunk of the video."""
    chunk_dir = work_dir / f"chunk_{chunk_id:03d}"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    frames_dir = chunk_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[render] Rendering chunk {chunk_id}: {from_sec:.1f}s - {to_sec:.1f}s")

    # Render frames using Python renderer
    frames = render_frames_python(
        from_sec=from_sec,
        to_sec=to_sec,
        fps=config["fps"],
        scale=config["scale"],
        out_dir=frames_dir,
        seed=seed,
        target_scene=target_scene,
        use_jpg=False
    )

    if not frames:
        raise RuntimeError(f"No frames rendered for chunk {chunk_id}")

    # Encode chunk
    chunk_output = chunk_dir / f"chunk_{chunk_id:03d}.mp4"
    encode_video_ffmpeg(
        frames_dir=frames_dir,
        output_path=chunk_output,
        fps=config["fps"],
        crf=config.get("crf", 18),
        preset=config.get("preset", "slow"),
        pix_fmt=config.get("pix_fmt", "yuv420p")
    )

    print(f"[render] ✅ Chunk {chunk_id} complete: {chunk_output}")
    return chunk_output


def concatenate_chunks(chunk_files: List[Path], output_path: Path):
    """Concatenate video chunks using ffmpeg concat demuxer."""
    list_file = output_path.parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for chunk in chunk_files:
            f.write(f"file '{chunk.absolute()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]
    run_cmd(cmd)
    print(f"[render] ✅ Concatenated {len(chunk_files)} chunks to {output_path}")


def render_preview(
    from_sec: float = 0,
    to_sec: float = None,
    config: Dict = None,
    work_dir: Path = None,
    seed: int = 42
) -> Path:
    """Render a preview (contact sheet + low-res MP4)."""
    if config is None:
        config = get_render_config("preview")

    if to_sec is None:
        beats = load_beats()
        to_sec = beats.get("duration", 60)

    if work_dir is None:
        work_dir = PROJECT_ROOT / "renders" / "previews"
    work_dir.mkdir(parents=True, exist_ok=True)

    frames_dir = work_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[render] PREVIEW MODE: {from_sec}s - {to_sec}s")
    print(f"[render] Config: {config}")

    # Render frames
    frames = render_frames_python(
        from_sec=from_sec,
        to_sec=to_sec,
        fps=config["fps"],
        scale=config["scale"],
        out_dir=frames_dir,
        seed=seed,
        use_jpg=True
    )

    # Create contact sheet
    sheet_path = work_dir / f"sheet_{from_sec}-{to_sec}.jpg"
    create_contact_sheet(frames_dir, sheet_path)

    # Encode preview MP4
    preview_mp4 = work_dir / f"preview_{from_sec}-{to_sec}.mp4"
    encode_video_ffmpeg(
        frames_dir=frames_dir,
        output_path=preview_mp4,
        fps=config["fps"],
        crf=config.get("crf", 28),
        preset=config.get("preset", "veryfast"),
        pix_fmt=config.get("pix_fmt", "yuv420p")
    )

    print(f"\n[render] ✅ Preview complete:")
    print(f"  Contact sheet: {sheet_path}")
    print(f"  Preview MP4:   {preview_mp4}")
    return preview_mp4


def render_final(
    from_sec: float = 0,
    to_sec: float = None,
    config: Dict = None,
    work_dir: Path = None,
    output_dir: Path = None,
    seed: int = 42,
    chunked: bool = False,
    max_chunk_duration: int = 120
) -> Path:
    """Render final video (with optional chunking)."""
    if config is None:
        config = get_render_config("final")

    beats_data = load_beats()
    if to_sec is None:
        to_sec = beats_data.get("duration", 60)

    if work_dir is None:
        work_dir = PROJECT_ROOT / "cache" / "render_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    if output_dir is None:
        output_dir = PROJECT_ROOT / "renders" / "final"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine output filename
    version = 1
    while (output_dir / f"myproject_v{version}.mp4").exists():
        version += 1
    final_output = output_dir / f"myproject_v{version}.mp4"

    print(f"\n[render] FINAL MODE: {from_sec}s - {to_sec}s")
    print(f"[render] Config: {config}")
    print(f"[render] Output: {final_output}")

    duration = to_sec - from_sec

    if chunked and duration > max_chunk_duration:
        # Chunked rendering
        print(f"[render] Duration {duration:.1f}s > {max_chunk_duration}s, using chunked rendering")
        chunks = []
        chunk_start = from_sec
        chunk_id = 0

        while chunk_start < to_sec:
            chunk_end = min(chunk_start + max_chunk_duration, to_sec)
            chunk_file = render_chunk(
                chunk_id=chunk_id,
                from_sec=chunk_start,
                to_sec=chunk_end,
                config=config,
                work_dir=work_dir,
                seed=seed
            )
            chunks.append(chunk_file)
            chunk_start = chunk_end
            chunk_id += 1

        # Concatenate chunks (video only, audio mixed separately)
        print("[render] Concatenating video chunks...")
        video_only = work_dir / "video_only.mp4"
        concatenate_chunks(chunks, video_only)

        # Mix audio
        print("[render] Mixing audio...")
        vo_path = ASSETS_DIR / "vo" / "vo_final.mp3"
        music_path = ASSETS_DIR / "music" / "bed.mp3" if (ASSETS_DIR / "music" / "bed.mp3").exists() else None
        mixed_audio = mix_audio_tracks(
            vo_path=vo_path,
            music_path=music_path,
            beats=beats_data,
            output_path=work_dir / "mixed_audio.wav"
        )

        # Combine video + audio with loudnorm
        print("[render] Final mux with loudness normalization...")
        loudnorm = config.get("loudnorm", {"I": -14, "TP": -1.5, "LRA": 11})
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_only),
            "-i", str(mixed_audio),
            "-c:v", "copy",
            "-c:a", config.get("audio_codec", "aac"),
            "-b:a", config.get("audio_bitrate", "192k"),
            "-ar", str(config.get("audio_sample_rate", 48000)),
            "-af", f"loudnorm=I={loudnorm['I']}:TP={loudnorm['TP']}:LRA={loudnorm['LRA']}:print_format=summary",
            "-movflags", "+faststart",
            str(final_output)
        ]
        run_cmd(cmd)

    else:
        # Single-pass rendering
        frames_dir = work_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        frames = render_frames_python(
            from_sec=from_sec,
            to_sec=to_sec,
            fps=config["fps"],
            scale=config["scale"],
            out_dir=frames_dir,
            seed=seed
        )

        # Mix audio
        vo_path = ASSETS_DIR / "vo" / "vo_final.mp3"
        music_path = ASSETS_DIR / "music" / "bed.mp3" if (ASSETS_DIR / "music" / "bed.mp3").exists() else None
        mixed_audio = mix_audio_tracks(
            vo_path=vo_path,
            music_path=music_path,
            beats=beats_data,
            output_path=work_dir / "mixed_audio.wav"
        )

        # Encode with audio
        loudnorm = config.get("loudnorm", {"I": -14, "TP": -1.5, "LRA": 11})
        encode_video_ffmpeg(
            frames_dir=frames_dir,
            output_path=final_output,
            fps=config["fps"],
            crf=config.get("crf", 18),
            preset=config.get("preset", "slow"),
            pix_fmt=config.get("pix_fmt", "yuv420p"),
            audio_path=mixed_audio,
            audio_codec=config.get("audio_codec", "aac"),
            audio_bitrate=config.get("audio_bitrate", "192k"),
            audio_sample_rate=config.get("audio_sample_rate", 48000),
            loudnorm=loudnorm
        )

    # Verify output
    result = run_cmd(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(final_output)], check=False, capture=True)
    if result.returncode == 0:
        actual_duration = float(result.stdout.strip())
        print(f"\n[render] ✅ Final render complete!")
        print(f"  Output: {final_output}")
        print(f"  Duration: {actual_duration:.2f}s (expected: {duration:.2f}s)")
    else:
        print(f"\n[render] ✅ Final render complete: {final_output}")

    # Copy to Google Drive if mounted
    drive_output_dir = Path("/content/drive/MyDrive/myproject/renders/final")
    if drive_output_dir.exists():
        drive_output = drive_output_dir / final_output.name
        shutil.copy2(final_output, drive_output)
        print(f"[render] 📁 Copied to Google Drive: {drive_output}")

    return final_output


def main():
    parser = argparse.ArgumentParser(description="Colab render script for Motion Video Director")
    parser.add_argument("--mode", choices=["preview", "final"], required=True, help="Render mode")
    parser.add_argument("--from", type=float, default=0, dest="from_sec", help="Start time in seconds")
    parser.add_argument("--to", type=float, default=None, dest="to_sec", help="End time in seconds")
    parser.add_argument("--fps", type=int, default=None, help="Override FPS")
    parser.add_argument("--scale", type=float, default=None, help="Override scale")
    parser.add_argument("--out", type=str, default=None, help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--scene", type=str, default=None, help="Render specific scene only")
    parser.add_argument("--chunked", action="store_true", help="Enable chunked rendering for long videos")
    parser.add_argument("--max-chunk-duration", type=int, default=120, help="Max chunk duration in seconds")
    parser.add_argument("--contact-sheet", action="store_true", help="Generate contact sheet (preview mode)")

    args = parser.parse_args()

    # Load config
    config = get_render_config(args.mode)
    if args.fps:
        config["fps"] = args.fps
    if args.scale:
        config["scale"] = args.scale

    work_dir = PROJECT_ROOT / "cache" / "render_work"
    output_dir = Path(args.out) if args.out else None

    if args.mode == "preview":
        render_preview(
            from_sec=args.from_sec,
            to_sec=args.to_sec,
            config=config,
            work_dir=work_dir,
            seed=args.seed
        )
    else:
        render_final(
            from_sec=args.from_sec,
            to_sec=args.to_sec,
            config=config,
            work_dir=work_dir,
            output_dir=output_dir,
            seed=args.seed,
            chunked=args.chunked,
            max_chunk_duration=args.max_chunk_duration
        )


if __name__ == "__main__":
    main()