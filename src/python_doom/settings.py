import math

from dataclasses import dataclass
from operator import truediv


@dataclass
class ScreenConfig:
    width: int = 1600
    height: int = 900
    half_width: int = width // 2
    half_height: int = height // 2
    fps: int = 60


@dataclass
class PlayerConfig:
    position: tuple = 14.9, 7.9
    heading: float = 3.825
    movement_speed: float = 0.004
    turn_rate: float = 0.002
    debug_heading: bool = True


@dataclass
class GraphicConfig:
    mode_2d: bool = False

    field_of_view: float = math.pi / 3
    half_fov: float = field_of_view / 2
    number_rays: int = ScreenConfig.width // 10
    half_number_rays: int = number_rays // 2
    delta_angle: float = field_of_view / number_rays
    max_depth: int = 20

    screen_dist: float = ScreenConfig.half_width / math.tan(half_fov)
    scaling: float = ScreenConfig.width // number_rays

    debug_rays: bool = True  # 2D only
    rendered: bool = True

    texture_size = 256
    half_texture_size = texture_size // 2
