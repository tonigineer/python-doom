import math

from dataclasses import dataclass


@dataclass
class ScreenConfig:
    width: int = 1600
    height: int = 900
    half_width: int = width // 2
    half_height: int = height // 2
    fps: int = 144
    lock_fps: bool = True


@dataclass
class PlayerConfig:
    position: tuple = 14, 7
    heading: float = 3.825
    movement_speed: float = 0.004
    turn_rate: float = 0.002
    size: int = 0.3


@dataclass
class GraphicsConfig:
    mode_2d: bool = True
    # 2D
    debug_rays: bool = False
    debug_line_of_sight = True
    # 3D
    debug_render_textures: bool = True

    field_of_view: float = math.pi / 3
    half_fov: float = field_of_view / 2
    number_rays: int = ScreenConfig.width // 5
    half_number_rays: int = number_rays // 2
    delta_angle: float = field_of_view / number_rays
    max_depth: int = 20

    screen_dist: float = ScreenConfig.half_width / math.tan(half_fov)
    scaling: float = ScreenConfig.width // number_rays

    texture_size = 256
    half_texture_size = texture_size // 2

    floor_color = (30, 30, 30)


@dataclass
class ControlsConfig:
    mouse_sensitivity: float = 0.0003
    mouse_max_rel_move: int = 40
    mouse_border_left: int = 100
    mouse_border_right: int = ScreenConfig.width - mouse_border_left
