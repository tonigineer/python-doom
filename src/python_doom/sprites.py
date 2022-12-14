import os

import pygame as pg
import numpy as np

from collections import deque
from pathlib import Path

from python_doom.settings import ScreenConfig as SCREEN
from python_doom.settings import GraphicsConfig as GRAPHICS
from python_doom.maps import TILE_SIZE
from python_doom.settings import PlayerConfig as PLAYER

from python_doom.rendering import RenderedObject


STATICS = [
    # {"path": 'resources/sprites/static_sprites/candlebra.png', "pos": (12, 6), "scale": 0.85, "height_shift": 0.5}
]

ANIMATIONS = [
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (1.5, 1.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (1.5, 7.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (5.5, 3.25), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (5.5, 4.75), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (7.5, 2.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (7.5, 5.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (14.5, 1.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (14.5, 4.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (14.5, 24.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (14.5, 30.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (1.5, 30.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/green_light', "pos": (1.5, 24.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (14.5, 5.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (14.5, 7.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (12.5, 7.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (14.5, 12.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (9.5, 20.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (10.5, 20.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (3.5, 14.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
    {"path": 'resources/sprites/animated_sprites/red_light', "pos": (3.5, 18.5), "scale": 0.85, "height_shift": 0.25, "animation_time": 120},
]


class SpritesHandler:
    sprites = []
    objects_to_render = []

    def __init__(self, game):
        self.game = game

        for static in STATICS:
            self.sprites.append(
                SpriteObject(self.game, **static)
            )
        for animation in ANIMATIONS:
            self.sprites.append(
                AnimatedObject(self.game, **animation)
            )

    def update(self):
        self.objects_to_render = []

        for sprite in self.sprites:
            if GRAPHICS.mode_2d:
                self._draw_2d(sprite.x, sprite.y)
                continue
            obj = sprite.update()
            if obj:
                self.objects_to_render.append(obj)

    def _draw_2d(self, x, y, r=100):
        pg.draw.circle(
            self.game.screen, (200, 200, 0),
            (int(x * r), int(y * r)),
            15
        )


class SpriteObject:
    def __init__(self, game, path, pos, scale=1.0, height_shift=0.0):
        self.game = game
        self.player = game.player
        self.x, self.y = pos
        self.scale = scale
        self.height_shift = height_shift

        if Path(path).is_file():
            self._load_image(path)

    def _load_image(self, path):
        self.image = pg.image.load(path).convert_alpha()
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()

    def _project_spite(self):
        height = GRAPHICS.screen_dist / self.norm_dist * self.scale
        width = height * self.IMAGE_RATIO

        image = pg.transform.scale(self.image, (int(width), int(height)))

        half_width = width // 2
        position = self.x_screen - half_width, \
            SCREEN.half_height - height // 2 + height * self.height_shift

        if GRAPHICS.mode_2d:
            image = pg.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
            return RenderedObject(self.norm_dist, image, (
                    self.x * TILE_SIZE - TILE_SIZE // 2,
                    self.y * TILE_SIZE - TILE_SIZE // 2
                )
            )

        return RenderedObject(self.norm_dist, image, position)

    def _calculate_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        theta = np.arctan2(dy, dx)

        delta = theta - self.player.heading
        # NOTE here 2pi still missing
        if (dx > 0 and self.player.heading > np.pi) or (dx < 0 and dy < 0):
            delta += (np.pi * 2)

        delta_rays = delta / GRAPHICS.delta_angle
        self.x_screen = \
            (GRAPHICS.half_number_rays + delta_rays) * GRAPHICS.scaling

        self.dist = np.hypot(dx, dy)
        self.norm_dist = self.dist * np.cos(delta)

        if self.norm_dist < PLAYER.size:
            return None

        # Sprite is visible for player
        if -self.IMAGE_HALF_WIDTH < self.x_screen < (SCREEN.width + self.IMAGE_HALF_WIDTH):
            return self._project_spite()

    def _draw_2d_pos(self):
        self.game.screen
        pg.draw.circle(
            self.game.screen, (200, 200, 0),
            (int(self.x * TILE_SIZE), int(self.y * TILE_SIZE)),
            15, 2
        )

    def update(self):
        # if GRAPHICS.mode_2d:
        #     self._draw_2d_pos()
        #     return None
        return self._calculate_sprite()


class AnimatedObject(SpriteObject):
    images = []
    animation_counter = 0
    animation_finished = True

    def __init__(self, game, path, pos, animation_time, scale, height_shift):
        super().__init__(game, path, pos, scale, height_shift)
        self.animation_time = animation_time

        if not self.images:
            self.images = self.grab_images(path)
        self._check_images()

        self.prev_time = pg.time.get_ticks()
        self.animation_trigger = False

    def update(self):
        self._check_animation_time()
        self._animate()
        return super().update()

    def _animate(self) -> bool:
        if self.animation_trigger:
            if len(self.images) > 1:
                self.images.rotate(-1)
            self.image = self.images[0]
            self.animation_trigger = False

            self.animation_counter = \
                (self.animation_counter + 1) % len(self.images)
            self.animation_finished = self.animation_counter == 0
            return self.animation_finished

    def _check_animation_time(self):
        now = pg.time.get_ticks()
        self.dt_ani = (now - self.prev_time)
        if (now - self.prev_time) > self.animation_time:
            self.prev_time = now
            self.animation_trigger = True

    def _check_images(self):
        self.IMAGE_WIDTH = self.images[0].get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.images[0].get_height()

        # for image in self.images:
        #     assert image.get_width() == self.IMAGE_WIDTH
        #     assert image.get_height() == self.IMAGE_WIDTH / self.IMAGE_RATIO

        self.image = self.images[0]

    @staticmethod
    def grab_images(path: str) -> list:
        images = deque()
        files = [f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f))]
        for file in sorted(files):
            image = pg.image.load(os.path.join(path, file)).convert_alpha()
            images.append(image)
        return images
