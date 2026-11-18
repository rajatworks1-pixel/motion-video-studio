"""
Scene 8: Outro — What If Continues (52-60s)
Static Earth, channel logo, subscribe button, URL.
"""

from ..render import (
    draw_starfield, hex_to_rgba, load_font, lerp, clamp,
    ease_out_back, ease_out_cubic, seeded_random, CONFIG
)


def draw_outro_scene(draw, beat, progress, t, width, height, colors, seed):
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

        draw.rounded_rectangle((btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), radius=30, outline=(0, 0, 0, 0), width=0)

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