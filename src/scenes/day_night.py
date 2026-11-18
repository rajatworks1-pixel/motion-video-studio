"""
Scene 2: Day/Night — Eternal Extremes (5-12s)
Split screen: blinding day side / frozen night side.
"""

from ..render import (
    hex_to_rgba, load_font, lerp, clamp,
    ease_out_cubic, ease_out_expo, perlin_noise, CONFIG
)


def draw_day_night_scene(draw, beat, progress, t, width, height, colors, seed):
    cx, cy = width // 2, height // 2

    # Split line position (expands from center)
    split_progress = ease_out_cubic(progress)
    left_width = int(cx * split_progress)
    right_start = width - left_width

    # Day side (left) - heat shimmer
    for x in range(left_width):
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