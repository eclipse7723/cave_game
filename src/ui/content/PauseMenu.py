from src.Settings import *
from src.ui.Surface import *


class PauseMenu(Surface):

    def __init__(self, screen):
        super().__init__(screen, DISPLAY_SIZE, (0, 0))
        self.font = PygameFont(FONT_PATH, FONT_SIZE)
        self.button = []
        self.name = None

    def show(self):
        self.surf.fill(RED)
        self.blit()
        tmp_pos = PIXEL_SIZE*6
        title = self.font.render("Pause", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0]/3), tmp_pos+50))
        title = self.font.render("Pause", True, BLACK)
        self.screen.blit(title, (int(STATUS_BAR[0]/3)+2, tmp_pos+52))
        title = self.font.render("Save", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0] / 3)+15, tmp_pos+300))
        title = self.font.render("Settings", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0] / 3)-35, tmp_pos + 400))
        title = self.font.render("Exit", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0] / 3) + 35, tmp_pos + 500))
        flip()

    def rectangle(self):
        x, y = get_mouse_position()
        for i in range(3):
            if LUC_PAUSE_BUTTON[i][0] <= x <= (SIZE_PAUSE_BUTTON[i][0]+LUC_PAUSE_BUTTON[i][0]) and \
                    LUC_PAUSE_BUTTON[i][1] <= y <= (SIZE_PAUSE_BUTTON[i][1]+LUC_PAUSE_BUTTON[i][1]):
                rect(self.screen, WHITE, (LUC_PAUSE_BUTTON[i], SIZE_PAUSE_BUTTON[i]), 4)
                return True, i
        else:
            return False, -1
