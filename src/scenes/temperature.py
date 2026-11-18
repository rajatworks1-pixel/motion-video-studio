"""
Scene 6: Temperature — Beyond Survival (36-44s)
Split thermometers: day rising to 100°C, night falling to -100°C.
"""

from ..render import (
    hex_to_rgba, load_font, lerp, clamp,
    ease_out_expo, seeded_random, CONFIG
)
import math


def draw_temperature_scene(draw, beat, progress, t, width, height, colors, seed):
    cx, cy = width // 2, height // 2

    # Left background (red gradient)
    for x in range(0, cx):
        p = x / cx
        r = int(lerp(50, 100, p))
        g = int(lerp(10, 0, p))
        b = 10
        draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))

    # Right background (blue gradient)
    for x in range(cx, width):
        p = (x - cx) / (width - cx)
        r = 10
        g = int(lerp(10, 30, p))
        b = int(lerp(50, 100, p))
        draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))

    # Thermometers
    left_x = cx - 300
    therm_w = 80
    therm_h = 500
    therm_y = cy - therm_h // 2

    # Day mercury (rising)
    day_progress = ease_out_expo(progress)
    mercury_h_day = int(therm_h * 0.9 * day_progress)
    mercury_y_day = therm_y + therm_h - mercury_h_day
    draw.rounded_rectangle([left_x, mercury_y_day, left_x + therm_w, therm_y + therm_h], radius=therm_w//2,
                           fill=(255, 50, 0, 255))

    # Glass crack on day side
    if day_progress > 0.8:
        crack_progress = (day_progress - 0.8) / 0.2
        for i in range(int(5 * crack_progress)):
            cx_crack = left_x + therm_w // 2 + int(seeded_random(seed + i) * 20 - 10)
            cy_crack = therm_y + int(seeded_random(seed + i + 10) * therm_h * 0.3)
            draw.line([(cx_crack, cy_crack), (cx_crack + int(seeded_random(seed + i + 20) * 30), cy_crack - 20)],
                      fill=(255, 255, 255, 200), width=2)

    # Night mercury (falling)
    night_progress = ease_out_expo(progress)
    mercury_h_night = int(therm_h * 0.9 * (1 - night_progress))
    mercury_y_night = therm_y + therm_h - mercury_h_night
    right_x = cx + 220
    draw.rounded_rectangle([right_x, mercury_y_night, right_x + therm_w, therm_y + therm_h], radius=therm_w//2,
                           fill=(0, 100, 255, 255))

    # Frost on night side
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