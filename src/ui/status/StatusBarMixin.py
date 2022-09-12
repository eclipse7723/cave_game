from src.Settings import *
from src.ui.Surface import *


class StatusBarMixin(Surface):

    def __init__(self, screen, size, position, margin=None, bg_color=GREEN):
        super().__init__(screen, size, position)

        self.margin = (PIXEL_SIZE * 3, PIXEL_SIZE) if margin is None else margin
        self.bg_color = bg_color
        self.font = PygameFont(FONT_PATH, FONT_SIZE)
