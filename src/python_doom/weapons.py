import pygame as pg
from collections import deque

from python_doom.sprites import AnimatedObject
from python_doom.rendering import RenderedObject
from python_doom.settings import ScreenConfig as SCREEN


SHOTGUN = {
    "path": 'resources/sprites/weapon/shotgun',
    "pos": (0, 0),
    "animation_time": 120,
    "scale": 0.5,
    "height_shift": 0
}


class Weapon(AnimatedObject):
    objects_to_render = []

    reloading = False
    damage = 50

    def __init__(self, game):
        self.game = game
        self.player = game.player

        super().__init__(game, **SHOTGUN)
        self.num_images = len(self.images)

        # Additional scaling/shifting to super class
        self.images = self._scale_weapon(self.images, 0.5)
        self.position = self._weapon_position(self.images[0])
        self.image = self.images[0]

    def update(self):
        if self.player.shot_fired:
            self.game.player.shot_fired = False
            self.reloading = True

        # Because of `depth` = 0, we don't call super().update()
        # -> manual creation of rendered object
        self._check_animation_time()
        self._animate_shooting()
        self.objects_to_render = [
            RenderedObject(0, self.image, self.position)
        ]

    def _animate_shooting(self):
        if self.reloading:
            if self._animate():
                self.reloading = False

    @staticmethod
    def _scale_weapon(images, scale):
        return deque(
            [pg.transform.smoothscale(
                image, (
                    int(image.get_width() * scale),
                    int(image.get_height() * scale)
                )
             ) for image in images]
        )

    @staticmethod
    def _weapon_position(image):
        return (
            SCREEN.half_width - image.get_width() // 2,
            SCREEN.height - image.get_height()
        )
