#!/usr/bin/env python3
"""
Download assets from manifest.json URLs.
Run in Colab after cloning the repository.
"""

import json
import os
import sys
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = PROJECT_ROOT / "manifest.json"
ASSETS_DIR = PROJECT_ROOT / "assets"


def load_manifest() -> Dict:
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)


def save_manifest(manifest: Dict):
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def get_file_hash(filepath: Path) -> str:
    """Compute SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_file(url: str, dest: Path, headers: Dict = None, timeout: int = 30) -> bool:
    """Download a file with progress bar."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(dest, "wb") as f, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=dest.name,
            leave=False
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        return True
    except Exception as e:
        print(f"[fetch_assets] Failed to download {url}: {e}")
        if dest.exists():
            dest.unlink()
        return False


def download_font(asset: Dict, manifest: Dict) -> bool:
    """Download a font file."""
    url = asset.get("source")
    if not url:
        print(f"[fetch_assets] No source URL for font {asset['path']}")
        return False

    dest = PROJECT_ROOT / asset["path"]
    if dest.exists():
        print(f"[fetch_assets] Font already exists: {dest.name}")
        asset["verified"] = True
        return True

    print(f"[fetch_assets] Downloading font: {asset['name']} from {url}")

    # Font URLs often need special handling
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MotionVideoDirector/1.0)"}

    # Some font sites require specific handling
    if "fontshare.com" in url:
        # Fontshare requires API or direct download link
        print(f"[fetch_assets] Fontshare fonts need manual download. Visit: {url}")
        return False

    success = download_file(url, dest, headers=headers)
    if success:
        asset["verified"] = True
        asset["hash"] = get_file_hash(dest)
        print(f"[fetch_assets] ✅ Downloaded: {dest.name}")
    return success


def download_image(asset: Dict, manifest: Dict) -> bool:
    """Download an image file."""
    url = asset.get("source")
    if not url:
        print(f"[fetch_assets] No source URL for image {asset['path']}")
        return False

    dest = PROJECT_ROOT / asset["path"]
    if dest.exists():
        print(f"[fetch_assets] Image already exists: {dest.name}")
        asset["verified"] = True
        return True

    print(f"[fetch_assets] Downloading image: {dest.name}")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; MotionVideoDirector/1.0)"}
    success = download_file(url, dest, headers=headers)
    if success:
        asset["verified"] = True
        asset["hash"] = get_file_hash(dest)
        print(f"[fetch_assets] ✅ Downloaded: {dest.name}")
    return success


def download_sfx(asset: Dict, manifest: Dict) -> bool:
    """Download a sound effect file."""
    url = asset.get("source")
    if not url:
        print(f"[fetch_assets] No source URL for SFX {asset['path']}")
        return False

    dest = PROJECT_ROOT / asset["path"]
    if dest.exists():
        print(f"[fetch_assets] SFX already exists: {dest.name}")
        asset["verified"] = True
        return True

    print(f"[fetch_assets] Downloading SFX: {dest.name}")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; MotionVideoDirector/1.0)"}
    success = download_file(url, dest, headers=headers)
    if success:
        asset["verified"] = True
        asset["hash"] = get_file_hash(dest)
        print(f"[fetch_assets] ✅ Downloaded: {dest.name}")
    return success


def download_music(asset: Dict, manifest: Dict) -> bool:
    """Download a music file."""
    return download_sfx(asset, manifest)


def download_lottie(asset: Dict, manifest: Dict) -> bool:
    """Download a Lottie animation."""
    return download_image(asset, manifest)


def verify_assets(manifest: Dict) -> Dict[str, List[str]]:
    """Verify all assets exist and have correct hashes."""
    results = {"missing": [], "verified": [], "hash_mismatch": []}

    for category, assets in manifest.get("assets", {}).items():
        if category == "vo":
            assets = [assets] if isinstance(assets, dict) else assets

        if not isinstance(assets, list):
            continue

        for asset in assets:
            path = PROJECT_ROOT / asset["path"]
            if not path.exists():
                results["missing"].append(asset["path"])
                continue

            if "hash" in asset:
                actual_hash = get_file_hash(path)
                if actual_hash != asset["hash"]:
                    results["hash_mismatch"].append(asset["path"])
                else:
                    results["verified"].append(asset["path"])
            else:
                results["verified"].append(asset["path"])

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Download assets from manifest.json")
    parser.add_argument("--category", choices=["fonts", "images", "lottie", "sfx", "music", "all"], default="all")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing assets")
    parser.add_argument("--force", action="store_true", help="Re-download even if file exists")
    args = parser.parse_args()

    manifest = load_manifest()
    assets = manifest.get("assets", {})

    if args.verify_only:
        results = verify_assets(manifest)
        print("\n[fetch_assets] Verification Results:")
        print(f"  ✅ Verified: {len(results['verified'])}")
        print(f"  ❌ Missing: {len(results['missing'])}")
        print(f"  ⚠️  Hash Mismatch: {len(results['hash_mismatch'])}")
        if results["missing"]:
            for m in results["missing"]:
                print(f"    - {m}")
        if results["hash_mismatch"]:
            for m in results["hash_mismatch"]:
                print(f"    - {m}")
        return

    categories = [args.category] if args.category != "all" else ["fonts", "images", "lottie", "sfx", "music"]

    for category in categories:
        if category not in assets:
            continue

        print(f"\n[fetch_assets] Processing {category}...")
        category_assets = assets[category]

        if category == "vo":
            # VO is user-provided, skip
            print(f"[fetch_assets] Skipping VO (user-provided)")
            continue

        downloaders = {
            "fonts": download_font,
            "images": download_image,
            "lottie": download_lottie,
            "sfx": download_sfx,
            "music": download_music,
        }

        downloader = downloaders.get(category)
        if not downloader:
            continue

        for asset in category_assets:
            if not args.force and asset.get("verified") and (PROJECT_ROOT / asset["path"]).exists():
                continue
            downloader(asset, manifest)

    save_manifest(manifest)
    print("\n[fetch_assets] Done. Manifest updated.")

    # Verify
    results = verify_assets(manifest)
    print(f"\n[fetch_assets] Final: ✅ {len(results['verified'])} | ❌ {len(results['missing'])} | ⚠️ {len(results['hash_mismatch'])}")


if __name__ == "__main__":
    main()