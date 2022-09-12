from src.ui.Surface import *
from src.events.Events import Events
from src.Settings import *
from src.utils.get_engine import get_engine


class GameUI(Surface):

    def __init__(self, screen, map):
        super().__init__(screen, GAME["SIZE"], GAME["POSITION"])

        self.font = PygameFont(FONT_PATH, FONT_SIZE)
        self.map = map

    def update(self):
        if True in Events.get_game_events():
            if Events.isSomeoneMoved:
                Events.isSomeoneMoved = False
            if Events.isHeroMoved:
                Events.isHeroMoved = False
            if Events.isSomeoneDied:
                Events.isSomeoneDied = False
            if DEBUG:
                engine = get_engine()
                engine.debug_text()

            self.map.render()
            self.blit()

