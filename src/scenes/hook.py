"""
Scene 1: Hook — The Freeze (0-5s)
Earth rotating in starfield, sudden freeze frame, camera push-in.
"""

from ..render import (
    draw_starfield, hex_to_rgba, load_font, lerp, clamp,
    ease_in_cubic, ease_out_expo, ease_out_cubic,
    seeded_random, CONFIG
)


def draw_hook_scene(draw, beat, progress, t, width, height, colors, seed):
    cx, cy = width // 2, height // 2

    # Starfield
    draw_starfield(draw, width, height, seed, 0.0008)

    # Earth circle
    earth_r = int(min(width, height) * 0.25)
    earth_progress = clamp(progress / 0.3, 0, 1)
    rotation_angle = lerp(0, -0.3, ease_in_cubic(earth_progress))

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