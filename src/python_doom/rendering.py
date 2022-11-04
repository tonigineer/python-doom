import pygame as pg
from dataclasses import dataclass

from python_doom.settings import GraphicConfig as GRAPHICS
from python_doom.settings import ScreenConfig as SCREEN


@dataclass
class RenderedObject:
    depth: float
    image: pg.Surface
    position: tuple


class Renderer:
    sky_offset = 0
    player_rel_move_factor = 4.5

    rendered_object = []

    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        self.wall_textures = self._load_wall_textures()
        self.sky_texture = self._load_sky_texture()

    def draw(self):
        self._draw_sky()
        self._draw_floor()
        self._render_objects()

    def _draw_sky(self):
        self.sky_offset = \
            (self.sky_offset + self.player_rel_move_factor *
             self.game.player.rel_move) % SCREEN.width

        self.screen.blit(
            self.sky_texture, (-self.sky_offset, 0)
        )
        self.screen.blit(
            self.sky_texture, (-self.sky_offset + SCREEN.width, 0)
        )

    def _draw_floor(self):
        pg.draw.rect(
            self.screen, GRAPHICS.floor_color,
            (0, SCREEN.half_height, SCREEN.width, SCREEN.half_height)
        )

    def _render_objects(self):
        all_objects = \
            self.game.ray_caster.objects_to_render + \
            self.game.sprites.objects_to_render + \
            self.game.weapon.object_to_render

        all_objects = sorted(
            all_objects, key=lambda obj: obj.depth, reverse=True
        )

        for obj in all_objects:
            self.screen.blit(obj.image, obj.position)

    @staticmethod
    def _grab_texture(path, res=(GRAPHICS.texture_size, GRAPHICS.texture_size)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    @classmethod
    def _load_wall_textures(cls):
        return {
            _: cls._grab_texture(f'resources/textures/{_}.png')
            for _ in range(1, 6)
        }

    @classmethod
    def _load_sky_texture(cls):
        return cls._grab_texture(
            f'resources/textures/sky.png',
            (SCREEN.width, SCREEN.half_height)
        )
