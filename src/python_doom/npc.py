from __future__ import annotations

import numpy as np
import pygame as pg

from random import choices, choice, random

from python_doom.sprites import AnimatedObject
from python_doom.maps import TILE_SIZE
from python_doom.path_finding import manhattan_dist

from python_doom.settings import GraphicsConfig as GRAPHICS
from python_doom.settings import ScreenConfig as SCREEN
from python_doom.settings import Difficulty as DIFFICULTY


class Npc(AnimatedObject):
    alive = True
    in_pain = False

    attacking = False
    player_within_sight = False
    player_pursuit = False
    path_to_player = []

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
        self._npc_main_logic()

        if GRAPHICS.mode_2d:
            self._draw_2d()
        return super().update()

    def _npc_main_logic(self):
        if not self.alive:
            # animation finish loops shortly to first frame of animation,
            # therefor we must take care ourself
            # if self.animation_finished:
            if self.animation_counter >= len(self.images_death)-1:
                self.images = [self.images_death[-1]]
                self.image = self.images_death[-1]
            return

        if self.attacking:
            if self.animation_finished:
                self.attacking = False
                if random() < self.accuracy:
                    self.player.take_damage(self.damage)

        if self.in_pain:
            self.in_pain = False

        self.player_within_sight = self._check_line_of_sight()
        self._check_hit_from_player()

        if self.in_pain:
            self.image = self.images_pain[0]

            self.health -= self.game.weapon.damage
            self._check_health()
            if self.alive:
                self.game.sounds.npc_pain.play()
            return

        if self.player_within_sight:
            self.player_pursuit = True
            # TODO: conditions to stop pursuing
            if self.dist_player < self.attack_distance:
                self._attack()
                return

        if self.player_pursuit:
            self.images = self.images_walk
            self.path_to_player = self.game.path_finding.get_path(
                self.tile_position, self.player.tile_position
            )

            self._movement()
            return

        self.images = self.images_idle

    def _check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sounds.npc_death.play()

            self.images = self.images_death
            self.animation_counter = 0
            if self.animation_finished:
                self.animation_finished = False
            self.animation_time *= 0.8

    def _check_hit_from_player(self):
        if self.player.shot_fired:
            x_left = SCREEN.half_height - self.IMAGE_HALF_WIDTH
            x_right = SCREEN.half_width + self.IMAGE_HALF_WIDTH
            if x_left < self.x_screen < x_right:
                if not self.player_within_sight:
                    return
                self.in_pain = True

    def _check_line_of_sight(self):
        if self.player.health <= 0:
            return False

        if self.player.tile_position == self.tile_position:
            return False

        self.dist_player = np.linalg.norm(
            np.array([self.player.position]) -
            np.array([self.position])
        )
        self.theta = np.arctan2(
            self.position[1]-self.player.position[1],
            self.position[0]-self.player.position[0]
        )
        dist_wall, _, _ = self.game.ray_caster.cast_ray(
            np.sin(self.theta),
            np.cos(self.theta)
        )
        return self.dist_player < dist_wall

    def _movement(self):
        # NOTE: penultimate tile is the next tile on the path to target
        target = self.path_to_player[-min(2, len(self.path_to_player))]
        if target in self.game.npc_handler.npc_positions:
            return

        if manhattan_dist(target, self.player.tile_position) < 2:
            return

        if not self.player_within_sight:
            # NOTE: 0.5 are added to target middle of tile
            theta = np.arctan2(
                self.position[1] - (target[1]+0.5),
                self.position[0] - (target[0]+0.5)
            )
        else:
            theta = np.arctan2(
                self.position[1]-self.player.position[1],
                self.position[0]-self.player.position[0]
            )

        dx = np.cos(theta+np.pi) * self.speed
        dy = np.sin(theta+np.pi) * self.speed

        self._check_collisions(dx, dy)

    def _attack(self):
        if self.animation_finished:
            self.images = self.images_attack
            self.image = self.images_attack[0]
            self.animation_counter = 0
            self.animation_finished = False
            self.attacking = True
            # self.game.sounds.npc_attack.play()

    def _draw_2d(self):
        LINE_WIDTH = 2
        COLOR = (255, 87, 51)
        RADIUS = 15

        if GRAPHICS.debug_line_of_sight:
            pg.draw.line(
                self.game.screen, COLOR,
                (self.x * TILE_SIZE, self.y * TILE_SIZE),
                (self.player.x * TILE_SIZE, self.player.y * TILE_SIZE),
                LINE_WIDTH
            )
        pg.draw.circle(
            self.game.screen, COLOR,
            (int(self.x * TILE_SIZE), int(self.y * TILE_SIZE)),
            RADIUS
        )

        [pg.draw.rect(
            self.game.screen,
            (100, 250, 18),
            (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE),
            2
        ) for pos in self.path_to_player]

    def _check_for_walls(self, x, y):
        for xs, ys in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            dx = xs * self.size
            dy = ys * self.size
            if (int(x+dx), int(y+dy)) in self.game.map.obstructed_tiles:
                return False
        return True

    def _check_for_npc(self, x, y) -> bool:
        for position in self.game.npc_handler.npc_positions:
            if position == self.tile_position:
                continue
            if manhattan_dist(position, (int(x), int(y))) <= 1:
                return False
        return True

    def _check_collisions(self, dx, dy):
        if self._check_for_walls(self.x + dx, self.y) and \
           self._check_for_npc(self.x + dx, self.y):
            self.x += dx
        if self._check_for_walls(self.x, self.y + dy) and \
           self._check_for_npc(self.x, self.y + dy):
            self.y += dy

    @property
    def position(self):
        return self.x, self.y

    @property
    def tile_position(self):
        return int(self.x), int(self.y)


