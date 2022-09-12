from src.Settings import *
from src.events.Events import Events
from src.ui.status.StatusBarMixin import StatusBarMixin
from src.utils.get_engine import get_engine


class PlayerBar(StatusBarMixin):

    def __init__(self, screen, player):
        super().__init__(screen, PLAYER_BAR["SIZE"], PLAYER_BAR["POSITION"])

        self.player = player
        self.heroHP = None
        self.heroAR = None

        self.__HPSize = ((self.size[0] - self.margin[1] * 2) * 2 // 3, self.size[1] - self.margin[0] * 2)
        self.__HPPosition = (self.position[0] + self.margin[1], self.margin[0])
        self.__ARSize = ((self.size[0] - self.margin[1] * 2) // 3, self.size[1] - self.margin[0] * 2)
        self.__ARPosition = (self.__HPSize[0] + self.margin[1], self.margin[0])

        self.blit()

    def update(self):
        if True not in Events.get_playerbar_events():
            return

        if Events.isHealthModified:
            Events.isHealthModified = False
        if Events.isArmorModified:
            Events.isArmorModified = False
        if DEBUG:
            engine = get_engine()
            engine.debug_text()

        self.blit()

    def blit(self):
        self.surf.fill(self.bg_color)
        self.heroHP = self.font.render(f"HP: {int(self.player.health)}/{int(self.player.MAXHEALTH)}", True, WHITE)
        self.heroAR = self.font.render(f"AR: {self.player.armor}", True, WHITE)
        self.surf.blit(self.heroHP, self.__HPPosition)
        self.surf.blit(self.heroAR, self.__ARPosition)
        self.screen.blit(self.surf, self.position)
