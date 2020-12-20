from abc import ABC, abstractmethod
import time
import os
import pygame
from PIL import Image
from maze import *           # Генерация лабиринта
from Settings import *       # Настройки


class Position:  # Координаты объектов
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def change(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y


class Unit(ABC):  # Общий класс для юнитов
    def __init__(self, map, name, hp, ar, dmg, color):
        self.pos = Position()
        self.map = map
        self._name = name
        self._health = hp
        self._armor = ar
        self._damage = dmg
        self._MAXHEALTH = 200.0
        self.color = color
        self.face = 'down'

    # Характеристики >>>
    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, hp):
        self._health = hp

    @property
    def damage(self):
        return self._damage

    @property
    def armor(self):
        return self._armor

    @property
    def name(self):
        return self._name

    @property
    def MAXHEALTH(self):
        return self._MAXHEALTH

    # <<< Характеристики

    # Действия >>>
    @abstractmethod
    def attack(self, unit):
        """Атака юнита unit"""
        raise NotImplementedError("Необходимо переопределить метод attack")

    def die(self, reason):
        print(f"[{get_time()}] {self.name} died - reason: {reason}.")
        self.map[self.pos.x][self.pos.y] = 1
        self.map.objects.remove(self)
        del self
        Events.isSomeoneDied = True
    # <<< Действия

    # Передвижение >>>
    @abstractmethod
    def move(self, direction):
        """Передвижение юнита"""
        raise NotImplementedError("Необходимо переопределить метод move")

    def get_distance_to(self, obj):
        if obj not in self.map.objects:
            log(f"{obj} isn't on the current map (level: {Map.created_maps}).")
        else:
            return ((self.pos.x - obj.pos.x) ** 2 + (self.pos.y - obj.pos.y) ** 2) ** (1 / 2)
    # <<< Передвижение


class Hero(Unit):  # Класс отвечающий за параметры главного героя
    def __init__(self, map):
        super().__init__(map, "Hero", hp=200.0, ar=3.0, dmg=5.0, color=RED)
        map.spawnObject(self)
        self._heal_cooldown = 0

    # Передвижение >>>
    def move(self, way):
        x, y = self.pos.x + WAYS[way][0], self.pos.y + WAYS[way][1]
        self.face = way
        if self.map.isExit(x, y):
            Events.isPassedLevel = True
            self.map.update_map()
        elif self.map.isFree(x, y):
            self.map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            self.map[self.pos.x][self.pos.y] = self
            Events.isHeroMoved = True
        # else: log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def heal(self, hp):
        if self.health >= self.MAXHEALTH:
            print(f"[{get_time()}] {self.name} already has max health ({self.health}/{self.MAXHEALTH}).")
        elif int(time.time()) < self._heal_cooldown + 5:
            print("Not now")
        else:
            print(f"[{get_time()}] {self.name}: +{hp} ({self.health}/{self.MAXHEALTH}).")
            self.health += hp
            Statistic.received_heal += hp
            self._heal_cooldown = int(time.time())
            Events.isHealthModified = True

    def teleport(self, x, y):
        self.map[self.pos.x][self.pos.y] = 1
        self.pos.change(x, y)
        self.map[self.pos.x][self.pos.y] = self
    # <<< Передвижение

    # Атака >>>
    def find_nearest_enemy(self):
        positions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1)]
        for pos in positions:
            enemy = self.map[self.pos.x + pos[0]][self.pos.y + pos[1]]
            if isinstance(enemy, Enemy): return enemy
        return None

    def attack(self, enemy):
        if enemy is None: return
        damage = (self.damage + random.randint(0, 3) - enemy.armor) * (0 if random.randint(0, 100) <= 10 else 1)
        enemy.health -= damage
        enemy.color = get_mod_color(enemy.color, -damage)
        Statistic.caused_damage += damage
        if damage:
            print(f"[{get_time()}] {self.name} inflict {damage} damage to {enemy.name} (HP: {enemy.health}).")
        else:
            print(f"[{get_time()}] {self.name} missed (HP: {enemy.health}).")
        if enemy.health <= 0:
            enemy.die(self.name)
            Statistic.killed_mobs += 1
            Statistic.score += enemy.points
            Events.isScoredPoints = True
            print(f"[{get_time()}] {self.name} scored {enemy.points} point (Total score: {Statistic.score}).")
    # <<< Атака


