from src.ui.Surface import *
from src.Settings import *
from src.events.Events import Events

from pygame.key import get_pressed as get_pressed_key
from pygame.constants import *


class Statistic(Surface):
    received_damage = 0
    caused_damage = 0
    received_heal = 0
    score = 0
    passed_levels = 0
    killed_mobs = 0
    played_time = time.time()

    def __init__(self, screen):
        super().__init__(screen, DISPLAY_SIZE, (0, 0))

        self.font = PygameFont(FONT_PATH, FONT_SIZE)
        self.stat_font = PygameFont(FONT_PATH, STAT_FONT_SIZE)
        self._message = None
        self._statistic_msg = None

    def update_statistic(self):
        Statistic.played_time = round((time.time()-Statistic.played_time)/60, 1)
        self._statistic_msg = f"Получено урона: {Statistic.received_damage}\n" \
                              f"Нанесено урона: {Statistic.caused_damage}\n" \
                              f"Убито врагов: {Statistic.killed_mobs}\n" \
                              f"Получено лечения: {Statistic.received_heal}\n" \
                              f"Заработано очков: {Statistic.score}\n" \
                              f"Пройдено уровней: {Statistic.passed_levels}\n" \
                              f"Отыграно минут: {Statistic.played_time}"

    def lose(self, color):
        self.surf.fill((color, color, color))
        self._message = self.font.render("YOU DIED", True, (255, color, 0))
        help_rect = self._message.get_rect(center=(GAME["SIZE"][0] // 2, ((GAME["SIZE"][1] // 2) + GAME["POSITION"][1])))
        self.blit()
        self.screen.blit(self._message, help_rect)

    def show(self):
        if Events.isStatisticShown is False:
            self.surf.fill(BLACK)
            self.blit()
            tmp_pos = PIXEL_SIZE*6
            title = self.font.render("Статистика", True, WHITE)
            self.screen.blit(title, (PIXEL_SIZE*4, tmp_pos))
            tmp_pos += FONT_SIZE*3
            for t in self._statistic_msg.split("\n"):
                tmp_pos += STAT_FONT_SIZE+PIXEL_SIZE
                msg = self.stat_font.render(t, True, WHITE)
                self.screen.blit(msg, (PIXEL_SIZE*2, tmp_pos))
            notify = self.stat_font.render("Press SPACE to close the game", True, WHITE)
            self.screen.blit(notify, (PIXEL_SIZE*4, DISPLAY_SIZE[1]-FONT_SIZE*2))
            flip()
            Events.isStatisticShown = True
        elif get_pressed_key()[K_SPACE]:
            exit()

