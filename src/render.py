#!/usr/bin/env python3
"""
Deterministic frame renderer for motion video (Python/Colab version).
Implements the same CLI contract as src/render.js.
Earth Stopped Spinning — 60s, 16:9, cinematic 2D animation
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("[render] Pillow not installed. Run: pip install pillow")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

CONFIG = {
    "project": "earth-stopped-spinning",
    "version": "1.0.0",
    "aspect": "16:9",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "duration": 60,
    "backgroundColor": "#0a0a1a",
    "fontFamilies": {
        "primary": "Cinzel",
        "secondary": "Libre Baskerville",
        "mono": "Space Mono"
    },
    "colors": {
        "primary": "#ffffff",
        "secondary": "#a0b8d0",
        "accent": "#e8a838",
        "accentGradient": ["#e8a838", "#ffcc00"],
        "danger": "#c0392b",
        "dangerGradient": ["#c0392b", "#e74c3c"],
        "atmosphere": "#00b4d8",
        "atmosphereGradient": ["#00b4d8", "#0077b6"],
        "background": "#0a0a1a",
        "surface": "#15152a",
        "text": "#ffffff",
        "textMuted": "#8899aa",
        "gold": "#e8a838",
        "teal": "#00b4d8",
        "red": "#c0392b"
    },
    "safeZones": {
        "top": 80,
        "bottom": 120,
        "right": 100,
        "left": 100
    },
    "intensity": 4,
    "videoType": "cinematic_documentary",
    "grain": 0.08,
    "vignette": 0.15
}

BEATS = [
    {"id": "hook", "start": 0.0, "end": 5.0, "label": "Hook — The Freeze", "voLine": 0},
    {"id": "day_night", "start": 5.0, "end": 12.0, "label": "Day/Night — Eternal Extremes", "voLine": 1},
    {"id": "atmosphere", "start": 12.0, "end": 20.0, "label": "Atmosphere — Supersonic Scour", "voLine": 2},
    {"id": "oceans", "start": 20.0, "end": 28.0, "label": "Oceans — Polar Surge", "voLine": 3},
    {"id": "magnetic", "start": 28.0, "end": 36.0, "label": "Magnetic — Field Collapse", "voLine": 4},
    {"id": "temperature", "start": 36.0, "end": 44.0, "label": "Temperature — Beyond Survival", "voLine": 5},
    {"id": "life", "start": 44.0, "end": 52.0, "label": "Life — Extremophiles Endure", "voLine": 6},
    {"id": "outro", "start": 52.0, "end": 60.0, "label": "Outro — What If Continues", "voLine": 7}
]

SCENES = [
    {"id": "hook", "component": "HookScene", "beats": ["hook"]},
    {"id": "day_night", "component": "DayNightScene", "beats": ["day_night"]},
    {"id": "atmosphere", "component": "AtmosphereScene", "beats": ["atmosphere"]},
    {"id": "oceans", "component": "OceansScene", "beats": ["oceans"]},
    {"id": "magnetic", "component": "MagneticScene", "beats": ["magnetic"]},
    {"id": "temperature", "component": "TemperatureScene", "beats": ["temperature"]},
    {"id": "life", "component": "LifeScene", "beats": ["life"]},
    {"id": "outro", "component": "OutroScene", "beats": ["outro"]}
]

FONT_CACHE: Dict[str, ImageFont.FreeTypeFont] = {}
NOISE_CACHE: Dict[Tuple[int, int], Image.Image] = {}


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


def ease_in_expo(t: float) -> float:
    return 0 if t == 0 else 2 ** (10 * (t - 1))


def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def stagger(index: int, base_delay: float, stagger_amount: float) -> float:
    return base_delay + index * stagger_amount


def seeded_random(seed: float) -> float:
    x = math.sin(seed) * 10000
    return x - math.floor(x)


def perlin_noise(x: float, y: float, seed: int = 42) -> float:
    n = math.sin(x * 12.9898 + y * 78.233 + seed) * 43758.5453
    return n - math.floor(n)


def smooth_step(t: float) -> float:
    return t * t * (3 - 2 * t)


def smoother_step(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


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
        ("Cinzel", "bold"): "Cinzel-Variable.ttf",
        ("Cinzel", "regular"): "Cinzel-Variable.ttf",
        ("Libre Baskerville", "bold"): "LibreBaskerville-Variable.ttf",
        ("Libre Baskerville", "regular"): "LibreBaskerville-Variable.ttf",
        ("Libre Baskerville", "italic"): "LibreBaskerville-Italic-Variable.ttf",
        ("Space Mono", "bold"): "SpaceMono-Bold.ttf",
        ("Space Mono", "regular"): "SpaceMono-Regular.ttf",
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


def draw_grain_overlay(img: Image.Image, grain_amount: float, seed: int) -> Image.Image:
    if grain_amount <= 0:
        return img
    w, h = img.size
    cache_key = (w, h)
    if cache_key not in NOISE_CACHE:
        noise = Image.effect_noise((w, h), 128).convert("L")
        NOISE_CACHE[cache_key] = noise
    noise = NOISE_CACHE[cache_key]
    grain_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grain_pixels = noise.load()
    grain_layer_pixels = grain_layer.load()
    for y in range(h):
        for x in range(w):
            val = grain_pixels[x, y]
            alpha = int((val - 128) * grain_amount * 0.5)
            if alpha != 0:
                grain_layer_pixels[x, y] = (255, 255, 255, clamp(alpha, -255, 255))
    return Image.alpha_composite(img.convert("RGBA"), grain_layer)


def draw_vignette(img: Image.Image, amount: float) -> Image.Image:
    if amount <= 0:
        return img
    w, h = img.size
    vignette = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(vignette)
    cx, cy = w // 2, h // 2
    max_r = math.hypot(cx, cy)
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / max_r
            alpha = int(255 * (1 - amount * smooth_step(d)))
            vignette.putpixel((x, y), clamp(alpha, 0, 255))
    img_rgba = img.convert("RGBA")
    img_rgba.putalpha(Image.composite(img_rgba.split()[3], Image.new("L", (w, h), 0), vignette))
    return img_rgba


def draw_starfield(draw: ImageDraw.Draw, width: int, height: int, seed: int, density: float = 0.001):
    num_stars = int(width * height * density)
    for _ in range(num_stars):
        x = int(seeded_random(seed + _) * width)
        y = int(seeded_random(seed + _ + 1000) * height)
        brightness = int(128 + seeded_random(seed + _ + 2000) * 127)
        size = 1 if seeded_random(seed + _ + 3000) > 0.7 else 2
        draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness, 255))


# ========== SCENE 1: HOOK ==========
def draw_hook_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Starfield
    draw_starfield(draw, width, height, seed, 0.0008)

    # Earth circle (simplified)
    earth_r = int(min(width, height) * 0.25)
    earth_progress = clamp(progress / 0.3, 0, 1)
    rotation_angle = lerp(0, -0.3, ease_in_cubic(earth_progress))  # rotates then stops

    # Draw Earth as circle with simple shading
    for r in range(earth_r, 0, -1):
        alpha = int(255 * (1 - r / earth_r) * 0.6)
        color = (30, 80, 150, alpha)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color)

    # Freeze flash at 1.5s (progress ~0.3)
    if 0.25 < progress < 0.35:
        flash_alpha = int(255 * (1 - abs(progress - 0.3) / 0.05))
        draw.ellipse([cx - earth_r, cy - earth_r, cx + earth_r, cy + earth_r],
                     outline=(255, 255, 200, flash_alpha), width=3)

    # Camera push-in (scale Earth)
    scale = lerp(1.0, 1.15, progress)
    scaled_r = int(earth_r * scale)

    # Text: "EARTH" rises from bottom
    text_progress = clamp((progress - 0.2) / 0.5, 0, 1)
    easing = ease_out_expo(text_progress)
    y = lerp(cy + 200, cy - 80, easing)
    opacity = int(easing * 255)

    font = load_font("Cinzel", 96, "bold")
    color = hex_to_rgba(colors["primary"], easing)

    text = "EARTH"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text((cx - text_w // 2, y - (bbox[3] - bbox[1]) // 2), text, font=font, fill=color)

    # "STOPPED SPINNING" below
    sub_progress = clamp((progress - 0.5) / 0.4, 0, 1)
    sub_easing = ease_out_cubic(sub_progress)
    sub_y = lerp(cy + 100, cy + 40, sub_easing)
    sub_opacity = int(sub_easing * 255)

    sub_font = load_font("Libre Baskerville", 36, "regular")
    sub_color = hex_to_rgba(colors["secondary"], sub_easing)

    sub_text = "STOPPED SPINNING"
    bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    sub_w = bbox[2] - bbox[0]
    draw.text((cx - sub_w // 2, sub_y), sub_text, font=sub_font, fill=sub_color)


# ========== SCENE 2: DAY/NIGHT ==========
def draw_day_night_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Split line position (expands from center)
    split_progress = ease_out_cubic(progress)
    left_width = int(cx * split_progress)
    right_start = width - left_width

    # Day side (left) - heat shimmer
    for x in range(left_width):
        # Heat distortion: vertical lines with noise offset
        for y in range(0, height, 4):
            noise_val = perlin_noise(x * 0.02, y * 0.01 + t * 2, seed)
            offset = int(noise_val * 8)
            shade = int(200 + noise_val * 55)
            draw.line([(x + offset, y), (x + offset, y + 3)], fill=(shade, shade // 2, 0, 255))

    # Sun glow on day side
    sun_alpha = int(100 * split_progress)
    for r in range(200, 0, -10):
        draw.ellipse([cx - left_width - r, cy - r, cx - left_width + r, cy + r],
                     outline=(255, 200, 0, sun_alpha // (200 // r + 1)))

    # Night side (right) - frost crystals
    for x in range(right_start, width):
        for y in range(0, height, 6):
            noise_val = perlin_noise(x * 0.015, y * 0.02, seed + 1000)
            if noise_val > 0.7:
                crystal_h = int(noise_val * 40)
                draw.line([(x, y), (x + int(noise_val * 3), y - crystal_h)],
                          fill=(100, 180, 255, int(noise_val * 200)), width=1)

    # Gold divider line
    divider_x = cx
    divider_alpha = int(255 * split_progress)
    draw.line([(divider_x, 0), (divider_x, height)], fill=(232, 168, 56, divider_alpha), width=3)

    # Text: "BURNS" (left, gold)
    burns_progress = clamp((progress - 0.1) / 0.4, 0, 1)
    burns_easing = ease_out_expo(burns_progress)
    if burns_progress > 0:
        font = load_font("Cinzel", 72, "bold")
        color = hex_to_rgba(colors["gold"], burns_easing)
        text = "BURNS"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - left_width // 2 - bbox[2] // 2, cy - 60), text, font=font, fill=color)

    # Text: "FREEZES" (right, teal)
    freezes_progress = clamp((progress - 0.2) / 0.4, 0, 1)
    freezes_easing = ease_out_expo(freezes_progress)
    if freezes_progress > 0:
        font = load_font("Cinzel", 72, "bold")
        color = hex_to_rgba(colors["teal"], freezes_easing)
        text = "FREEZES"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx + (width - right_start) // 2 - bbox[2] // 2, cy - 60), text, font=font, fill=color)

    # Sub text
    sub_progress = clamp((progress - 0.5) / 0.4, 0, 1)
    sub_easing = ease_out_cubic(sub_progress)
    if sub_progress > 0:
        font = load_font("Libre Baskerville", 28, "italic")
        color = hex_to_rgba(colors["textMuted"], sub_easing)
        draw.text((cx - left_width // 2 - 100, cy + 40), "ETERNAL DAY", font=font, fill=color)
        draw.text((cx + (width - right_start) // 2 - 100, cy + 40), "ENDLESS NIGHT", font=font, fill=color)


# ========== SCENE 3: ATMOSPHERE ==========
def draw_atmosphere_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Earth silhouette (bottom)
    earth_h = int(height * 0.3)
    draw.rectangle([0, height - earth_h, width, height], fill=(10, 10, 30, 255))

    # Atmosphere layer (teal gradient)
    atmo_h = int(height * 0.15)
    atmo_y = height - earth_h - atmo_h
    for y in range(atmo_h):
        p = y / atmo_h
        r = int(lerp(0, 0, p))
        g = int(lerp(180, 0, p))
        b = int(lerp(216, 100, p))
        a = int(lerp(180, 0, p))
        draw.line([(0, atmo_y + y), (width, atmo_y + y)], fill=(r, g, b, a))

    # Wind flow lines (left to right, high speed)
    flow_speed = t * 500  # pixels per second
    num_lines = 20
    for i in range(num_lines):
        y = atmo_y + int(i / num_lines * atmo_h)
        line_progress = (flow_speed + i * 50) % width
        line_len = 150
        alpha = int(200 * (1 - abs((line_progress % width) - width/2) / (width/2)))
        draw.line([(line_progress, y), (line_progress + line_len, y)],
                  fill=(0, 200, 255, alpha), width=2)

    # Particles ripped from surface
    for i in range(50):
        p_seed = seed + i * 100
        x = (seeded_random(p_seed) * width + t * 300) % width
        y = height - earth_h - int(seeded_random(p_seed + 1) * earth_h * 0.5)
        size = int(2 + seeded_random(p_seed + 2) * 4)
        alpha = int(150 + seeded_random(p_seed + 3) * 100)
        draw.ellipse([x, y, x + size, y + size], fill=(200, 200, 100, alpha))

    # Shockwave cones at "mountains"
    mountain_x = [width * 0.2, width * 0.5, width * 0.8]
    for mx in mountain_x:
        sw_progress = (t * 2) % 1.5 / 1.5
        sw_h = int(earth_h * sw_progress)
        sw_alpha = int(200 * (1 - sw_progress))
        for dy in range(sw_h):
            w = int(dy * 0.5)
            draw.line([(mx - w, height - earth_h - dy), (mx + w, height - earth_h - dy)],
                      fill=(255, 150, 0, sw_alpha), width=1)

    # Text: "SUPERSONIC" (stretched along flow)
    text_progress = clamp((progress - 0.1) / 0.3, 0, 1)
    if text_progress > 0:
        font = load_font("Cinzel", 80, "bold")
        color = hex_to_rgba(colors["teal"], text_progress)
        text = "SUPERSONIC"
        bbox = draw.textbbox((0, 0), text, font=font)
        # Stretch effect: draw each char with increasing x offset
        x_start = width * 0.1
        for i, char in enumerate(text):
            char_bbox = draw.textbbox((0, 0), char, font=font)
            char_w = char_bbox[2] - char_bbox[0]
            stretch = 1 + text_progress * 0.5
            x = x_start + i * char_w * stretch
            y = atmo_y - 60 + math.sin(t * 5 + i) * 5
            draw.text((x, y), char, font=font, fill=color)

    # "1,000 MPH" counter
    counter_progress = clamp((progress - 0.4) / 0.3, 0, 1)
    if counter_progress > 0:
        font = load_font("Space Mono", 48, "bold")
        color = hex_to_rgba(colors["gold"], counter_progress)
        val = int(1000 * ease_out_expo(counter_progress))
        text = f"{val:,} MPH"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((width - bbox[2] - 50, 50), text, font=font, fill=color)


# ========== SCENE 4: OCEANS ==========
def draw_oceans_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Top-down Earth circle
    r = int(min(width, height) * 0.35)

    # Ocean (blue) - water rushing to poles
    # Draw as animated arcs from equator to poles
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        # Flow toward poles (90° and 270°)
        pole_factor = abs(math.sin(rad))
        flow_progress = (progress + pole_factor * 0.5) % 1.0
        current_r = int(r * (0.3 + 0.7 * flow_progress))

        x1 = cx + int(current_r * math.cos(rad))
        y1 = cy + int(current_r * math.sin(rad))
        x2 = cx + int(r * math.cos(rad))
        y2 = cy + int(r * math.sin(rad))

        alpha = int(200 * pole_factor)
        draw.line([(x1, y1), (x2, y2)], fill=(0, 100, 200, alpha), width=3)

    # Land masses emerging at equator (brown/green)
    land_angles = [0, 45, 135, 180, 225, 315]  # equatorial regions
    for angle in land_angles:
        rad = math.radians(angle)
        land_progress = ease_out_expo(progress)
        land_r = int(r * 0.3 * land_progress)
        x = cx + int((r * 0.4 + land_r) * math.cos(rad))
        y = cy + int((r * 0.4 + land_r) * math.sin(rad))
        size = int(30 * land_progress)
        color = (100, 150, 50, int(255 * land_progress))
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)

    # Arrow indicators (red) showing flow
    for angle in [30, 150, 210, 330]:
        rad = math.radians(angle)
        arrow_r = r * 0.6
        x = cx + int(arrow_r * math.cos(rad))
        y = cy + int(arrow_r * math.sin(rad))
        # Arrow pointing toward nearest pole
        pole_y = -1 if y < cy else 1
        draw.polygon([
            (x, y),
            (x - 10, y + 20 * pole_y),
            (x + 10, y + 20 * pole_y)
        ], fill=(255, 50, 50, 200))

    # Text: "OCEANS SURGE" (curved along flow)
    text_progress = clamp((progress - 0.1) / 0.3, 0, 1)
    if text_progress > 0:
        font = load_font("Cinzel", 56, "bold")
        color = hex_to_rgba(colors["teal"], text_progress)
        text = "OCEANS SURGE"
        # Draw along circular path
        for i, char in enumerate(text):
            angle = -90 + i * 180 / len(text)
            rad = math.radians(angle)
            x = cx + int(r * 1.2 * math.cos(rad)) - 15
            y = cy + int(r * 1.2 * math.sin(rad)) - 10
            draw.text((x, y), char, font=font, fill=color)

    # "POLES" at top/bottom
    poles_progress = clamp((progress - 0.4) / 0.3, 0, 1)
    if poles_progress > 0:
        font = load_font("Cinzel", 40, "bold")
        color = hex_to_rgba(colors["primary"], poles_progress)
        draw.text((cx - 40, cy - r - 80), "POLES", font=font, fill=color)
        draw.text((cx - 40, cy + r + 40), "POLES", font=font, fill=color)

    # "CONTINENTS RISE" at equator
    continents_progress = clamp((progress - 0.6) / 0.3, 0, 1)
    if continents_progress > 0:
        font = load_font("Libre Baskerville", 28, "italic")
        color = hex_to_rgba(colors["gold"], continents_progress)
        draw.text((cx - 120, cy + r + 100), "CONTINENTS RISE", font=font, fill=color)


# ========== SCENE 5: MAGNETIC ==========
def draw_magnetic_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Earth
    earth_r = int(min(width, height) * 0.2)
    draw.ellipse([cx - earth_r, cy - earth_r, cx + earth_r, cy + earth_r], fill=(20, 20, 40, 255))

    # Magnetic field lines (gold loops) - decaying
    field_strength = 1 - ease_in_cubic(progress)
    num_loops = 12
    for i in range(num_loops):
        angle = i * 2 * math.pi / num_loops
        loop_r = int(earth_r * 1.5 * field_strength)
        if loop_r < earth_r:
            continue

        # Draw loop as ellipse
        alpha = int(200 * field_strength)
        color = (232, 168, 56, alpha)
        # Simplified: draw arcs
        for a in range(0, 180, 5):
            rad = math.radians(a)
            x1 = cx + int(loop_r * math.cos(rad) * math.cos(angle))
            y1 = cy + int(loop_r * math.sin(rad) * 0.5)
            x2 = cx + int(loop_r * math.cos(rad + 0.087) * math.cos(angle))
            y2 = cy + int(loop_r * math.sin(rad + 0.087) * 0.5)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

    # Solar particles penetrating (increasing)
    particle_rate = progress * 200
    for i in range(int(particle_rate)):
        p_seed = seed + i * 10 + int(t * 1000)
        angle = seeded_random(p_seed) * 2 * math.pi
        dist = earth_r + int(seeded_random(p_seed + 1) * 300)
        x = cx + int(dist * math.cos(angle))
        y = cy + int(dist * math.sin(angle) * 0.5)

        # Move toward Earth
        px = x + int((cx - x) * progress * 0.1)
        py = y + int((cy - y) * progress * 0.1)

        size = 2
        alpha = int(255 * seeded_random(p_seed + 2))
        draw.ellipse([px, py, px + size, py + size], fill=(255, 255, 255, alpha))

        # Impact spark on atmosphere
        if dist < earth_r + 50:
            spark_alpha = int(255 * (1 - progress))
            draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(255, 50, 0, spark_alpha))

    # Atmosphere fading
    atmo_alpha = int(150 * field_strength)
    for r in range(earth_r, earth_r + 40):
        a = int(atmo_alpha * (1 - (r - earth_r) / 40))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 180, 216, a))

    # Text: "MAGNETIC FIELD" (fading)
    field_progress = field_strength
    if field_progress > 0:
        font = load_font("Cinzel", 48, "bold")
        color = hex_to_rgba(colors["gold"], field_progress)
        text = "MAGNETIC FIELD"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2] // 2, cy - earth_r - 100), text, font=font, fill=color)

    # "COLLAPSES" (impact flash)
    collapse_progress = clamp((progress - 0.3) / 0.2, 0, 1)
    if collapse_progress > 0:
        font = load_font("Cinzel", 72, "bold")
        color = hex_to_rgba(colors["red"], collapse_progress)
        text = "COLLAPSES"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2] // 2, cy - earth_r - 100), text, font=font, fill=color)
        # Flash
        if collapse_progress < 0.3:
            flash_alpha = int(200 * (1 - collapse_progress / 0.3))
            draw.rectangle([0, 0, width, height], fill=(255, 50, 0, flash_alpha))

    # "RADIATION" counter
    rad_progress = clamp((progress - 0.5) / 0.3, 0, 1)
    if rad_progress > 0:
        font = load_font("Space Mono", 36, "bold")
        color = hex_to_rgba(colors["red"], rad_progress)
        val = int(10000 * progress)
        text = f"RADIATION: {val:,}/s"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((50, 50), text, font=font, fill=color)


# ========== SCENE 6: TEMPERATURE ==========
def draw_temperature_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Split screen: left (day/heat), right (night/cold)
    # Left thermometer
    left_x = cx - 300
    therm_w = 80
    therm_h = 500
    therm_y = cy - therm_h // 2

    # Day side background (red gradient)
    for x in range(0, cx):
        p = x / cx
        r = int(lerp(50, 100, p))
        g = int(lerp(10, 0, p))
        b = 10
        draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))

    # Right side background (blue gradient)
    for x in range(cx, width):
        p = (x - cx) / (width - cx)
        r = 10
        g = int(lerp(10, 30, p))
        b = int(lerp(50, 100, p))
        draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))

    # Mercury level (day) - rising
    day_progress = ease_out_expo(progress)
    mercury_h_day = int(therm_h * 0.9 * day_progress)
    mercury_y_day = therm_y + therm_h - mercury_h_day
    draw.rounded_rectangle([left_x, mercury_y_day, left_x + therm_w, therm_y + therm_h], radius=therm_w//2,
                           fill=(255, 50, 0, 255))

    # Glass crack on day side (appears near top)
    if day_progress > 0.8:
        crack_progress = (day_progress - 0.8) / 0.2
        for i in range(int(5 * crack_progress)):
            cx_crack = left_x + therm_w // 2 + int(seeded_random(seed + i) * 20 - 10)
            cy_crack = therm_y + int(seeded_random(seed + i + 10) * therm_h * 0.3)
            draw.line([(cx_crack, cy_crack), (cx_crack + int(seeded_random(seed + i + 20) * 30), cy_crack - 20)],
                      fill=(255, 255, 255, 200), width=2)

    # Mercury level (night) - falling
    night_progress = ease_out_expo(progress)
    mercury_h_night = int(therm_h * 0.9 * (1 - night_progress))
    mercury_y_night = therm_y + therm_h - mercury_h_night
    right_x = cx + 220
    draw.rounded_rectangle([right_x, mercury_y_night, right_x + therm_w, therm_y + therm_h], radius=therm_w//2,
                           fill=(0, 100, 255, 255))

    # Frost on night side (at bottom)
    if night_progress > 0.7:
        frost_progress = (night_progress - 0.7) / 0.3
        for i in range(int(20 * frost_progress)):
            fx = right_x + int(seeded_random(seed + i + 100) * therm_w)
            fy = therm_y + therm_h - int(seeded_random(seed + i + 200) * therm_h * 0.5)
            fh = int(seeded_random(seed + i + 300) * 30)
            draw.line([(fx, fy), (fx + int(seeded_random(seed + i + 400) * 5), fy - fh)],
                      fill=(150, 200, 255, 200), width=1)

    # Temperature numbers
    day_temp = int(100 * day_progress)
    night_temp = int(-100 * night_progress)

    font = load_font("Space Mono", 64, "bold")
    draw.text((left_x - 20, therm_y - 100), f"+{day_temp}°C", font=font, fill=(255, 200, 0, 255))
    draw.text((right_x - 20, therm_y - 100), f"{night_temp}°C", font=font, fill=(0, 200, 255, 255))

    # "BEYOND SURVIVAL" center
    survival_progress = clamp((progress - 0.5) / 0.3, 0, 1)
    if survival_progress > 0:
        font = load_font("Libre Baskerville", 48, "italic")
        color = hex_to_rgba(colors["primary"], survival_progress)
        text = "BEYOND SURVIVAL"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2] // 2, cy + 150), text, font=font, fill=color)

    # Labels
    label_font = load_font("Libre Baskerville", 24, "regular")
    draw.text((left_x - 30, therm_y + therm_h + 30), "ETERNAL DAY", font=label_font, fill=(200, 200, 200, 255))
    draw.text((right_x - 30, therm_y + therm_h + 30), "ETERNAL NIGHT", font=label_font, fill=(200, 200, 200, 255))


# ========== SCENE 7: LIFE ==========
def draw_life_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Dark ocean background
    draw.rectangle([0, 0, width, height], fill=(5, 10, 20, 255))

    # Hydrothermal vent (center-bottom)
    vent_x = cx
    vent_y = cy + 100
    vent_w = 60
    vent_h = 200

    # Vent chimney
    draw.rounded_rectangle([vent_x - vent_w//2, vent_y - vent_h, vent_x + vent_w//2, vent_y],
                           radius=vent_w//2, fill=(40, 30, 20, 255))

    # Vent plume (turbulent, teal/gold)
    plume_progress = progress
    for y in range(vent_h):
        p = y / vent_h
        plume_w = int(vent_w * (1 + p * 2))
        alpha = int(150 * (1 - p) * plume_progress)
        r = int(lerp(0, 232, p))
        g = int(lerp(180, 168, p))
        b = int(lerp(216, 56, p))
        draw.ellipse([vent_x - plume_w//2, vent_y - y - 10, vent_x + plume_w//2, vent_y - y + 10],
                     fill=(r, g, b, alpha))

    # Extremophile microbes (gold rods) near vent
    for i in range(30):
        m_seed = seed + i * 50
        angle = seeded_random(m_seed) * 2 * math.pi
        dist = 50 + seeded_random(m_seed + 1) * 150
        mx = vent_x + int(dist * math.cos(angle))
        my = vent_y - int(dist * math.sin(angle) * 0.5)  # flattened

        # Brownian motion
        mx += int(math.sin(t * 3 + i) * 5)
        my += int(math.cos(t * 2 + i) * 3)

        # Microbe: rod shape
        length = 12
        width_m = 3
        angle_m = seeded_random(m_seed + 2) * 2 * math.pi
        # Draw as rotated rectangle (simplified: ellipse)
        alpha = int(200 + 55 * math.sin(t * 2 + i))
        draw.ellipse([mx - length//2, my - width_m//2, mx + length//2, my + width_m//2],
                     fill=(232, 168, 56, alpha))

    # Bioluminescence pulses
    for i in range(10):
        pulse = (math.sin(t * 1.5 + i) + 1) / 2
        px = vent_x + int(seeded_random(seed + i * 100) * 200 - 100)
        py = vent_y - int(seeded_random(seed + i * 100 + 1) * 150)
        size = int(5 + pulse * 15)
        draw.ellipse([px - size, py - size, px + size, py + size],
                     fill=(232, 168, 56, int(pulse * 100)))

    # Camera descent effect (vignette increases)
    descent_progress = progress
    vignette_amount = 0.1 + descent_progress * 0.3

    # Text: "EXTREMOPHILES" (floating with microbes)
    extrem_progress = clamp((progress - 0.1) / 0.3, 0, 1)
    if extrem_progress > 0:
        font = load_font("Cinzel", 56, "bold")
        color = hex_to_rgba(colors["gold"], extrem_progress)
        text = "EXTREMOPHILES"
        # Floating position
        fx = cx + int(math.sin(t * 0.5) * 50)
        fy = cy - 100 + int(math.cos(t * 0.3) * 30)
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((fx - bbox[2]//2, fy), text, font=font, fill=color)

    # "ENDURE" fade in
    endure_progress = clamp((progress - 0.4) / 0.3, 0, 1)
    if endure_progress > 0:
        font = load_font("Libre Baskerville", 40, "italic")
        color = hex_to_rgba(colors["primary"], endure_progress)
        text = "ENDURE"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2]//2, cy + 50), text, font=font, fill=color)

    # "LIFE FINDS A WAY" (final hold)
    way_progress = clamp((progress - 0.7) / 0.3, 0, 1)
    if way_progress > 0:
        font = load_font("Cinzel", 64, "bold")
        color = hex_to_rgba(colors["gold"], way_progress)
        text = "LIFE FINDS A WAY"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2]//2, cy + 150), text, font=font, fill=color)


# ========== SCENE 8: OUTRO ==========
def draw_outro_scene(draw: ImageDraw.Draw, beat: Dict, progress: float, t: float, width: int, height: int, colors: Dict, seed: int):
    cx, cy = width // 2, height // 2

    # Starfield
    draw_starfield(draw, width, height, seed, 0.001)

    # Earth (static, no rotation) - scaling down
    earth_r = int(min(width, height) * 0.25)
    scale = lerp(1.0, 0.7, progress)
    scaled_r = int(earth_r * scale)

    # Earth with simple texture suggestion
    for r in range(scaled_r, 0, -1):
        p = r / scaled_r
        alpha = int(200 * (1 - p * 0.5))
        color = (int(30 * p), int(80 * p), int(150 * p), alpha)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color)

    # Fade to starfield (overlay)
    fade_alpha = int(255 * progress)
    draw.rectangle([0, 0, width, height], fill=(10, 10, 26, fade_alpha))

    # Channel logo (placeholder - circle with text)
    logo_progress = clamp((progress - 0.1) / 0.4, 0, 1)
    logo_easing = ease_out_back(logo_progress)
    if logo_progress > 0:
        logo_r = int(80 * logo_easing)
        # Logo background
        draw.ellipse([cx - logo_r, cy - logo_r - 50, cx + logo_r, cy + logo_r - 50],
                     fill=(20, 20, 40, int(255 * logo_easing)), outline=(232, 168, 56, int(255 * logo_easing)), width=3)
        # Logo text
        font = load_font("Cinzel", int(36 * logo_easing), "bold")
        color = hex_to_rgba(colors["gold"], logo_easing)
        text = "WHAT IF"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2]//2, cy - 50 - bbox[3]//2), text, font=font, fill=color)

    # Subscribe button
    btn_progress = clamp((progress - 0.4) / 0.3, 0, 1)
    btn_easing = ease_out_cubic(btn_progress)
    if btn_progress > 0:
        btn_w = 300
        btn_h = 60
        btn_x = cx - btn_w // 2
        btn_y = cy + 100

        # Gradient button
        for py in range(btn_h):
            p = py / btn_h
            r = int(lerp(232, 255, p))
            g = int(lerp(168, 204, p))
            b = int(lerp(56, 0, p))
            a = int(255 * btn_easing)
            draw.line([(btn_x, btn_y + py), (btn_x + btn_w, btn_y + py)], fill=(r, g, b, a))

        # Shimmer sweep
        shimmer_x = btn_x + int((btn_w + 100) * ((t * 0.5) % 1)) - 50
        if btn_x < shimmer_x < btn_x + btn_w:
            for py in range(btn_h):
                draw.line([(shimmer_x, btn_y + py), (shimmer_x + 20, btn_y + py)], fill=(255, 255, 255, 100))

        draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), 30, outline=(0, 0, 0, 0), width=0)

        # Button text
        font = load_font("Cinzel", 28, "bold")
        color = (0, 0, 0, int(255 * btn_easing))
        text = "SUBSCRIBE"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2]//2, btn_y + btn_h//2 - bbox[3]//2), text, font=font, fill=color)

    # "What If... continues"
    continues_progress = clamp((progress - 0.6) / 0.3, 0, 1)
    if continues_progress > 0:
        font = load_font("Libre Baskerville", 32, "italic")
        color = hex_to_rgba(colors["primary"], continues_progress)
        text = "What If... continues"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2]//2, cy + 200), text, font=font, fill=color)

    # Channel URL
    url_progress = clamp((progress - 0.7) / 0.3, 0, 1)
    if url_progress > 0:
        font = load_font("Space Mono", 20, "regular")
        color = hex_to_rgba(colors["teal"], url_progress)
        text = "youtube.com/@whatif"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - bbox[2]//2, cy + 250), text, font=font, fill=color)


def draw_debug_info(draw: ImageDraw.Draw, t: float, frame_index: int, width: int, height: int, fps: int, scale: float, seed: int):
    font = load_font("Space Mono", 12, "regular")
    color = (255, 255, 255, 128)
    draw.text((10, 10), f"t={t:.3f}s frame={frame_index} seed={seed}", font=font, fill=color)
    draw.text((10, 30), f"{width}x{height} @ {fps}fps scale={scale}", font=font, fill=color)

    # Current beat
    for beat in BEATS:
        if beat["start"] <= t < beat["end"]:
            draw.text((10, 50), f"Beat: {beat['id']} ({beat['label']})", font=font, fill=(232, 168, 56, 200))
            break


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
            elif scene_id == "day_night":
                draw_day_night_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "atmosphere":
                draw_atmosphere_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "oceans":
                draw_oceans_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "magnetic":
                draw_magnetic_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "temperature":
                draw_temperature_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "life":
                draw_life_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)
            elif scene_id == "outro":
                draw_outro_scene(draw, beat, progress, t, width, height, CONFIG["colors"], seed)

    # Apply grain and vignette
    img = draw_grain_overlay(img, CONFIG["grain"], seed)
    img = draw_vignette(img, CONFIG["vignette"])

    draw_debug_info(draw, t, frame_index, width, height, fps, scale, seed)
    return img


def create_contact_sheet(frames_dir: Path, output_path: Path, cols: int = 6, thumb_width: int = 240):
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    if not frame_files:
        return

    rows = math.ceil(len(frame_files) / cols)
    thumb_height = int(thumb_width * 1080 / 1920)
    sheet_width = cols * thumb_width
    sheet_height = rows * (thumb_height + 30)

    sheet = Image.new("RGB", (sheet_width, sheet_height), (20, 20, 30))
    draw = ImageDraw.Draw(sheet)
    font = load_font("Space Mono", 10, "regular")

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