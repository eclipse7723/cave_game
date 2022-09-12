from src.Map import Map
from src.Settings import *
from src.events.Events import Events

from src.ui.status.StatusBarMixin import StatusBarMixin
from src.ui.content.Statistic import Statistic


class GameBar(StatusBarMixin):

    def __init__(self, screen):
        super().__init__(screen, GAME_BAR["SIZE"], GAME_BAR["POSITION"])

        self.score = None
        self.level = None

        self.__scoreSize = ((self.size[0] - self.margin[1] * 2) * 2 // 3, self.size[1] - self.margin[0] * 2)
        self.__scorePosition = (self.position[0] + self.margin[1], self.margin[0])
        self.__levelSize = ((self.size[0] - self.margin[1] * 2) // 3, self.size[1] - self.margin[0] * 2)
        self.__levelPosition = (self.__scoreSize[0] + self.margin[1], self.margin[0])

        self.blit()

    def update(self):
        if True in Events.get_gamebar_events():
            if Events.isScoredPoints:
                Events.isScoredPoints = False
            if Events.isPassedLevel:
                Events.isPassedLevel = False
            self.blit()

    def blit(self):
        self.surf.fill(self.bg_color)
        self.score = self.font.render(f"Score: {Statistic.score}", True, WHITE)
        self.level = self.font.render(f"LVL: {Map.created_maps}", True, WHITE)
        self.surf.blit(self.score, self.__scorePosition)
        self.surf.blit(self.level, self.__levelPosition)
        self.screen.blit(self.surf, self.position)
