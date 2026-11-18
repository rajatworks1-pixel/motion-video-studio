"""
Scene modules for Earth Stopped Spinning video.
Each scene is a self-contained drawing function.
"""

from .hook import draw_hook_scene
from .day_night import draw_day_night_scene
from .atmosphere import draw_atmosphere_scene
from .oceans import draw_oceans_scene
from .magnetic import draw_magnetic_scene
from .temperature import draw_temperature_scene
from .life import draw_life_scene
from .outro import draw_outro_scene

__all__ = [
    "draw_hook_scene",
    "draw_day_night_scene",
    "draw_atmosphere_scene",
    "draw_oceans_scene",
    "draw_magnetic_scene",
    "draw_temperature_scene",
    "draw_life_scene",
    "draw_outro_scene",
]