import math

import pygame as pg

from python_doom.settings import PlayerConfig as PLAYER
from python_doom.settings import ScreenConfig as SCREEN
from python_doom.settings import GraphicConfig as GRAPHICS
from python_doom.maps import TILE_SIZE


class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER.position
        self.heading = PLAYER.heading

    def movement(self):
        v = PLAYER.movement_speed * self.game.delta_t
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
            self.heading -= PLAYER.turn_rate * self.game.delta_t
        if keys[pg.K_RIGHT]:
            self.heading += PLAYER.turn_rate * self.game.delta_t

        self.check_collisions(dx, dy)
        self.heading %= math.tau

    def can_move(self, x, y):
        return (int(x), int(y)) not in self.game.map.obstructed_tiles

    def check_collisions(self, dx, dy):
        if self.can_move(self.x + dx, self.y):
            self.x += dx
        if self.can_move(self.x, self.y + dy):
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
        self.movement()

    @property
    def position(self):
        return self.x, self.y

    @property
    def tile_position(self):
        return int(self.x), int(self.y)
