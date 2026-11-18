#!/usr/bin/env python3
"""
Deterministic frame renderer for motion video (Python/Colab version).
Implements the same CLI contract as src/render.js.
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[render] Pillow not installed. Run: pip install pillow")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

CONFIG = {
    "project": "myproject",
    "version": "1.0.0",
    "aspect": "9:16",
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "duration": 60,
    "backgroundColor": "#0a0a0a",
    "fontFamilies": {
        "primary": "Satoshi",
        "secondary": "Inter",
        "accent": "Caveat Brush"
    },
    "colors": {
        "primary": "#ffffff",
        "secondary": "#a0a0a0",
        "accent": "#ff6a1a",
        "accentGradient": ["#ff6a1a", "#ffaa00"],
        "background": "#0a0a0a",
        "surface": "#1a1a1a",
        "text": "#ffffff",
        "textMuted": "#888888"
    },
    "safeZones": {
        "top": 220,
        "bottom": 420,
        "right": 140,
        "left": 140
    },
    "intensity": 2,
    "videoType": "saas_explainer"
}

BEATS = [
    {"id": "hook", "start": 0.0, "end": 3.0, "label": "Hook", "voLine": 0},
    {"id": "problem", "start": 3.0, "end": 8.0, "label": "Problem", "voLine": 1},
    {"id": "solution", "start": 8.0, "end": 18.0, "label": "Solution", "voLine": 2},
    {"id": "proof", "start": 18.0, "end": 30.0, "label": "Proof", "voLine": 3},
    {"id": "cta", "start": 30.0, "end": 35.0, "label": "CTA", "voLine": 4},
    {"id": "outro", "start": 35.0, "end": 40.0, "label": "Outro", "voLine": 5}
]

SCENES = [
    {"id": "hook", "component": "HookScene", "beats": ["hook"]},
    {"id": "problem", "component": "ProblemScene", "beats": ["problem"]},
    {"id": "solution", "component": "SolutionScene", "beats": ["solution"]},
    {"id": "proof", "component": "ProofScene", "beats": ["proof"]},
    {"id": "cta", "component": "CTAScene", "beats": ["cta"]},
    {"id": "outro", "component": "OutroScene", "beats": ["outro"]}
]

FONT_CACHE: Dict[str, ImageFont.FreeTypeFont] = {}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_cubic(t: float) -> float:
    return t ** 3


def ease_out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - 2 ** (-10 * t)


def stagger(index: int, base_delay: float, stagger_amount: float) -> float:
    return base_delay + index * stagger_amount


def seeded_random(seed: float) -> float:
    x = math.sin(seed) * 10000
    return x - math.floor(x)


def get_beat(beat_id: str) -> Optional[Dict]:
    for b in BEATS:
        if b["id"] == beat_id:
            return b
    return None


def get_scene(scene_id: str) -> Optional[Dict]:
    for s in SCENES:
        if s["id"] == scene_id:
            return s
    return None


def get_beats_for_scene(scene_id: str) -> List[Dict]:
    scene = get_scene(scene_id)
    if not scene:
        return []
    return [get_beat(bid) for bid in scene["beats"] if get_beat(bid)]


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def hex_to_rgba(hex_color: str, alpha: float) -> tuple:
    r, g, b = hex_to_rgb(hex_color)
    return (r, g, b, int(alpha * 255))


def load_font(font_name: str, size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    key = f"{font_name}-{weight}-{size}"
    if key in FONT_CACHE:
        return FONT_CACHE[key]

    font_dir = PROJECT_ROOT / "assets" / "fonts"
    font_map = {
        ("Satoshi", "bold"): "Satoshi-Bold.woff2",
        ("Satoshi", "regular"): "Satoshi-Regular.woff2",
        ("Inter", "bold"): "Inter-Bold.woff2",
        ("Inter", "regular"): "Inter-Regular.woff2",
        ("Inter", "light"): "Inter-Light.woff2",
        ("Caveat Brush", "regular"): "CaveatBrush-Regular.ttf",
    }

    font_file = font_map.get((font_name, weight))
    if font_file and (font_dir / font_file).exists():
        try:
            font = ImageFont.truetype(str(font_dir / font_file), size)
            FONT_CACHE[key] = font
            return font
        except Exception as e:
            print(f"[render] Font load failed: {font_file} - {e}")

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf" if weight == "bold" else "DejaVuSans.ttf", size)
    except Exception:
        font = ImageFont.load_default()
    FONT_CACHE[key] = font
    return font


def draw_rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int, fill: tuple = None, outline: tuple = None, width: int = 1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_hook_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2
    easing = ease_out_expo(progress)
    y = lerp(cy + 200, cy, easing)
    opacity = int(easing * 255)

    font = load_font("Satoshi", 96, "bold")
    color = hex_to_rgba(colors["primary"], easing)

    text = "Nobody drew this."
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text((cx - text_w // 2, y - (bbox[3] - bbox[1]) // 2), text, font=font, fill=color)


def draw_problem_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2
    easing = ease_out_cubic(progress)
    y = lerp(cy + 150, cy, easing)
    opacity = int(easing * 255)

    font = load_font("Inter", 48, "regular")
    color = hex_to_rgba(colors["secondary"], easing)

    lines = [
        "Most teams lose hours",
        "every week to manual work."
    ]

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text((cx - text_w // 2, y + i * 70 - (bbox[3] - bbox[1]) // 2), line, font=font, fill=color)


def draw_solution_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2
    easing = ease_out_cubic(progress)
    scale = lerp(0.5, 1.0, easing)
    opacity = int(easing * 255)

    font = load_font("Satoshi", int(72 * scale), "bold")

    gradient_colors = [hex_to_rgb(colors["accentGradient"][0]), hex_to_rgb(colors["accentGradient"][1])]

    text = "Meet Flow."
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    for i, char in enumerate(text):
        char_bbox = draw.textbbox((0, 0), char, font=font)
        char_w = char_bbox[2] - char_bbox[0]
        t_char = i / max(len(text) - 1, 1)
        r = int(lerp(gradient_colors[0][0], gradient_colors[1][0], t_char))
        g = int(lerp(gradient_colors[0][1], gradient_colors[1][1], t_char))
        b = int(lerp(gradient_colors[0][2], gradient_colors[1][2], t_char))
        x_pos = cx - text_w // 2 + sum(draw.textbbox((0, 0), c, font=font)[2] - draw.textbbox((0, 0), c, font=font)[0] for c in text[:i])
        draw.text((x_pos, cy - text_h // 2), char, font=font, fill=(r, g, b, opacity))


def draw_proof_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2
    card_count = 3
    card_width = 300
    card_height = 400
    spacing = 40
    total_width = card_count * card_width + (card_count - 1) * spacing
    start_x = cx - total_width // 2

    for i in range(card_count):
        card_progress = clamp((progress - i * 0.1) / 0.8, 0, 1)
        easing = ease_out_expo(card_progress)
        x = start_x + i * (card_width + spacing)
        y = cy - card_height // 2
        scale = lerp(0.8, 1.0, easing)
        opacity = int(easing * 255)

        scaled_w = int(card_width * scale)
        scaled_h = int(card_height * scale)
        scaled_x = x + (card_width - scaled_w) // 2
        scaled_y = y + (card_height - scaled_h) // 2

        surface_color = hex_to_rgba(colors["surface"], easing)
        draw_rounded_rect(draw, (scaled_x, scaled_y, scaled_x + scaled_w, scaled_y + scaled_h), 16, fill=surface_color)

        title_font = load_font("Satoshi", int(24 * scale), "bold")
        body_font = load_font("Inter", int(20 * scale), "light")
        text_color = hex_to_rgba(colors["primary"], easing)
        muted_color = hex_to_rgba(colors["textMuted"], easing)

        title = f"Feature {i + 1}"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        draw.text((scaled_x + (scaled_w - (bbox[2] - bbox[0])) // 2, scaled_y + 60), title, font=title_font, fill=text_color)

        items = ["Automated workflow", "Real-time sync", "Zero config"]
        for j, item in enumerate(items):
            bbox = draw.textbbox((0, 0), item, font=body_font)
            draw.text((scaled_x + (scaled_w - (bbox[2] - bbox[0])) // 2, scaled_y + 100 + j * 40), item, font=body_font, fill=muted_color)


def draw_cta_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2
    easing = ease_out_cubic(progress)
    y = lerp(cy + 100, cy, easing)
    opacity = int(easing * 255)

    btn_width = 320
    btn_height = 72
    btn_x = cx - btn_width // 2
    btn_y = y - btn_height // 2

    grad_start = hex_to_rgb(colors["accentGradient"][0])
    grad_end = hex_to_rgb(colors["accentGradient"][1])

    for py in range(btn_height):
        t_grad = py / btn_height
        r = int(lerp(grad_start[0], grad_end[0], t_grad))
        g = int(lerp(grad_start[1], grad_end[1], t_grad))
        b = int(lerp(grad_start[2], grad_end[2], t_grad))
        draw.line([(btn_x, btn_y + py), (btn_x + btn_width, btn_y + py)], fill=(r, g, b, opacity))

    draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_width, btn_y + btn_height), 36, outline=(0, 0, 0, 0), width=0)

    font = load_font("Satoshi", 28, "bold")
    text = "Start Free Today"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text((cx - text_w // 2, y - text_h // 2), text, font=font, fill=(0, 0, 0, opacity))


def draw_outro_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2
    easing = ease_out_cubic(progress)
    opacity = int(easing * 255)

    font_bold = load_font("Satoshi", 48, "bold")
    font_light = load_font("Inter", 24, "light")

    text1 = "Flow"
    bbox = draw.textbbox((0, 0), text1, font=font_bold)
    draw.text((cx - (bbox[2] - bbox[0]) // 2, cy - 40 - (bbox[3] - bbox[1]) // 2), text1, font=font_bold, fill=hex_to_rgba(colors["primary"], easing))

    text2 = "flow.example.com"
    bbox = draw.textbbox((0, 0), text2, font=font_light)
    draw.text((cx - (bbox[2] - bbox[0]) // 2, cy + 30 - (bbox[3] - bbox[1]) // 2), text2, font=font_light, fill=hex_to_rgba(colors["textMuted"], easing))


def draw_debug_info(draw: ImageDraw.Draw, t: float, frame_index: int, width: int, height: int, fps: int, scale: float, seed: int):
    font = load_font("Inter", 12, "regular")
    color = (255, 255, 255, 128)
    draw.text((10, 10), f"t={t:.3f}s frame={frame_index} seed={seed}", font=font, fill=color)
    draw.text((10, 30), f"{width}x{height} @ {fps}fps scale={scale}", font=font, fill=color)


def draw_frame(t: float, frame_index: int, width: int, height: int, fps: int, scale: float, seed: int, target_scene: Optional[str]) -> Image.Image:
    img = Image.new("RGBA", (width, height), hex_to_rgb(CONFIG["backgroundColor"]) + (255,))
    draw = ImageDraw.Draw(img)

    active_scenes = []
    for scene in SCENES:
        if target_scene and scene["id"] != target_scene:
            continue
        beats = get_beats_for_scene(scene["id"])
        if any(b and t >= b["start"] and t < b["end"] for b in beats):
            active_scenes.append(scene)

    for scene in active_scenes:
        beats = get_beats_for_scene(scene["id"])
        for beat in beats:
            if not beat:
                continue
            progress = clamp((t - beat["start"]) / (beat["end"] - beat["start"]), 0, 1)
            scene_id = scene["id"]

            if scene_id == "hook":
                draw_hook_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "problem":
                draw_problem_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "solution":
                draw_solution_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "proof":
                draw_proof_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "cta":
                draw_cta_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "outro":
                draw_outro_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)

    draw_debug_info(draw, t, frame_index, width, height, fps, scale, seed)
    return img


def create_contact_sheet(frames_dir: Path, output_path: Path, cols: int = 6, thumb_width: int = 180):
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    if not frame_files:
        return

    rows = math.ceil(len(frame_files) / cols)
    thumb_height = int(thumb_width * 1920 / 1080)
    sheet_width = cols * thumb_width
    sheet_height = rows * (thumb_height + 30)

    sheet = Image.new("RGB", (sheet_width, sheet_height), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)
    font = load_font("Inter", 10, "regular")

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

    sheet.save(output_path, "JPEG", quality=85)
    print(f"[contact-sheet] Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Deterministic frame renderer for motion video")
    parser.add_argument("--from", type=float, default=0, dest="from_sec", help="Start time in seconds")
    parser.add_argument("--to", type=float, default=CONFIG["duration"], dest="to_sec", help="End time in seconds")
    parser.add_argument("--fps", type=int, default=CONFIG["fps"], help="Frames per second")
    parser.add_argument("--scale", type=float, default=1.0, help="Resolution scale 0-1")
    parser.add_argument("--out", type=str, default="renders/final", help="Output directory")
    parser.add_argument("--jpg", action="store_true", help="Output JPG instead of PNG")
    parser.add_argument("--scene", type=str, default=None, help="Render specific scene only")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic noise")
    parser.add_argument("--contact-sheet", action="store_true", help="Generate contact sheet after render")
    parser.add_argument("--contact-sheet-cols", type=int, default=6, help="Contact sheet columns")

    args = parser.parse_args()

    FROM = args.from_sec
    TO = args.to_sec
    FPS = args.fps
    SCALE = clamp(args.scale, 0.01, 1.0)
    OUT_DIR = PROJECT_ROOT / args.out
    USE_JPG = args.jpg
    TARGET_SCENE = args.scene
    SEED = args.seed

    WIDTH = round(CONFIG["width"] * SCALE)
    HEIGHT = round(CONFIG["height"] * SCALE)
    TOTAL_FRAMES = round((TO - FROM) * FPS)

    print(f"[render] Project: {CONFIG['project']}")
    print(f"[render] Range: {FROM}s - {TO}s ({TOTAL_FRAMES} frames)")
    print(f"[render] Resolution: {WIDTH}x{HEIGHT} @ {FPS}fps (scale: {SCALE})")
    print(f"[render] Output: {OUT_DIR}")
    print(f"[render] Seed: {SEED}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    for frame in range(TOTAL_FRAMES):
        t = FROM + frame / FPS
        img = draw_frame(t, frame, WIDTH, HEIGHT, FPS, SCALE, SEED, TARGET_SCENE)

        ext = "jpg" if USE_JPG else "png"
        filename = f"frame_{frame:06d}.{ext}"
        filepath = OUT_DIR / filename

        if USE_JPG:
            rgb_img = Image.new("RGB", img.size, (0, 0, 0))
            rgb_img.paste(img, mask=img.split()[3])
            rgb_img.save(filepath, "JPEG", quality=90)
        else:
            img.save(filepath, "PNG")

        if frame % 30 == 0 or frame == TOTAL_FRAMES - 1:
            pct = (frame + 1) / TOTAL_FRAMES * 100
            print(f"[render] {pct:.1f}% ({frame + 1}/{TOTAL_FRAMES})")

    elapsed = time.time() - start_time
    print(f"[render] Done in {elapsed:.1f}s. Frames saved to {OUT_DIR}")

    if args.contact_sheet:
        sheet_path = OUT_DIR.parent / "previews" / f"sheet_{FROM}-{TO}.jpg"
        sheet_path.parent.mkdir(parents=True, exist_ok=True)
        create_contact_sheet(OUT_DIR, sheet_path, cols=args.contact_sheet_cols)


if __name__ == "__main__":
    main()