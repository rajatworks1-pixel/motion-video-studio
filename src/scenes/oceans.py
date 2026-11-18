"""
Scene 4: Oceans — Polar Surge (20-28s)
Top-down view: water rushing to poles, land emerging at equator.
"""

from ..render import (
    hex_to_rgba, load_font, lerp, clamp,
    ease_out_expo, seeded_random, CONFIG
)
import math


def draw_oceans_scene(draw, beat, progress, t, width, height, colors, seed):
    cx, cy = width // 2, height // 2

    # Top-down Earth circle
    r = int(min(width, height) * 0.35)

    # Ocean currents - water rushing to poles
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        pole_factor = abs(math.sin(rad))
        flow_progress = (progress + pole_factor * 0.5) % 1.0
        current_r = int(r * (0.3 + 0.7 * flow_progress))

        x1 = cx + int(current_r * math.cos(rad))
        y1 = cy + int(current_r * math.sin(rad))
        x2 = cx + int(r * math.cos(rad))
        y2 = cy + int(r * math.sin(rad))

        alpha = int(200 * pole_factor)
        draw.line([(x1, y1), (x2, y2)], fill=(0, 100, 200, alpha), width=3)

    # Land masses emerging at equator
    land_angles = [0, 45, 135, 180, 225, 315]
    land_progress = ease_out_expo(progress)
    for angle in land_angles:
        rad = math.radians(angle)
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