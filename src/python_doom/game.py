import sys

import pygame as pg

from python_doom.settings import ScreenConfig as SCREEN
from python_doom.maps import Maps
from python_doom.player import Player
from python_doom.ray_casting import RayCasting
from python_doom.rendering import Renderer


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode([
            SCREEN.width,
            SCREEN.height
        ])
        self.clock = pg.time.Clock()
        self.delta_t = 0
        self.new_game()

    def new_game(self):
        self.map = Maps(self)
        self.player = Player(self)
        self.renderer = Renderer(self)
        self.raycaster = RayCasting(self)

    def update(self):
        self.player.update()
        self.raycaster.update()
        pg.display.flip()

        # self.delta_t = self.clock.tick(Settings.fps)
        self.delta_t = self.clock.tick()
        pg.display.set_caption(f'{self.clock.get_fps() :.1f} - {self.player.x} {self.player.y} {self.player.heading}')

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.renderer.draw()
        self.map.draw()
        self.player.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()