class Enemy(Unit):
    def __init__(self, map, name, points, agr):
        super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0, color=BLUE)
        randPoint = map.get_randomPoint()
        map.spawnObject(self, randPoint[0], randPoint[1])
        self.points = points
        self.agr_radius = agr

    # Передвижение >>>
    def move(self, way):
        x, y = self.pos.x + WAYS[way][0], self.pos.y + WAYS[way][1]
        self.face = way
        if self.map.isFree(x, y):
            self.map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            self.map[self.pos.x][self.pos.y] = self
            Events.isSomeoneMoved = True
        # else: log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def wander(self):
        self.move(random.choice(list(WAYS.keys())))

    def haunt(self, player):
        cur_dist = self.get_distance_to(player)
        if cur_dist is None or self.agr_radius < cur_dist: return
        for way in WAYS.items():
            possibly_pos = (self.pos.x + way[1][0], self.pos.y + way[1][1])
            if not self.map.isFree(possibly_pos[0], possibly_pos[1]): continue
            possibly_dist = ((player.pos.x - possibly_pos[0]) ** 2 + (player.pos.y - possibly_pos[1]) ** 2) ** (1 / 2)
            if possibly_dist < cur_dist: self.move(way[0])
        if self.get_distance_to(player) < 2:
            self.attack(player)

    # <<< Передвижение

    def attack(self, player):
        damage = (self._damage + random.randint(0, 3) - player.armor) * (0 if random.randint(0, 100) <= 10 else 1)
        player.health -= damage
        Statistic.received_damage += damage
        if damage:
            print(f"[{get_time()}] {self.name} inflict {damage} damage to {player.name} (HP: {player.health}).")
            Events.isHealthModified = True
        else:
            print(f"[{get_time()}] {self.name} missed (HP: {player.health}).")
        if player.health <= 0:
            player.health = 0
            player.die(self.name)
            Events.isHeroDied = True

    @staticmethod
    def get_ork_name():
        start = ["Slog", "Ra", "Ro", "Og", "Kegi", "Zor", "Un", "Yag", "Blak", "Mug", "Gud"]
        middle = "abcdeghklmnopqrst"
        end = ["ka", "rana", "all", "mash", "tan", "gu", "tag", "ge", "rim"]
        return random.choice(start) + (random.choice(middle) if random.randint(0, 1) else "") + random.choice(end)


