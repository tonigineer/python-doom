import math
import pygame as pg
from dataclasses import dataclass

from python_doom.maps import TILE_SIZE
from python_doom.settings import ScreenConfig as SCREEN
from python_doom.settings import GraphicConfig as GRAPHICS

from python_doom.rendering import RenderedObject


@dataclass
class Ray:
    depth: float
    texture_id: int
    texture_offset: float
    projection_height: float


class RayCasting:
    def __init__(self, game):
        self.game = game

        self.objects_to_render = []
        self.textures = self.game.renderer.wall_textures

    def update(self):
        self._scan_field_of_view()
        self._get_objects_to_render()

    def _get_objects_to_render(self):
        self.objects_to_render = []
        for ray_id, ray in enumerate(self.casted_rays):

            # TODO Better naming!
            y = SCREEN.half_height - ray.projection_height // 2
            h = GRAPHICS.texture_size
            b = 0
            hh = int(ray.projection_height)

            # Limit object in height when getting close
            if ray.projection_height >= SCREEN.height:
                y = 0
                h = GRAPHICS.texture_size * SCREEN.height / ray.projection_height
                b = GRAPHICS.half_texture_size - h // 2
                hh = SCREEN.height

            wall_column = self.textures[ray.texture_id].subsurface(
                ray.texture_offset * (
                    GRAPHICS.texture_size - GRAPHICS.scaling
                ),
                b, GRAPHICS.scaling, h
            )

            wall_column = pg.transform.scale(
                wall_column, (GRAPHICS.scaling, hh)
            )

            wall_position = (ray_id * GRAPHICS.scaling, y)

            self.objects_to_render.append(
                RenderedObject(
                    ray.depth, wall_column, wall_position
                )
            )

    def _scan_field_of_view(self):
        self.casted_rays = []

        self.x_player, self.y_player = self.game.player.position
        self.x_tile, self.y_tile = self.game.player.tile_position

        ray_angle = self.game.player.heading - GRAPHICS.half_fov
        for ray_id in range(GRAPHICS.number_rays):
            a_sin = math.sin(ray_angle)
            a_cos = math.cos(ray_angle)

            depth, texture_id, offset = self._cast_ray(a_sin, a_cos)

            if GRAPHICS.mode_2d and GRAPHICS.debug_rays:
                self._draw_ray(
                    self.game.screen, self.x_player, self.y_player,
                    depth, a_sin, a_cos
                )

            if not GRAPHICS.mode_2d:
                depth *= math.cos(
                    self.game.player.heading - ray_angle
                )  # remove fishbowl effects
                proj_height = GRAPHICS.screen_dist / (depth + 1e-4)

                if not GRAPHICS.debug_render_textures:
                    self._draw_object_frame(
                        self.game.screen, ray_id, depth, proj_height
                    )

                if GRAPHICS.debug_render_textures:
                    self.casted_rays.append(Ray(
                        depth, texture_id, offset, proj_height
                    ))

            ray_angle += GRAPHICS.delta_angle

    def _cast_ray(self, a_sin: float, a_cos: float):
        """Cast a ray and determine information of intercepted object.

        There calculation is separated into vertical and horizontal
        direction.

        TODO: refactor to get rid of duplicated code.
        """
        texture_vert_id, texture_hor_id = 1, 1

        # Check horizontally
        y_hor, dy = (self.y_tile + 1, 1) if a_sin > 0 else (self.y_tile - 1e-6, -1)

        depth_hor = (y_hor - self.y_player) / a_sin
        x_hor = self.x_player + depth_hor * a_cos

        delta_depth = dy / a_sin
        dx = delta_depth * a_cos

        for _ in range(GRAPHICS.max_depth):
            tile = (int(x_hor), int(y_hor))
            if tile in self.game.map.obstructed_tiles:
                texture_hor_id = self.game.map.obstructed_tiles[tile]
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # Check vertically
        x_vert, dx = (self.x_tile + 1, 1) if a_cos > 0 else (self.x_tile - 1e-6, -1)

        depth_vert = (x_vert - self.x_player) / a_cos
        y_vert = self.y_player + depth_vert * a_sin

        delta_depth = dx / a_cos
        dy = delta_depth * a_sin

        for _ in range(GRAPHICS.max_depth):
            tile = (int(x_vert), int(y_vert))
            if tile in self.game.map.obstructed_tiles:
                texture_vert_id = self.game.map.obstructed_tiles[tile]
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        # Determine texture offset of closest depth
        if depth_vert < depth_hor:
            depth, texture_id = depth_vert, texture_vert_id
            y_vert %= 1
            texture_offset = y_vert if a_cos > 0 else (1 - y_vert)
        else:
            depth, texture_id = depth_hor, texture_hor_id
            x_hor %= 1
            texture_offset = (1 - x_hor) if a_sin > 0 else x_hor

        return depth, texture_id, texture_offset

    @staticmethod
    def _draw_ray(screen, x, y, depth, a_sin, a_cos):
        LINE_WIDTH = 2
        COLOR = (40, 250, 10)

        pg.draw.line(
            screen, COLOR,
            (x * TILE_SIZE, y * TILE_SIZE),
            (x * TILE_SIZE + TILE_SIZE * depth * a_cos,
             y * TILE_SIZE + TILE_SIZE * depth * a_sin),
            LINE_WIDTH
        )

    @staticmethod
    def _draw_object_frame(screen, ray_id, depth, proj_height):
        LINE_WIDTH = 2
        color = (255 / (1 + depth ** 5 * 1e-5 * 2), 0, 0)

        rect = pg.Rect(
            ray_id * GRAPHICS.scaling, SCREEN.half_height - proj_height // 2,
            GRAPHICS.scaling, proj_height
        )
        pg.draw.rect(screen, color, rect, LINE_WIDTH)
