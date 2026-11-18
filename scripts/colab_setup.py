#!/usr/bin/env python3
"""
Colab environment setup script.
Installs dependencies, downloads models, mounts Google Drive.
Run this first in the Colab notebook.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def run_cmd(cmd: list, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"[setup] $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture, text=True, check=False)
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def check_gpu() -> bool:
    """Check if GPU is available."""
    try:
        result = run_cmd(["nvidia-smi"], check=False, capture=True)
        return result.returncode == 0
    except Exception:
        return False


def install_python_deps():
    """Install Python dependencies from requirements.txt."""
    req_file = PROJECT_ROOT / "scripts" / "requirements.txt"
    if not req_file.exists():
        print("[setup] No requirements.txt found")
        return

    print("[setup] Installing Python dependencies...")
    run_cmd([sys.executable, "-m", "pip", "install", "-r", str(req_file), "-q"])

    # Install Playwright browsers
    print("[setup] Installing Playwright Chromium...")
    run_cmd([sys.executable, "-m", "playwright", "install", "chromium"], check=False)


def install_system_deps():
    """Install system dependencies via apt."""
    print("[setup] Updating apt and installing system deps...")
    run_cmd(["apt-get", "update", "-qq"])
    run_cmd(["apt-get", "install", "-y", "-qq", "ffmpeg", "fonts-dejavu", "libglib2.0-0", "libnss3", "libnspr4",
             "libdbus-1-3", "libatk1.0-0", "libatk-bridge2.0-0", "libcups2", "libdrm2", "libxkbcommon0",
             "libxcomposite1", "libxdamage1", "libxfixes3", "libxrandr2", "libgbm1", "libasound2"])


def download_models():
    """Pre-download ML models to cache."""
    print("[setup] Pre-downloading models...")

    # faster-whisper small model
    try:
        from faster_whisper import WhisperModel
        print("[setup] Downloading faster-whisper small model...")
        model = WhisperModel("small", device="cpu", compute_type="int8")
        print("[setup] ✅ faster-whisper model cached")
    except Exception as e:
        print(f"[setup] faster-whisper download failed: {e}")

    # Demucs htdemucs model
    try:
        import demucs
        from demucs.pretrained import get_model
        print("[setup] Downloading Demucs htdemucs model...")
        model = get_model("htdemucs")
        print("[setup] ✅ Demucs model cached")
    except Exception as e:
        print(f"[setup] Demucs download failed: {e}")


def mount_google_drive(drive_folder: str = "MyDrive/myproject") -> Path:
    """Mount Google Drive and return the project folder path."""
    print("[setup] Mounting Google Drive...")
    try:
        from google.colab import drive
        drive.mount("/content/drive", force_remount=True)
        drive_path = Path("/content/drive") / drive_folder
        drive_path.mkdir(parents=True, exist_ok=True)
        print(f"[setup] ✅ Google Drive mounted at {drive_path}")
        return drive_path
    except Exception as e:
        print(f"[setup] Failed to mount Google Drive: {e}")
        return None


def setup_project_symlink(drive_path: Path):
    """Create symlink from /content/project to Drive folder."""
    content_project = Path("/content/project")
    if content_project.exists() or content_project.is_symlink():
        content_project.unlink()
    content_project.symlink_to(drive_path)
    print(f"[setup] ✅ Symlink created: /content/project -> {drive_path}")


def clone_or_sync_repo(repo_url: str, target_dir: Path):
    """Clone or pull the GitHub repository."""
    if (target_dir / ".git").exists():
        print("[setup] Repository exists, pulling latest...")
        run_cmd(["git", "-C", str(target_dir), "pull"], check=False)
    else:
        print(f"[setup] Cloning repository from {repo_url}...")
        run_cmd(["git", "clone", repo_url, str(target_dir)], check=False)


def verify_environment():
    """Verify the environment is ready."""
    print("\n[setup] Environment Verification:")

    # Python
    print(f"  Python: {sys.version.split()[0]}")

    # PyTorch
    try:
        import torch
        print(f"  PyTorch: {torch.__version__} | CUDA: {torch.cuda.is_available()} | Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    except Exception:
        print("  PyTorch: Not installed")

    # Playwright
    try:
        import playwright
        print(f"  Playwright: {playwright.__version__}")
    except Exception:
        print("  Playwright: Not installed")

    # ffmpeg
    result = run_cmd(["ffmpeg", "-version"], check=False, capture=True)
    if result.returncode == 0:
        version_line = result.stdout.split("\n")[0]
        print(f"  ffmpeg: {version_line}")
    else:
        print("  ffmpeg: Not found")

    # Fonts
    font_dir = PROJECT_ROOT / "assets" / "fonts"
    fonts = list(font_dir.glob("*.woff2")) + list(font_dir.glob("*.ttf"))
    print(f"  Fonts: {len(fonts)} found in assets/fonts/")

    # Manifest
    manifest_path = PROJECT_ROOT / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        asset_count = sum(len(v) if isinstance(v, list) else 1 for v in manifest.get("assets", {}).values())
        print(f"  Manifest: {asset_count} assets registered")
    else:
        print("  Manifest: Not found")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Colab environment setup")
    parser.add_argument("--repo", type=str, help="GitHub repository URL (e.g., https://github.com/user/repo.git)")
    parser.add_argument("--drive-folder", type=str, default="MyDrive/myproject", help="Google Drive folder path")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-models", action="store_true", help="Skip model downloads")
    parser.add_argument("--skip-drive", action="store_true", help="Skip Google Drive mount")
    args = parser.parse_args()

    print("=" * 60)
    print("  Motion Video Director - Colab Setup")
    print("=" * 60)

    # Check GPU
    has_gpu = check_gpu()
    print(f"\n[setup] GPU Available: {'Yes 🎮' if has_gpu else 'No (CPU only)'}")

    # Mount Google Drive
    drive_path = None
    if not args.skip_drive:
        drive_path = mount_google_drive(args.drive_folder)
        if drive_path:
            setup_project_symlink(drive_path)

    # Clone/sync repo
    if args.repo and drive_path:
        clone_or_sync_repo(args.repo, drive_path)

    # Install system deps
    install_system_deps()

    # Install Python deps
    if not args.skip_deps:
        install_python_deps()

    # Download models
    if not args.skip_models:
        download_models()

    # Verify
    verify_environment()

    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: python scripts/fetch_assets.py --category all")
    print("  2. Run: python scripts/colab_render.py --mode preview")
    print("  3. Check renders/previews/ for contact sheet and preview MP4")


if __name__ == "__main__":
    main()