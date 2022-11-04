import pygame as pg
from collections import deque

from python_doom.sprites import AnimatedObject
from python_doom.settings import ScreenConfig as SCREEN


SHOTGUN = {"path": 'resources/sprites/weapon/shotgun', "pos": (0, 0), "scale": 0.4, "height_shift": 500, "animation_time": 90}


class Weapon(AnimatedObject):
    object_to_render = []

    reloading = False
    frame_counter = 0
    damage = 50

    def __init__(self, game):
        self.game = game
        self.player = game.player
        super().__init__(game, **SHOTGUN)

        # Re-grabbing images should be caught within super().__inti__() of animatedObject
        self.images = super().grab_images(SHOTGUN["path"])
        self.images = self._scale_weapon(self.images, 0.5)
        self.position = self._weapon_position(self.images[0])
        self.image = self.images[0]

        self.num_images = len(self.images)

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

    def update(self):
        print(self.player.shot_fired)
        print(self.reloading)
        if self.player.shot_fired:
            self.game.player.shot_fired = False
            self.reloading = True
        self._check_animation_time()
        self._animate_shooting()

    def draw(self):
        self.game.screen.blit(self.image, self.position)
