from src.Settings import *
from src.ui.Surface import *


class MainMenu(Surface):

    def __init__(self, screen, play, settings):
        super().__init__(screen, DISPLAY_SIZE, (0, 0))

        self.font = PygameFont(FONT_PATH, FONT_SIZE)
        self.button = [play, settings]

    def show(self):
        self.surf.fill(RED)
        self.blit()

        tmp_pos = PIXEL_SIZE*6
        title = self.font.render(f"CaveX {VERSION}", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0]/3) - 75, tmp_pos + 50))
        title = self.font.render(f"CaveX {VERSION}", True, BLACK)
        self.screen.blit(title, (int(STATUS_BAR[0]/3) - 73, tmp_pos + 52))
        title = self.font.render(f"Play", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0] / 3) + 15, tmp_pos + 300))
        title = self.font.render(f"Load", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0] / 3) + 35, tmp_pos + 400))
        title = self.font.render(f"Settings", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0] / 3) - 35, tmp_pos + 500))
        title = self.font.render(f"Exit", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0] / 3) + 35, tmp_pos + 600))

        flip()

    def rectangle(self):
        x, y = get_mouse_position()
        for i in range(4):
            if LUC_MENU_BUTTON[i][0] <= x <= (SIZE_MENU_BUTTON[i][0] + LUC_MENU_BUTTON[i][0]) and \
                    LUC_MENU_BUTTON[i][1] <= y <= (SIZE_MENU_BUTTON[i][1] + LUC_MENU_BUTTON[i][1]):
                rect(self.screen, WHITE, (LUC_MENU_BUTTON[i], SIZE_MENU_BUTTON[i]), 4)
                return True, i
        else:
            return False, -1
