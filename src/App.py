import pygame
import random

from src.Settings import *
from src.events.Events import Events
from src.Map import Map

from src.utils.Singelton import SingletonMeta

from src.entities.Hero import Hero
from src.entities.Enemy import Enemy

from src.ui.GameUI import GameUI
from src.ui.content.Statistic import Statistic
from src.ui.content.MainMenu import MainMenu
from src.ui.content.PauseMenu import PauseMenu
from src.ui.content.SaveMenu import SaveMenu
from src.ui.status.GameBar import GameBar
from src.ui.status.PlayerBar import PlayerBar


# Главный класс проекта (запуск здесь)
class GameEngine(metaclass=SingletonMeta):
    def __init__(self):
        self.screen = pygame.display.set_mode(DISPLAY_SIZE)
        self.game = None
        self.game_bar = None
        self.player_bar = None
        self.statistic = None
        self.pausemenu = None
        self.timer = 0
        self._map = None
        self._hero = None
        self.BMenu = False
        self.buttonmenu = -1
        self.BSave = False
        self.buttonsave = -1
        self.BPause = False
        self.buttonpause = -1

        if DEBUG:
            self.debug_cords = None

    # Воспомогательные функции >>>
    def units_action(self):
        # Передвижение мобов
        if len(self._map.objects) > 1:
            enemy = random.choice(self._map.objects[1:])
            if isinstance(enemy, Enemy):
                enemy.wander()

        # Охота мобов на перса
        if self.timer != int(time.time()):
            self.timer = int(time.time())
            for enemy in self._map.objects[1:]:
                if isinstance(enemy, Enemy):
                    enemy.haunt(self._hero)

    def player_movement(self):
        key = pygame.key.get_pressed()      # Действия, пока клавиша зажата
        if key[pygame.K_LEFT] or key[pygame.K_a]:       # Движение влево
            self._hero.move("left")
        if key[pygame.K_RIGHT] or key[pygame.K_d]:      # Движение вправо
            self._hero.move("right")
        if key[pygame.K_UP] or key[pygame.K_w]:         # Движение вперёд
            self._hero.move("up")
        if key[pygame.K_DOWN] or key[pygame.K_s]:       # Движение назадw
            self._hero.move("down")
        if key[pygame.K_SPACE]:                         # Атака
            self._hero.attack(self._map.find_nearest_enemy())
        if key[pygame.K_e]:                             # Хилка
            self._hero.heal(50)

    def check_losed_game(self):
        if Events.isHeroDied is False:
            return
        if Events.isGameLoosed is True:
            return

        start_color = 105
        self._map.kill_all("Hero died :(")
        clock = pygame.time.Clock()
        self.timer = int(time.time())
        while start_color:
            clock.tick(10)
            self.statistic.lose(start_color)
            pygame.display.flip()
            start_color -= 5
        Events.isGameLoosed = True
        self.statistic.update_statistic()

    def debug_text(self):
        pygame.draw.rect(self.screen, GREEN, (DISPLAY_SIZE[0]-100, DISPLAY_SIZE[1]-20, DISPLAY_SIZE[0]-50, DISPLAY_SIZE[1]))
        font = pygame.font.SysFont("Arial", PIXEL_SIZE*2)
        text = f"x:{self._hero.pos.x}, y:{self._hero.pos.y}"
        self.debug_cords = font.render(text, True, WHITE)
        self.screen.blit(self.debug_cords, (DISPLAY_SIZE[0]-100, DISPLAY_SIZE[1]-20))
    # <<< Воспомогательные функции

    # Запуск игры >>>
    def start(self):
        pygame.init()
        pygame.display.set_caption(f"CaveX v{VERSION}")

        # Игровые объекты
        self._map = Map()
        self._hero = Hero(self._map)
        self._map.generate_enemies()
        self.timer = int(time.time())

        # Инициализация блоков
        self.game_bar = GameBar(self.screen)
        self.game = GameUI(self.screen, self._map)
        self.player_bar = PlayerBar(self.screen, self._hero)
        self.statistic = Statistic(self.screen)
        self.pausemenu = PauseMenu(self.screen)
        self.savemenu = SaveMenu(self.screen)
        self.settings = None
        self.menu = MainMenu(self.screen, self.savemenu, self.settings)
        self._map.render()      # Рисуем карту
        self.game.blit()
        self.mainloop()         # Цикл игры

    def mainloop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(FPS)  # Количество кадров в секунду
            if Events.isMenu:
                self.menu.show()
                self.BMenu, self.buttonmenu = self.menu.rectangle()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                    elif self.BMenu and event.type == pygame.MOUSEBUTTONDOWN:
                        if self.buttonmenu == 0 and event.button == 1:
                            Events.isMenu = False
                            Events.isGameStart = True
                        if self.buttonmenu == 1 and event.button == 1:
                            Events.isSaveMenu = True
                            Events.isMenu = False
                        if self.buttonmenu == 2 and event.button == 1:
                            exit()
            elif Events.isSaveMenu:
                self.savemenu.show()
                self.BSave, self.buttonsave = self.savemenu.rectangle()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if not Events.isGameStart:
                                Events.isSaveMenu = False
                                Events.isMenu = True
                            else:
                                Events.isSaveMenu = False
                                Events.isPause = True
                    elif self.BSave and event.type == pygame.MOUSEBUTTONDOWN:
                        if self.buttonsave == 1 or self.buttonsave == 0:
                            print(f"Play Menu {self.buttonsave}")
            elif Events.isGameStart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            Events.isPause = not Events.isPause
                    elif self.BPause and event.type == pygame.MOUSEBUTTONDOWN:
                        if self.buttonpause == 0 and event.button == 1:
                            Events.isSaveMenu = True
                            Events.isPause = False
                        elif self.buttonpause == 2 and event.button == 1:
                            exit()
                self.check_losed_game()
                if Events.isGameLoosed:
                    self.statistic.show()
                    continue
                elif not (Events.isPause or Events.isSaveMenu):
                    self.player_movement()
                    self.units_action()
                    self.game.blit()
                    self.game_bar.blit()
                    self.player_bar.blit()
                else:
                    self.pausemenu.show()
                    self.BPause, self.buttonpause = self.pausemenu.rectangle()
                self.game.update()
                self.game_bar.update()
                self.player_bar.update()
            pygame.display.flip()
    # <<< Запуск игры


def run():
    engine = GameEngine()
    engine.start()
