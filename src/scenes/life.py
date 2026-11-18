"""
Scene 7: Life — Extremophiles Endure (44-52s)
Microscopic view: archaea at hydrothermal vent, camera descends.
"""

from ..render import (
    hex_to_rgba, load_font, lerp, clamp,
    ease_out_back, seeded_random, CONFIG
)
import math


def draw_life_scene(draw, beat, progress, t, width, height, colors, seed):
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
    for y in range(vent_h):
        p = y / vent_h
        plume_w = int(vent_w * (1 + p * 2))
        alpha = int(150 * (1 - p) * progress)
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
        my = vent_y - int(dist * math.sin(angle) * 0.5)

        # Brownian motion
        mx += int(math.sin(t * 3 + i) * 5)
        my += int(math.cos(t * 2 + i) * 3)

        # Microbe: rod shape
        alpha = int(200 + 55 * math.sin(t * 2 + i))
        draw.ellipse([mx - 6, my - 2, mx + 6, my + 2],
                     fill=(232, 168, 56, alpha))

    # Bioluminescence pulses
    for i in range(10):
        pulse = (math.sin(t * 1.5 + i) + 1) / 2
        px = vent_x + int(seeded_random(seed + i * 100) * 200 - 100)
        py = vent_y - int(seeded_random(seed + i * 100 + 1) * 150)
        size = int(5 + pulse * 15)
        draw.ellipse([px - size, py - size, px + size, py + size],
                     fill=(232, 168, 56, int(pulse * 100)))

    # Text: "EXTREMOPHILES" (floating)
    extrem_progress = clamp((progress - 0.1) / 0.3, 0, 1)
    if extrem_progress > 0:
        font = load_font("Cinzel", 56, "bold")
        color = hex_to_rgba(colors["gold"], extrem_progress)
        text = "EXTREMOPHILES"
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