class Soldier(Npc):

    path = 'resources/sprites/npc/soldier'
    animation_time = 120
    scale = 0.6
    height_shift = 0.38
    speed = 0.015
    size = 0.1
    health = 100
    damage = 5
    attack_distance = 4
    accuracy = 0.35

    def __init__(self, game, pos):
        super().__init__(
            game, self.path, pos, self.animation_time, self.scale,
            self.height_shift, self.speed, self.size, self.health,
            self.damage, self.accuracy
        )


class CacoDemon(Npc):

    path = 'resources/sprites/npc/caco_demon'
    animation_time = 250
    scale = 0.7
    height_shift = 0.27
    speed = 0.025
    size = 0.3
    health = 150
    damage = 30
    attack_distance = 3
    accuracy = 0.15

    def __init__(self, game, pos):
        super().__init__(
            game, self.path, pos, self.animation_time, self.scale,
            self.height_shift, self.speed, self.size, self.health,
            self.damage, self.accuracy
        )


class CyberDemon(Npc):

    path = 'resources/sprites/npc/cyber_demon'
    animation_time = 210
    scale = 1.0
    height_shift = 0.04
    speed = 0.0055
    size = 0.2
    health = 350
    damage = 15
    attack_distance = 5.5
    accuracy = 0.25

    def __init__(self, game, pos):
        super().__init__(
            game, self.path, pos, self.animation_time, self.scale,
            self.height_shift, self.speed, self.size, self.health,
            self.damage, self.accuracy
        )


class NpcHandler:
    all_npc = []
    objects_to_render = []

    NPC_TYPES = [Soldier, CacoDemon, CyberDemon]

    def __init__(self, game):
        self.game = game

        self.populate_map()

    def update(self):
        self.objects_to_render = []

        for npc in self.all_npc:
            self.npc_positions = \
                [npc.tile_position for npc in self.all_npc
                 if npc.alive and
                    npc.tile_position is not self.game.player.tile_position]

            obj = npc.update()
            if obj:
                self.objects_to_render.append(obj)

    def populate_map(self):
        for _ in range(DIFFICULTY.num_nps):
            while True:
                position = choice(self.game.map.free_tiles)
                self.game.map.free_tiles.remove(position)
                manhattan_dist = abs(
                    position[0]-self.game.player.tile_position[0] +
                    position[1]-self.game.player.tile_position[1]
                )
                if manhattan_dist > DIFFICULTY.min_npc_spawn_dist:
                    break

            npc_type = choices(
                self.NPC_TYPES, DIFFICULTY.npc_ratio
            )[0]

            self.all_npc.append(
                npc_type(self.game, (position[0] + .5, position[1] + .5))
            )
