import pygame as pg

from python_doom.settings import GraphicConfig as GRAPHICS


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        self.wall_textures = self.load_wall_textures()

    def draw(self):
        self.render_objects()

    def render_objects(self):
        objects = self.game.raycaster.objects
        for depth, image, pos in objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_textures(path, res=(GRAPHICS.texture_size, GRAPHICS.texture_size)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            _: self.get_textures(f'resources/textures/{_}.png')
            for _ in range(1, 6)
        }
