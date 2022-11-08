import pygame as pg


class Sounds:
    PATH_FILES = 'resources/sound/'

    def __init__(self, game):
        self.game = game
        pg.init()

        self.theme = pg.mixer.Sound(self.PATH_FILES + 'theme.wav')
        self.shotgun = pg.mixer.Sound(self.PATH_FILES + 'shotgun.wav')
        self.pain = pg.mixer.Sound(self.PATH_FILES + 'player_pain.wav')
        self.npc_pain = pg.mixer.Sound(self.PATH_FILES + 'npc_pain.wav')
        self.npc_death = pg.mixer.Sound(self.PATH_FILES + 'npc_death.wav')
        self.npc_attack = pg.mixer.Sound(self.PATH_FILES + 'npc_attack.wav')
