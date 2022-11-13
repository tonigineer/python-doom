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
    health = 100

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
        if not (
            CONTROLS.mouse_border_left <= x <= CONTROLS.mouse_border_right and
            CONTROLS.mouse_border_bottom <= y <= CONTROLS.mouse_border_top
        ):
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

    def _draw_2d(self):
        COLOR = (14, 185, 162)
        LINE_WIDTH = 2
        RADIUS = 15

        if GRAPHICS.mode_2d:
            pg.draw.line(
                self.game.screen, COLOR,
                (self.x * TILE_SIZE, self.y * TILE_SIZE),
                (self.x * TILE_SIZE + GRAPHICS.max_depth * TILE_SIZE * math.cos(self.heading),
                 self.y * TILE_SIZE + GRAPHICS.max_depth * TILE_SIZE * math.sin(self.heading)),
                LINE_WIDTH)
            pg.draw.circle(
                self.game.screen, COLOR,
                (int(self.x * TILE_SIZE), int(self.y * TILE_SIZE)),
                RADIUS
            )

    def update(self):
        self._movement()
        self._mouse_look()
        self._draw_2d()

    def take_damage(self, attack_damage):
        self.health -= min(attack_damage, self.health)
        self.game.renderer.player_took_damage = True
        self.game.sounds.pain.play()

    @property
    def position(self):
        return self.x, self.y

    @property
    def tile_position(self):
        return int(self.x), int(self.y)
