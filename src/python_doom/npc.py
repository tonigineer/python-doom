import numpy as np
import pygame as pg

from python_doom.sprites import AnimatedObject
from python_doom.settings import GraphicsConfig as GRAPHICS
from python_doom.maps import TILE_SIZE
from python_doom.settings import ScreenConfig as SCREEN

STARTING_NPC = [{
    "path": 'resources/sprites/npc/soldier',
    "pos": (10, 5),
    "animation_time": 180,
    "scale": 0.6,
    "height_shift": 0.38,
    "speed": 0.03,
    "size": 10,
    "health": 100,
    "damage": 10,
    "accuracy": 0.15,
}]


class NpcHandler:
    all_npc = []
    objects_to_render = []

    def __init__(self, game):
        self.game = game

        for entity in STARTING_NPC:
            self.all_npc.append(
                Npc(game, **entity)
            )

    def update(self):
        self.objects_to_render = []

        for npc in self.all_npc:
            obj = npc.update()
            if obj:
                self.objects_to_render.append(obj)


class Npc(AnimatedObject):
    alive = True
    in_pain = False

    player_within_sight = False

    def __init__(self, game,
                 path, pos, animation_time, scale, height_shift,
                 speed, size, health, damage, accuracy):
        super().__init__(game, path, pos, animation_time, scale, height_shift)

        self.x, self.y = pos
        self.path = path
        self._read_all_animations()

        self.speed = speed
        self.size = size
        self.health = health
        self.damage = damage
        self.accuracy = accuracy

    def _read_all_animations(self):
        self.images_attack = self.grab_images(self.path + '/attack')
        self.images_death = self.grab_images(self.path + '/death')
        self.images_idle = self.grab_images(self.path + '/idle')
        self.images_pain = self.grab_images(self.path + '/pain')
        self.images_walk = self.grab_images(self.path + '/walk')

    def update(self):
        if GRAPHICS.mode_2d:
            if GRAPHICS.debug_line_of_sight:
                if self.player_within_sight:
                    self._draw_line_of_sight()
        self._npc_main_logic()
        return super().update()

    def _npc_main_logic(self):
        self.player_within_sight = self._check_line_of_sight()

        if self.in_pain:
            self.in_pain = False

        if self.alive:
            self._check_hit_from_player()
            if self.in_pain:
                self.game.sounds.npc_pain.play()
                self.image = self.images_pain[0]
            else:
                self.images = self.images_idle

    def _check_hit_from_player(self):
        if self.player.shot_fired:
            x_left = SCREEN.half_height - self.IMAGE_HALF_WIDTH
            x_right = SCREEN.half_width + self.IMAGE_HALF_WIDTH
            if x_left < self.x_screen < x_right:
                if not self.player_within_sight:
                    return
                self.in_pain = True

    def _check_line_of_sight(self):
        if self.player.tile_position == self.tile_position:
            return False

        dist_player = np.linalg.norm(
            np.array([self.player.position]) -
            np.array([self.position])
        )
        theta = np.arctan2(
            self.position[1]-self.player.position[1],
            self.position[0]-self.player.position[0]
        )
        dist_wall, _, _ = self.game.ray_caster._cast_ray(
            np.sin(theta),
            np.cos(theta)
        )
        return dist_player < dist_wall

    def _draw_line_of_sight(self):
        LINE_WIDTH = 2
        COLOR = (40, 250, 210)

        pg.draw.line(
            self.game.screen, COLOR,
            (self.x * TILE_SIZE, self.y * TILE_SIZE),
            (self.player.x * TILE_SIZE, self.player.y * TILE_SIZE),
            LINE_WIDTH
        )

    @property
    def position(self):
        return self.x, self.y

    @property
    def tile_position(self):
        return int(self.x), int(self.y)
