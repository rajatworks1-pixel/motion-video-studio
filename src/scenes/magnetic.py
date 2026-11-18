"""
Scene 5: Magnetic — Field Collapse (28-36s)
Magnetic field lines decaying, solar particles penetrating.
"""

from ..render import (
    hex_to_rgba, load_font, lerp, clamp,
    ease_in_cubic, ease_out_expo, seeded_random, CONFIG
)
import math


def draw_magnetic_scene(draw, beat, progress, t, width, height, colors, seed):
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

        alpha = int(200 * field_strength)
        color = (232, 168, 56, alpha)
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
    if field_strength > 0:
        font = load_font("Cinzel", 48, "bold")
        color = hex_to_rgba(colors["gold"], field_strength)
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