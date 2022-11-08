import math

import pygame as pg
import numpy as np

from python_doom.settings import PlayerConfig as PLAYER
from python_doom.settings import ScreenConfig as SCREEN
from python_doom.settings import GraphicsConfig as GRAPHICS
from python_doom.settings import ControlsConfig as CONTROLS
from python_doom.maps import TILE_SIZE


class Player:
    shot_fired = False

    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER.position
        self.heading = PLAYER.heading

    def check_shooting(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.shot_fired or self.game.weapon.reloading:
                    return
                self.game.sounds.shotgun.play()
                self.shot_fired = True

    def _movement(self):
        v = PLAYER.movement_speed * self.game.dt
        v_sin = math.sin(self.heading) * v
        v_cos = math.cos(self.heading) * v

        dx, dy = 0, 0

        keys = pg.key.get_pressed()
        # Moving
        if keys[pg.K_w]:
            dx += v_cos
            dy += v_sin
        if keys[pg.K_s]:
            dx -= v_cos
            dy -= v_sin
        # Strafing
        if keys[pg.K_a]:
            dx += v_sin
            dy -= v_cos
        if keys[pg.K_d]:
            dx -= v_sin
            dy += v_cos
        # Turning
        if keys[pg.K_LEFT]:
            self.heading -= PLAYER.turn_rate * self.game.dt
        if keys[pg.K_RIGHT]:
            self.heading += PLAYER.turn_rate * self.game.dt

        self._check_collisions(dx, dy)
        self.heading %= math.tau

    def _mouse_look(self):
        x, y = pg.mouse.get_pos()
        if x < CONTROLS.mouse_border_left or x > CONTROLS.mouse_border_right:
            pg.mouse.set_pos([SCREEN.half_width, SCREEN.half_height])

        self.rel_move = pg.mouse.get_rel()[0]
        self.rel_move = np.clip(
            self.rel_move, -CONTROLS.mouse_max_rel_move,
            CONTROLS.mouse_max_rel_move
        )

        self.heading += self.rel_move * CONTROLS.mouse_sensitivity * self.game.dt

    def _check_for_walls(self, x, y):
        for xs, ys in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            dx = xs * PLAYER.size
            dy = ys * PLAYER.size
            if (int(x+dx), int(y+dy)) in self.game.map.obstructed_tiles:
                return False
        return True

    def _check_collisions(self, dx, dy):
        if self._check_for_walls(self.x + dx, self.y):
            self.x += dx
        if self._check_for_walls(self.x, self.y + dy):
            self.y += dy

    def draw(self):
        if GRAPHICS.mode_2d:
            pg.draw.line(
                self.game.screen, (100, 0, 150),
                (self.x * TILE_SIZE, self.y * TILE_SIZE),
                (self.x * TILE_SIZE + SCREEN.width * math.cos(self.heading),
                 self.y * TILE_SIZE + SCREEN.width * math.sin(self.heading)),
                2)
            pg.draw.circle(
                self.game.screen, (200, 200, 0),
                (int(self.x * TILE_SIZE), int(self.y * TILE_SIZE)),
                15
            )

    def update(self):
        self._movement()
        self._mouse_look()

    @property
    def position(self):
        return self.x, self.y

    @property
    def tile_position(self):
        return int(self.x), int(self.y)
