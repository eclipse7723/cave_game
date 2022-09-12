from src.Settings import *
from src.ui.Surface import *


class SaveMenu(Surface):

    def __init__(self, screen):
        super().__init__(screen, DISPLAY_SIZE, (0, 0))

        self.font = PygameFont(FONT_PATH, FONT_SIZE)
        self.font2 = PygameFont(FONT_PATH, FONT_SIZE-35)
        self.time = get_time()

    def add_save(self, index):
        tmp_pos = PIXEL_SIZE*6
        title = self.font2.render(f"Lvl: 0", True, WHITE)
        self.screen.blit(title, (50, tmp_pos + 400))
        title = self.font2.render(f"Time: {self.time}", True, WHITE)
        self.screen.blit(title, (370, tmp_pos + 400))

    def show(self):
        self.surf.fill(RED)
        self.blit()

        tmp_pos = PIXEL_SIZE*6
        title = self.font.render(f"Save menu", True, WHITE)
        self.screen.blit(title, (int(STATUS_BAR[0]/3)-50, tmp_pos+50))
        title = self.font.render(f"Save menu", True, BLACK)
        self.screen.blit(title, (int(STATUS_BAR[0]/3)-48, tmp_pos+52))
        title = self.font.render(f"Save slot 1", True, WHITE)
        self.screen.blit(title, (50, tmp_pos + 300))
        title = self.font.render(f"Save slot 2", True, WHITE)
        self.screen.blit(title, (50, tmp_pos + 450))
        title = self.font.render(f"Save slot 3", True, WHITE)

        self.screen.blit(title, (50, tmp_pos + 600))
        flip()

    def rectangle(self):
        x, y = get_mouse_position()
        for i in range(3):
            if LUC_SAVE_BUTTON[i][0] <= x <= (SAVE_MENU_BUTTON[i][0] + LUC_SAVE_BUTTON[i][0]) and \
                    LUC_SAVE_BUTTON[i][1] <= y <= (SAVE_MENU_BUTTON[i][1] + LUC_SAVE_BUTTON[i][1]):
                rect(self.screen, WHITE, (LUC_SAVE_BUTTON[i], SAVE_MENU_BUTTON[i]), 4)
                if i == 0:
                    self.add_save(1)
                return True, i
        else:
            return False, -1
