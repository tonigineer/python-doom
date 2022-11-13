import pygame as pg
from dataclasses import dataclass

from python_doom.settings import GraphicsConfig as GRAPHICS
from python_doom.maps import TILE_SIZE
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

    player_took_damage = False
    player_damage_time = None
    PLAYER_DAMAGE_ANIMATION_TIME = 200

    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        self.wall_textures = self._load_wall_textures()
        self.sky_texture = self._load_sky_texture()

        self.digits = self._load_digits()
        self.blood_screen = self._load_blood_screen()

    def draw(self):
        if not GRAPHICS.mode_2d:
            self._draw_sky()
            self._draw_floor()
        self._render_objects()

    def render_win(self):
        self.screen.blit(self._load_win_screen(), (0, 0))

    def render_loss(self):
        self.screen.blit(self._load_lose_screen(), (0, 0))

    def render_player_health(self):
        for idx, char in enumerate(str(self.game.player.health)):
            self.screen.blit(
                self.digits[int(char)],
                (idx * GRAPHICS.player_health_size, 0)
            )

    def render_player_damage(self):
        if self.player_took_damage:
            now = pg.time.get_ticks()
            if not self.player_damage_time:
                self.player_damage_time = now

            self.screen.blit(self.blood_screen, (0, 0))

            if (now - self.player_damage_time) > \
               self.PLAYER_DAMAGE_ANIMATION_TIME:
                self.player_took_damage = False
                self.player_damage_time = None

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
            self.game.sprites_handler.objects_to_render + \
            self.game.weapon.objects_to_render + \
            self.game.npc_handler.objects_to_render

        all_objects = sorted(
            all_objects, key=lambda obj: obj.depth, reverse=True
        )

        for obj in all_objects:
            self.screen.blit(obj.image, obj.position)

        self.render_player_health()
        self.render_player_damage()

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

    @classmethod
    def _load_blood_screen(cls):
        return cls._grab_texture(
            f'resources/textures/blood_screen.png',
            (SCREEN.width, SCREEN.height)
        )

    @classmethod
    def _load_lose_screen(cls):
        return cls._grab_texture(
            f'resources/textures/game_over.png',
            (SCREEN.width, SCREEN.height)
        )

    @classmethod
    def _load_win_screen(cls):
        return cls._grab_texture(
            f'resources/textures/win.png',
            (SCREEN.width, SCREEN.height)
        )

    @classmethod
    def _load_digits(cls):
        return {
            _: cls._grab_texture(
                f'resources/textures/digits/{_}.png',
                (GRAPHICS.player_health_size, GRAPHICS.player_health_size)
            )
            for _ in range(0, 10)
        }