class Map(list):
    created_maps = 0

    def __init__(self):
        super().__init__()
        self.size = 51
        self.objects = []
        self.create_map('map.png')
        self.spawn = None

    # Воспомогательные функции >>>
    def isWall(self, x, y):
        return True if self[x][y] == 0 else False

    def isExit(self, x, y):
        return True if self[x][y] == "exit" else False

    def isFree(self, x, y):
        return True if self[x][y] == 1 else False

    def get_randomPoint(self):
        random.seed(time.time())
        while True:
            x = random.randint(1, self.size - 1)
            y = random.randint(1, self.size - 1)
            if self.isFree(x, y): break
        return x, y

    def find_pos(self, obj):  # Найти позицию определённого объекта на карте
        for x in range(self.size):
            try:
                y = self[x].index(obj)
            except ValueError:
                continue
            else:
                return x, y
        return None, None
    # <<< Воспомогательные функции

    # Отрисовка >>>
    def render(self):
        player = self.objects[0]

        engine.game.surf.fill(DARK_GREEN)
        for y, j in zip(range(player.pos.y - radius//2, player.pos.y + radius//2), range(radius)):
            for x, i in zip(range(player.pos.x - radius//2, player.pos.x + radius//2), range(radius)):
                if x < 0 or x > 50 or y < 0 or y > 50:
                    continue
                if self[x][y] == 1:
                    pygame.draw.rect(engine.game.surf, WHITE, get_draw_position(i, j, PIXEL))
                elif self[x][y] == "exit":
                    pygame.draw.rect(engine.game.surf, BLACK, get_draw_position(i, j, PIXEL))
                elif self[x][y] == 0:
                    pygame.draw.rect(engine.game.surf, GREEN, get_draw_position(i, j, PIXEL))
                elif isinstance(self[x][y], Unit):
                    obj = self[x][y]
                    pygame.draw.rect(engine.game.surf, obj.color, get_draw_position(i, j, PIXEL))
                    pygame.draw.rect(engine.game.surf, get_mod_color(obj.color, -50),
                                     ((i * PIXEL) + FACE[obj.face][0], (j * PIXEL) + FACE[obj.face][1],
                                      PIXEL - TAIL[obj.face][0], PIXEL - TAIL[obj.face][1]))
    # <<< Отрисовка

    # Настройки карты >>>
    def create_map(self, path):  # Создание карты по картинке
        im = Image.open(path)
        pix = im.load()
        for i in range(self.size):
            self.append([])
            for j in range(self.size):
                if pix[i, j][:3] == WHITE:
                    self[i].append(1)
                elif pix[i, j][:3] == YELLOW:
                    self[i].append("spawn")
                    self.spawn = (i, j)
                elif pix[i, j][:3] == BLACK:
                    self[i].append("exit")
                else:
                    self[i].append(0)
        if self.spawn is None: self.spawn = (1, 1)
        Map.created_maps += 1

    def gen_map(self):  # Генерация нового лабиринта
        m = Maze()
        m.create(self.size, self.size, Maze.Create.KRUSKAL)
        m.save_maze()
        im = Image.open('maze.png')
        pix = im.load()
        for i in range(self.size):
            self.append([])
            for j in range(self.size):
                if pix[i, j][:3] == BLACK:
                    im.putpixel((i, j), GREEN)
        im.putpixel((1, 1), YELLOW)
        im.putpixel((MAP_SIZE - 2, MAP_SIZE - 2), BLACK)
        im.save("maze.png")

    def update_map(self):  # Обновить карту (заново отрегенить, расставить мобов итд)
        print(f"[{get_time()}] Level {Map.created_maps} has been passed.")
        self.kill_all("level passed")
        os.remove("maze.png")
        self.gen_map()
        for i in range(len(self)): self.pop()
        self.create_map("maze.png")
        self.objects[0].teleport(self.spawn[0], self.spawn[1])
        [Enemy(self, f"Ork {Enemy.get_ork_name()}", random.randint(2, 5), 5.0) for i in range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1]))]
        Map.created_maps += 1
        Statistic.passed_levels += 1
        log(f"Level {Map.created_maps} has been started.")
        Statistic.score += 10
    # <<< Настройки карты

    def spawnObject(self, obj, x=0, y=0):  # Спавн объекта на определённых координатах
        if isinstance(obj, Hero):  # Герой всегда на спавн-точке
            spawnCords = self.find_pos("spawn")
            if spawnCords is None:
                randPoint = self.get_randomPoint()
                x, y = randPoint[0], randPoint[1]
            else:
                x, y = spawnCords[0], spawnCords[1]
        self.objects.append(obj)
        obj.map = self
        self[x][y] = obj
        obj.pos.change(x, y)

    def kill_all(self, reason: str):
        for entity in self.objects[1:]: entity.die(reason)


class Events:
    isScoredPoints = False          # Получены ли баллы
    isPassedLevel = False           # Пройден ли уровень
    isHealthModified = False        # Изменилось ли HP героя
    isArmorModified = False         # Изменилось ли AR героя
    isSomeoneMoved = False          # Двинулся ли кто-то
    isHeroMoved = False             # Двинулся ли герой
    isSomeoneDied = False           # Умер ли кто-то
    isHeroDied = False              # Умер ли герой
    isGameLoosed = False            # Проиграна ли игра
    isStatisticShown = False        # Отображена ли статистика

    @staticmethod
    def get_game_events():          # Ивенты игрового блока
        return Events.isSomeoneDied, Events.isSomeoneMoved, Events.isHeroMoved, Events.isHeroDied

    @staticmethod
    def get_playerbar_events():     # Ивенты статусбара игрока
        return Events.isHealthModified, Events.isArmorModified

    @staticmethod
    def get_gamebar_events():       # Ивенты статусбара игры
        return Events.isScoredPoints, Events.isPassedLevel


class Surface(ABC):  # Класс блоков
    def __init__(self, screen, size, position):
        self.screen = screen
        self.size = size
        self.position = position
        self.surf = pygame.Surface(size)


class ISurface(ABC):
    @abstractmethod
    def update(self):
        """Обновление поверхности"""
        raise NotImplementedError("Необходимо переопределить метод update")

    @abstractmethod
    def blit(self):
        """Наложение всех деталей на поверхность"""
        raise NotImplementedError("Необходимо переопределить метод blit")


class Game(Surface, ISurface):
    def __init__(self, screen, map):
        super().__init__(screen, GAME["SIZE"], GAME["POSITION"])
        self.font = pygame.font.Font("font.ttf", FONT_SIZE)
        self.map = map

    def update(self):
        if True in Events.get_game_events():
            if Events.isSomeoneMoved: Events.isSomeoneMoved = False
            if Events.isHeroMoved: Events.isHeroMoved = False
            if Events.isSomeoneDied: Events.isSomeoneDied = False
            self.map.render()
            engine.debug_text()
            self.blit()

    def blit(self):
        self.screen.blit(self.surf, self.position)

    # def lose(self, color):
    #     self.surf.fill((color, color, color))
    #     self.message = self.font.render("YOU DIED", 1, (255, color, 0))
    #     self.message_rect = self.message.get_rect(center=(GAME["SIZE"][0] // 2, ((GAME["SIZE"][1] // 2) + GAME["POSITION"][1])))
    #     self.blit()
    #     self.screen.blit(self.message, self.message_rect)


class StatusBar(Surface, ABC):
    def __init__(self, screen, size, position, margin=None, bg_color=GREEN):
        super().__init__(screen, size, position)
        self.margin = (PIXEL_SIZE * 3, PIXEL_SIZE) if margin is None else margin
        self.bg_color = bg_color
        self.font = pygame.font.Font("font.ttf", FONT_SIZE)


class GameBar(StatusBar, ISurface):
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
            if Events.isScoredPoints: Events.isScoredPoints = False
            if Events.isPassedLevel: Events.isPassedLevel = False
            self.blit()

    def blit(self):
        self.surf.fill(self.bg_color)
        self.score = self.font.render(f"Score: {Statistic.score}", True, WHITE)
        self.level = self.font.render(f"LVL: {Map.created_maps}", True, WHITE)
        self.surf.blit(self.score, self.__scorePosition)
        self.surf.blit(self.level, self.__levelPosition)
        self.screen.blit(self.surf, self.position)


class PlayerBar(StatusBar, ISurface):
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
        if True in Events.get_playerbar_events():
            if Events.isHealthModified: Events.isHealthModified = False
            if Events.isArmorModified: Events.isArmorModified = False
            engine.debug_text()
            self.blit()

    def blit(self):
        self.surf.fill(self.bg_color)
        self.heroHP = self.font.render(f"HP: {int(self.player.health)}/{int(self.player.MAXHEALTH)}", True, WHITE)
        self.heroAR = self.font.render(f"AR: {self.player.armor}", True, WHITE)
        self.surf.blit(self.heroHP, self.__HPPosition)
        self.surf.blit(self.heroAR, self.__ARPosition)
        self.screen.blit(self.surf, self.position)


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
        self.font = pygame.font.Font("font.ttf", FONT_SIZE)
        self.stat_font = pygame.font.Font("font.ttf", STAT_FONT_SIZE)
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
        self._message = self.font.render("YOU DIED", 1, (255, color, 0))
        help_rect = self._message.get_rect(center=(GAME["SIZE"][0] // 2, ((GAME["SIZE"][1] // 2) + GAME["POSITION"][1])))
        self.blit()
        self.screen.blit(self._message, help_rect)

    def show(self):
        if Events.isStatisticShown is False:
            self.surf.fill(BLACK)
            self.blit()
            tmp_pos = PIXEL_SIZE*6
            title = self.font.render("Статистика", 1, WHITE)
            self.screen.blit(title, (PIXEL_SIZE*4, tmp_pos))
            tmp_pos += FONT_SIZE*3
            for t in self._statistic_msg.split("\n"):
                tmp_pos += STAT_FONT_SIZE+PIXEL_SIZE
                msg = self.stat_font.render(t, 1, WHITE)
                self.screen.blit(msg, (PIXEL_SIZE*2, tmp_pos))
            notify = self.stat_font.render("Press SPACE to close the game", 1, WHITE)
            self.screen.blit(notify, (PIXEL_SIZE*4, DISPLAY_SIZE[1]-FONT_SIZE*2))
            pygame.display.flip()
            Events.isStatisticShown = True
        elif pygame.key.get_pressed()[pygame.K_SPACE]:
            exit()

    def blit(self):
        self.screen.blit(self.surf, self.position)


class SingletonMeta(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in cls._instance:
            instance = super().__call__(*args, **kwargs)
            cls._instance[cls.__name__] = instance
        return cls._instance[cls.__name__]


class GameEngine(metaclass=SingletonMeta):
    def __init__(self):
        self.screen = pygame.display.set_mode(DISPLAY_SIZE)
        self.game = None
        self.game_bar = None
        self.player_bar = None
        self.statistic = None
        self.timer = 0
        self._map = None
        self._hero = None

        # debug
        if DEBUG:
            self.debug_cords = None

    # Воспомогательные функции >>>
    def units_action(self):
        # Передвижение мобов
        if len(self._map.objects) > 1:
            enemy = random.choice(self._map.objects[1:])
            if isinstance(enemy, Enemy): enemy.wander()
        # Охота мобов на перса
        if self.timer != int(time.time()):
            self.timer = int(time.time())
            for enemy in self._map.objects[1:]:
                if isinstance(enemy, Enemy): enemy.haunt(self._hero)

    def player_movement(self):
        key = pygame.key.get_pressed()      # Действия, пока клавиша зажата
        if key[pygame.K_LEFT] or key[pygame.K_a]:       # Движение влево
            self._hero.move("left")
        if key[pygame.K_RIGHT] or key[pygame.K_d]:      # Движение вправо
            self._hero.move("right")
        if key[pygame.K_UP] or key[pygame.K_w]:         # Движение вперёд
            self._hero.move("up")
        if key[pygame.K_DOWN] or key[pygame.K_s]:       # Движение назад
            self._hero.move("down")
        if key[pygame.K_SPACE]:                         # Атака
            self._hero.attack(self._hero.find_nearest_enemy())
        if key[pygame.K_e]:                             # Хилка
            self._hero.heal(50)

    def check_losed_game(self):
        if Events.isHeroDied and Events.isGameLoosed is False:
            color = 105
            self._map.kill_all("Hero died :(")
            clock = pygame.time.Clock()
            self.timer = int(time.time())
            while color:
                clock.tick(10)
                self.statistic.lose(color)
                pygame.display.flip()
                color -= 5
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
        [Enemy(self._map, f"Ork {Enemy.get_ork_name()}", random.randint(2, 5), 5.0) for i in range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1]))]
        self.timer = int(time.time())

        # Инициализация блоков
        self.game_bar = GameBar(self.screen)
        self.game = Game(self.screen, self._map)
        self.player_bar = PlayerBar(self.screen, self._hero)
        self.statistic = Statistic(self.screen)

        self._map.render()      # Рисуем карту
        self.game.blit()
        self.mainloop()         # Цикл игры

    def mainloop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(FPS)  # Количество кадров в секунду
            [exit() for event in pygame.event.get() if event.type == pygame.QUIT]

            self.check_losed_game()
            if Events.isGameLoosed:
                self.statistic.show()
                continue

            self.player_movement()
            self.units_action()

            self.game.update()
            self.game_bar.update()
            self.player_bar.update()
            pygame.display.flip()
    # <<< Запуск игры


if __name__ == "__main__":
    engine = GameEngine()
    engine.start()
