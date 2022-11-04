import pygame as pg


class Sounds:
    PATH_FILES = 'resources/sound/'

    def __init__(self, game):
        self.game = game
        pg.init()

        self.theme = pg.mixer.Sound(self.PATH_FILES + 'theme.wav')
