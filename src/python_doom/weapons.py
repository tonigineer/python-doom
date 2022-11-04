import pygame as pg

from python_doom.sprites import AnimatedObject
from python_doom.rendering import RenderedObject
from python_doom.settings import ScreenConfig as SCREEN


SHOTGUN = {"path": 'resources/sprites/weapon/shotgun', "pos": None, "scale": 1, "height_shift": 0, "animation_time": 90}


class Weapon(AnimatedObject):
    object_to_render = []

    def __init__(self, game):
        self.game = game

        self.images = super().grab_images(SHOTGUN["path"])
        # SHOTGUN["pos"] = self._weapon_position(image)
        self.position = self._weapon_position(self.images[0])

        # super().__init__(game, **SHOTGUN)

    @staticmethod
    def _weapon_position(image):
        return (
            SCREEN.half_width - image.get_width() // 2,
            SCREEN.height - image.get_height()
        )

    def update(self):
        self._draw()

    def _draw(self):
        self.game.screen.blit(self.images[3], self.position)
