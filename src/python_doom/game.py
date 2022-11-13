import sys

import pygame as pg

from python_doom.settings import ScreenConfig as SCREEN
from python_doom.settings import GraphicsConfig as GRAPHICS
from python_doom.maps import Maps
from python_doom.npc import NpcHandler
from python_doom.player import Player
from python_doom.path_finding import PathFinding
from python_doom.ray_casting import RayCasting
from python_doom.rendering import Renderer
from python_doom.sprites import SpritesHandler
from python_doom.sounds import Sounds
from python_doom.weapons import Weapon


class Game:
    dt = 1e-16

    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode([
            SCREEN.width,
            SCREEN.height
        ])
        self.clock = pg.time.Clock()
        self._new_game()

        self.sprites_handler = SpritesHandler(self)
        self.npc_handler = NpcHandler(self)
        self.renderer = Renderer(self)
        self.ray_caster = RayCasting(self)

    def _new_game(self):
        self.map = Maps(self)
        self.path_finding = PathFinding(self)
        self.player = Player(self)
        self.weapon = Weapon(self)
        self.sounds = Sounds(self)
        self.sounds.theme.play(-1)

    def _check_game_logic(self) -> bool:
        if self.player.health <= 0:
            self.renderer.render_loss()
            return False

        if len([npc for npc in self.npc_handler.all_npc if npc.alive]) <= 0:
            self.renderer.render_win()
            return False

        return True

    def update(self):
        if self._check_game_logic():
            self.player.update()
            self.ray_caster.update()
            self.sprites_handler.update()
            self.npc_handler.update()
            self.weapon.update()
        pg.display.flip()

        self.dt = self.clock.tick(SCREEN.fps if SCREEN.lock_fps else 1e1)

        caption = \
            f'{self.clock.get_fps() :.1f} - ' + \
            f'{self.player.x :.1f} {self.player.y :.1f} ' + \
            f'{self.player.heading :.2f}'
        pg.display.set_caption(caption)

    def draw(self):
        if GRAPHICS.mode_2d:
            self.screen.fill((0, 0, 0))
        self.renderer.draw()
        self.map.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self._quit()
            self.player.check_shooting(event)

    @staticmethod
    def _quit():
        pg.quit()
        sys.exit()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()
