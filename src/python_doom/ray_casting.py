import math
from optparse import Values
from re import I
from this import d

import pygame as pg

from python_doom.maps import TILE_SIZE
from python_doom.settings import ScreenConfig as SCREEN
from python_doom.settings import GraphicConfig as GRAPHICS


class RayCasting:
    def __init__(self, game):
        self.game = game

        self.objects = []
        self.textures = self.game.renderer.wall_textures

    def get_objects_to_render(self):
        self.objects = []
        for ray, value in enumerate(self.casted_rays):
            depth, proj_height, texture, offset = value

            wall_column = self.textures[texture].subsurface(
                offset * (GRAPHICS.texture_size - GRAPHICS.scaling), 0, GRAPHICS.scaling, GRAPHICS.texture_size
            )
            wall_column = pg.transform.scale(wall_column,(GRAPHICS.scaling, int(proj_height)))
            wall_position = (ray * GRAPHICS.scaling, SCREEN.half_height - proj_height // 2)

            self.objects.append((depth, wall_column, wall_position))

    def ray_cast(self):
        self.casted_rays = []

        x_player, y_player = self.game.player.position
        x_tile, y_tile = self.game.player.tile_position

        texture_vert, texture_hor = 1, 1

        ray_angle = self.game.player.heading - GRAPHICS.half_fov
        for ray in range(GRAPHICS.number_rays):
            a_sin = math.sin(ray_angle)
            a_cos = math.cos(ray_angle)

            # Check vertically
            #   determine starting position in x
            y_hor, dy = (y_tile + 1, 1) if a_sin > 0 else (y_tile - 1e-6, -1)

            #   determine starting postion in y
            depth_hor = (y_hor - y_player) / a_sin
            x_hor = x_player + depth_hor * a_cos

            #   determine dy, while dx is always 1
            delta_depth = dy / a_sin
            dx = delta_depth * a_cos

            # Iterate with dx and dy in max depth to find intersection
            # with obstacles
            for _ in range(GRAPHICS.max_depth):
                tile = (int(x_hor), int(y_hor))
                if tile in self.game.map.obstructed_tiles:
                    break
                x_hor += dx
                y_hor += dy

                depth_hor += delta_depth

            # Check vertically
            #   determine starting position in x
            x_vert, dx = (x_tile + 1, 1) if a_cos > 0 else (x_tile - 1e-6, -1)

            #   determine starting postion in y
            depth_vert = (x_vert - x_player) / a_cos
            y_vert = y_player + depth_vert * a_sin

            #   determine dy, while dx is always 1
            delta_depth = dx / a_cos
            dy = delta_depth * a_sin

            # Iterate with dx and dy in max depth to find intersection
            # with obstacles
            for _ in range(GRAPHICS.max_depth):
                tile = (int(x_vert), int(y_vert))
                if tile in self.game.map.obstructed_tiles:
                    texture_vert = self.game.map.obstructed_tiles[tile]
                    break
                x_vert += dx
                y_vert += dy

                depth_vert += delta_depth

            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if a_cos > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if a_sin > 0 else x_hor

            if GRAPHICS.mode_2d and GRAPHICS.debug_rays:
                pg.draw.line(
                    self.game.screen, (40, 250, 10),
                    (x_player * TILE_SIZE, y_player * TILE_SIZE),
                    (x_player * TILE_SIZE + TILE_SIZE * depth * a_cos,
                     y_player * TILE_SIZE + TILE_SIZE * depth * a_sin),
                    2
                )

            if not GRAPHICS.mode_2d:
                # Remove fishbowl effect
                depth *= math.cos(self.game.player.heading - ray_angle)

                proj_height = GRAPHICS.screen_dist / (depth + 1e-4)

                if not GRAPHICS.rendered:
                    color = (255 / (1 + depth ** 5 * 1e-5 * 2), 0, 0)

                    rect = pg.Rect(
                        ray * GRAPHICS.scaling, SCREEN.half_height - proj_height // 2,
                        GRAPHICS.scaling, proj_height
                    )
                    pg.draw.rect(self.game.screen, color, rect, 2)

                if GRAPHICS.rendered:
                    self.casted_rays.append((depth, proj_height, texture, offset))

            ray_angle += GRAPHICS.delta_angle


    # def _cast_ray()
    # def draw_ray()
    # def determine_depth(self, x, y, dx, dy, dd) -> float:
        # depth = 0
        # for _ in range(GRAPHICS.max_depth):
        #     if (int(x), int(y)) in self.game.map.obstructed_tiles:
        #         break
        #     x += dx
        #     y += dy

        #     depth += dd
        # return depth

    def update(self):
        self.ray_cast()
        self.get_objects_to_render()
