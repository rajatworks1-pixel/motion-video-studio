"""
Scene 3: Atmosphere — Supersonic Scour (12-20s)
Side view: atmosphere rushing, wind arrows, particles, shockwaves.
"""

from ..render import (
    hex_to_rgba, load_font, lerp, clamp,
    ease_out_expo, seeded_random, CONFIG
)


def draw_atmosphere_scene(draw, beat, progress, t, width, height, colors, seed):
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
    flow_speed = t * 500
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
        x_start = width * 0.1
        for i, char in enumerate(text):
            char_bbox = draw.textbbox((0, 0), char, font=font)
            char_w = char_bbox[2] - char_bbox[0]
            stretch = 1 + text_progress * 0.5
            x = x_start + i * char_w * stretch
            y = atmo_y - 60 + int(__import__('math').sin(t * 5 + i) * 5)
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