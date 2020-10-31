# Необходимие библиотеки >>>
from abc import ABC, abstractmethod
import pygame
import time
import os
from PIL import Image
from maze import *

# Необходимые библиотеки <<<

# Константы
LOGGING = True  # Логи разработчика
ENEMIES_RANGE = (25, 100)  # Количество мобов на карте (от, до)
FPS = 15  # Количество кадров в секунду
WAYS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
FACE = {"up": (0, 0), "down": (0, 8), "left": (0, 0), "right": (8, 0)}
TAIL = {"up": (0, 8), "down": (0, 8), "left": (8, 0), "right": (8, 0)}
CHECKING = [(0, 1), (1, 0), (1, 1)]
VERSION = "0.6"
# Запуск перенесён в GameEngine
# Небольшие изменения и исправления

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
YELLOW = (255, 255, 0)
BLUE = (51, 102, 204)
PINK = (230, 50, 230)

# Размеры
MAP_SIZE = 51
PIXEL_SIZE = 10
STATUS_BAR = (MAP_SIZE * PIXEL_SIZE, 10 * PIXEL_SIZE)
DISPLAY_SIZE = (MAP_SIZE * PIXEL_SIZE, MAP_SIZE * PIXEL_SIZE + (2 * (STATUS_BAR[1])))
GAME_BAR = {"SIZE": STATUS_BAR, "POSITION": (0, 0)}
GAME = {"SIZE": (MAP_SIZE * PIXEL_SIZE, MAP_SIZE * PIXEL_SIZE), "POSITION": (0, GAME_BAR["SIZE"][1])}
PLAYER_BAR = {"SIZE": STATUS_BAR, "POSITION": (0, GAME["SIZE"][1] + GAME_BAR["SIZE"][1])}


# Воспомогательные функции >>>
def get_time (): return time.strftime('%x_%X')  # Время в консоли


def log (text):  # Логи разработчика
    if LOGGING: print(f"[{get_time()}] LOG: {text}")


# <<< Воспомогательные функции


class Position(ABC):  # Координаты объектов
    def __init__ (self, x=0, y=0):
        self.x = x
        self.y = y

    def change (self, x, y):
        self.x = x
        self.y = y

    def get_position (self):
        return self.x, self.y


class Unit(ABC):  # Общий класс для юнитов
    def __init__ (self, map, name, hp, ar, dmg, color):
        self.pos = Position()
        self._map = map
        self._name = name
        self._health = hp
        self._armor = ar
        self._damage = dmg
        self._MAXHEALTH = 200.0
        self.color = color
        self.face = 'down'

    # Характеристики >>>
    @property
    def map (self):
        return self._map

    @map.setter
    def map (self, map):
        self._map = map

    @property
    def health (self):
        return self._health

    @health.setter
    def health (self, hp):
        self._health = hp

    @property
    def damage (self):
        return self._damage

    @property
    def armor (self):
        return self._armor

    @property
    def name (self):
        return self._name

    @property
    def MAXHEALTH (self):
        return self._MAXHEALTH

    # <<< Характеристики

    # Действия >>>
    @abstractmethod
    def attack (self, unit):
        """Атака юнита unit"""
        raise NotImplementedError("Необходимо переопределить метод attack")

    def die (self, reason):
        print(f"[{get_time()}] {self.name} died - reason: {reason}.")
        pygame.draw.rect(engine.game.surf, WHITE,
                         (self.pos.x * PIXEL_SIZE, self.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
        self.map[self.pos.x][self.pos.y] = 1
        self.map.objects.remove(self)
        del self
        Events.isSomeoneDied = True

    # <<< Действия

    # Передвижение >>>
    @abstractmethod
    def move (self, direction):
        """Передвижение юнита"""
        raise NotImplementedError("Необходимо переопределить метод move")

    def get_distance_to (self, obj):
        if obj not in self.map.objects:
            log(f"{obj} isn't on the current map (level: {Map.get_current_level()}).")
        else:
            return ((self.pos.x - obj.pos.x) ** 2 + (self.pos.y - obj.pos.y) ** 2) ** (1 / 2)

    def unit_near_self_unit (self, unit):
        x, y = self.pos.x, self.pos.y
        X, Y = unit.pos.x, unit.pos.y
        if (abs(X - x), abs(Y - y)) in CHECKING:
            return True
        else:
            return False

    # <<< Передвижение


class Hero(Unit):  # Класс отвечающий за параметры главного героя
    def __init__ (self, map):
        super().__init__(map, "Hero", hp=200.0, ar=3.0, dmg=5.0, color=RED)
        map.spawnObject(self)
        self.score = 0
        self.heal_cooldown = 0

    # Передвижение >>>
    def move (self, way):
        x, y = self.pos.x + WAYS[way][0], self.pos.y + WAYS[way][1]
        self.face = way
        if self.map.isExit(x, y):
            self.map.update_map()
            Events.isPassedLevel = True
        elif self.map.isFree(x, y):
            pygame.draw.rect(engine.game.surf, WHITE,
                             (self.pos.x * PIXEL_SIZE, self.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            self.map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            self.map[self.pos.x][self.pos.y] = self
            self.map.render_object(self)
            Events.isHeroMoved = True
        # else: log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def heal (self, hp):
        if self.health >= self.MAXHEALTH:
            print(f"[{get_time()}] {self.name} already has max health ({self.health}/{self.MAXHEALTH}).")
        elif int(time.time()) < self.heal_cooldown + 5:
            print("Not now")
        else:
            print(f"[{get_time()}] {self.name}: +{hp} ({self.health}/{self.MAXHEALTH}).")
            self.health += hp
            self.heal_cooldown = int(time.time())
            Events.isHealthModified = True

    def teleport (self, x, y):
        self.map[self.pos.x][self.pos.y] = 1
        self.pos.change(x, y)
        self.map[self.pos.x][self.pos.y] = self

    # <<< Передвижение

    # Атака >>>
    def find_nearest_enemy (self):
        positions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1)]
        for pos in positions:
            enemy = self.map[self.pos.x + pos[0]][self.pos.y + pos[1]]
            if isinstance(enemy, Enemy): return enemy
        return None

    def attack (self, enemy):
        if enemy is None: return
        damage = (self.damage + random.randint(0, 3) - enemy.armor) * (0 if random.randint(0, 100) <= 10 else 1)
        enemy.health -= damage
        if damage:
            print(f"[{get_time()}] {self.name} inflict {damage} damage to {enemy.name} (HP: {enemy.health}).")
        else:
            print(f"[{get_time()}] {self.name} missed (HP: {enemy.health}).")
        if enemy.health <= 0:
            enemy.die(self.name)
            self.score += enemy.points
            Events.isScoredPoints = True
            print(f"[{get_time()}] {self.name} scored {enemy.points} point (Total score: {self.score}).")
    # <<< Атака


class Enemy(Unit):
    def __init__ (self, map, name, points, agr):
        super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0, color=PINK)
        randPoint = map.get_randomPoint()
        map.spawnObject(self, randPoint[0], randPoint[1])
        self.points = points
        self.agr_radius = agr

    # Передвижение >>>
    def move (self, way):
        x, y = self.pos.x + WAYS[way][0], self.pos.y + WAYS[way][1]
        self.face = way
        if self.map.isFree(x, y):
            pygame.draw.rect(engine.game.surf, WHITE,
                             (self.pos.x * PIXEL_SIZE, self.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            self.map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            self.map[self.pos.x][self.pos.y] = self
            self.map.render_object(self)
            Events.isSomeoneMoved = True
        # else: log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def wander (self):
        self.move(["left", "right", "up", "down"][random.randint(0, 3)])

    def haunt (self, player):
        cur_dist = self.get_distance_to(player)
        if cur_dist is None or self.agr_radius < cur_dist: return
        for way in WAYS.items():
            possibly_pos = (self.pos.x + way[1][0], self.pos.y + way[1][1])
            if not self.map.isFree(possibly_pos[0], possibly_pos[1]): continue
            possibly_dist = ((player.pos.x - possibly_pos[0]) ** 2 + (player.pos.y - possibly_pos[1]) ** 2) ** (1 / 2)
            if possibly_dist < cur_dist: self.move(way[0])
        if self.unit_near_self_unit(player):
            self.attack(player)

    # <<< Передвижение

    def attack (self, player):
        damage = (self._damage + random.randint(0, 3) - player.armor) * (0 if random.randint(0, 100) <= 10 else 1)
        if player.health - damage < 0:
            player.health = 0
        else:
            player.health -= damage
        if damage:
            print(f"[{get_time()}] {self.name} inflict {damage} damage to {player.name} (HP: {player.health}).")
            Events.isHealthModified = True
        else:
            print(f"[{get_time()}] {self.name} missed (HP: {player.health}).")
        if player.health <= 0: player.die(self.name)

    @staticmethod
    def get_OrkName ():
        start = ["Slog", "Ra", "Ro", "Og", "Kegi", "Zor", "Un", "Yag", "Black", "Mug", "Gud"]
        middle = "abcdeghklmnopqrst"
        end = ["ka", "rana", "all", "mash", "tan", "gu", "tag", "ge", "rim"]
        return start[random.randint(0, len(start)) - 1] + middle[random.randint(0, len(middle) - 1)] * random.randint(0,
                                                                                                                      1) + \
               end[random.randint(0, len(end) - 1)]


class Map(list):
    created_maps = 1

    def __init__ (self):
        super().__init__()
        self.size = 51
        self.objects = []
        self.create_map('map.png')
        self.spawn = None

    # Воспомогательные функции >>>
    @staticmethod
    def get_current_level ():
        return Map.created_maps

    def isWall (self, x, y):
        if self[x][y] == 0: return True
        return False

    def isExit (self, x, y):
        if self[x][y] == "exit": return True
        return False

    def isFree (self, x, y):
        if self[x][y] == 1: return True
        return False

    def get_randomPoint (self):
        random.seed(time.time())
        while True:
            x = random.randint(1, self.size - 1)
            y = random.randint(1, self.size - 1)
            if self.isFree(x, y): break
        return x, y

    def find_pos (self, obj):  # Найти позицию определённого объекта на карте
        for x in range(self.size):
            try:
                y = self[x].index(obj)
            except ValueError:
                continue
            else:
                return x, y
        return None, None

    # <<< Воспомогательные функции

    # Настройки карты >>>
    def create_map (self, path):  # Создание карты по картинке
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
                # elif pix[i, j][:3] == RED:
                # 	self[i].append(Enemy(map, f"Ork {Enemy.get_OrkName()}", random.randint(2, 5)))
                else:
                    self[i].append(0)
        if self.spawn is None: self.spawn = (1, 1)

    def gen_map (self):  # Генерация нового лабиринта
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
        im.putpixel((49, 49), BLACK)
        im.save("maze.png")

    def render_map (self):  # Отрисовка карты
        for j in range(self.size):
            for i in range(self.size):
                if self[i][j] == 1:
                    pygame.draw.rect(engine.game.surf, WHITE, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "exit":
                    pygame.draw.rect(engine.game.surf, BLACK, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "spawn":
                    pygame.draw.rect(engine.game.surf, YELLOW, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                else:
                    pygame.draw.rect(engine.game.surf, GREEN, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

    def render_objects (self):
        for obj in self.objects:
            self.render_object(obj)

    def render_object (self, obj):
        if obj not in self.objects:
            log(f"{obj} has not been spawned (not in map.objects)")
            return
        pygame.draw.rect(engine.game.surf, obj.color,
                         (obj.pos.x * PIXEL_SIZE, obj.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
        pygame.draw.rect(engine.game.surf, BLUE, ((obj.pos.x * PIXEL_SIZE) + FACE[obj.face][0],
                                                  (obj.pos.y * PIXEL_SIZE) + FACE[obj.face][1],
                                                  PIXEL_SIZE - TAIL[obj.face][0], PIXEL_SIZE - TAIL[obj.face][1]))

    def update_map (self):  # Обновить карту (заново отрегенить, расставить мобов итд)
        print(f"[{get_time()}] Level {Map.created_maps} has been passed.")
        for i in range(len(self.objects) - 1):
            self.objects[-1].die("level passed")
        os.remove("maze.png")
        self.gen_map()
        for i in range(len(self)): self.pop()
        self.create_map("maze.png")
        self.objects[0].teleport(self.spawn[0], self.spawn[1])
        self.render_map()
        [Enemy(self, f"Ork {Enemy.get_OrkName()}", random.randint(2, 5), 5.0) for i in
         range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1]))]
        self.render_objects()
        Map.created_maps += 1
        log(f"Level {Map.created_maps} has been started.")
        self.objects[0].score += 10

    def lose_game (self):
        for i in range(len(self.objects)):
            self.objects[-1].die("Player losed")
        for i in range(len(self)): self.pop()

    # <<< Настройки карты

    def spawnObject (self, obj, x=0, y=0):  # Спавн объекта на определённых координатах
        if isinstance(obj, Hero):  # Герой всегда на спавн-точке
            spawnCords = self.find_pos("spawn")
            if spawnCords is None:
                randPoint = self.get_randomPoint()
                x, y = randPoint[0], randPoint[1]
            else:
                x, y = spawnCords[0], spawnCords[1]
        elif self[x][y] != 1:
            return log(f"{obj} couldn't spawn on the wall (x:{x}, y:{y}).")
        self.objects.append(obj)
        obj.map = self
        self[x][y] = obj
        obj.pos.change(x, y)


class Events:
    isScoredPoints = False
    isPassedLevel = False
    isHealthModified = False
    isArmorModified = False
    isSomeoneMoved = False
    isHeroMoved = False
    isSomeoneDied = False
    isHeroDied = False
    isLose = False

    @staticmethod
    def get_game_events ():
        return Events.isSomeoneDied, Events.isSomeoneMoved, Events.isHeroMoved, Events.isHeroDied

    @staticmethod
    def get_playerbar_events ():
        return Events.isHealthModified, Events.isArmorModified

    @staticmethod
    def get_gamebar_events ():
        return Events.isScoredPoints, Events.isPassedLevel


class Surface(ABC):  # Класс блоков
    def __init__ (self, screen, size, position):
        self.screen = screen
        self.size = size
        self.position = position
        self.surf = pygame.Surface(size)


class ISurface(ABC):
    @abstractmethod
    def update (self):
        """Обновление поверхности"""
        raise NotImplementedError("Необходимо переопределить метод update")

    @abstractmethod
    def blit (self):
        """Наложение всех деталей на поверхность"""
        raise NotImplementedError("Необходимо переопределить метод blit")


class Game(Surface, ISurface):
    def __init__ (self, screen):
        super().__init__(screen, GAME["SIZE"], GAME["POSITION"])
        self.font = pygame.font.Font("font.ttf", 40)
        self.message = None
        self.message_rect = None

    def update (self):
        if True in Events.get_game_events():
            if Events.isSomeoneMoved: Events.isSomeoneMoved = False
            if Events.isHeroMoved: Events.isHeroMoved = False
            if Events.isSomeoneDied: Events.isSomeoneDied = False
            if Events.isHeroDied: Events.isHeroDied = False
            self.blit()

    def blit (self):
        self.screen.blit(self.surf, self.position)

    def lose (self, colour):
        self.surf.fill((colour, colour, colour))
        self.message = self.font.render("YOU DIED", 1, (255, colour, 0))
        self.message_rect = self.message.get_rect(
            center=(GAME["SIZE"][0] / 2, ((GAME["SIZE"][1] / 2) + GAME["POSITION"][1])))
        self.blit()
        self.screen.blit(self.message, self.message_rect)


class StatusBar(Surface, ABC):
    def __init__ (self, screen, size, position, margin=None):
        super().__init__(screen, size, position)
        self.margin = (PIXEL_SIZE * 3, PIXEL_SIZE) if margin is None else margin
        self.font = pygame.font.Font("font.ttf", 40)


class GameBar(StatusBar, ISurface):
    def __init__ (self, screen, player):
        super().__init__(screen, GAME_BAR["SIZE"], GAME_BAR["POSITION"])
        self.player = player
        self.score = None
        self.level = None

        self.__scoreSize = ((self.size[0] - self.margin[1] * 2) * 2 // 3, self.size[1] - self.margin[0] * 2)
        self.__scorePosition = (self.position[0] + self.margin[1], self.margin[0])
        self.__levelSize = ((self.size[0] - self.margin[1] * 2) // 3, self.size[1] - self.margin[0] * 2)
        self.__levelPosition = (self.__scoreSize[0] + self.margin[1], self.margin[0])

        self.blit()

    def update (self):
        if True in Events.get_gamebar_events():
            if Events.isScoredPoints: Events.isScoredPoints = False
            if Events.isPassedLevel: Events.isPassedLevel = False
            self.blit()

    def blit (self):
        self.surf.fill(GREEN)
        self.score = self.font.render(f"Score: {self.player.score}", True, WHITE)
        self.level = self.font.render(f"LVL: {Map.get_current_level()}", True, WHITE)
        self.surf.blit(self.score, self.__scorePosition)
        self.surf.blit(self.level, self.__levelPosition)
        self.screen.blit(self.surf, self.position)


class PlayerBar(StatusBar, ISurface):
    def __init__ (self, screen, player):
        super().__init__(screen, PLAYER_BAR["SIZE"], PLAYER_BAR["POSITION"])
        self.player = player
        self.heroHP = None
        self.heroAR = None

        self.__HPSize = ((self.size[0] - self.margin[1] * 2) * 2 // 3, self.size[1] - self.margin[0] * 2)
        self.__HPPosition = (self.position[0] + self.margin[1], self.margin[0])
        self.__ARSize = ((self.size[0] - self.margin[1] * 2) // 3, self.size[1] - self.margin[0] * 2)
        self.__ARPosition = (self.__HPSize[0] + self.margin[1], self.margin[0])

        self.blit()

    def update (self):
        if True in Events.get_playerbar_events():
            if Events.isHealthModified: Events.isHealthModified = False
            if Events.isArmorModified: Events.isArmorModified = False
            self.blit()

    def blit (self):
        self.surf.fill(GREEN)
        self.heroHP = self.font.render(f"HP: {int(self.player.health)}/{int(self.player.MAXHEALTH)}", True, WHITE)
        self.heroAR = self.font.render(f"AR: {self.player.armor}", True, WHITE)
        self.surf.blit(self.heroHP, self.__HPPosition)
        self.surf.blit(self.heroAR, self.__ARPosition)
        self.screen.blit(self.surf, self.position)


class GameEngine:
    def __init__ (self):
        self.screen = pygame.display.set_mode(DISPLAY_SIZE)
        self.game = None
        self.game_bar = None
        self.player_bar = None
        self.font = None
        self.timer = 0
        self._map = None
        self._hero = None

    def start (self):
        pygame.init()
        pygame.display.set_caption(f"CaveX v{VERSION}")

        # Игровые объекты
        self._map = Map()
        self._hero = Hero(self._map)
        [Enemy(self._map, f"Ork {Enemy.get_OrkName()}", random.randint(2, 5), 5.0) for i in
         range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1]))]
        self.timer = int(time.time())

        # Инициализация блоков
        self.game_bar = GameBar(self.screen, self._hero)
        self.game = Game(self.screen)
        self.player_bar = PlayerBar(self.screen, self._hero)

        self._map.render_map()  # Рисуем карту
        self._map.render_objects()  # Рисуем каждый объект
        log(self._hero.health)
        self.mainloop()

    def mainloop (self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(FPS)  # Количество кадров в секунду
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self._hero.heal(50)

            # Управление >>>
            key = pygame.key.get_pressed()  # Выполнение передвижение пока зажата клавиша
            if key[pygame.K_LEFT] or key[pygame.K_a]:  # Клавиша передвижение влево
                self._hero.move("left")
            if key[pygame.K_RIGHT] or key[pygame.K_d]:  # Клавиша передвижение вправо
                self._hero.move("right")
            if key[pygame.K_UP] or key[pygame.K_w]:  # Клавиша передвижение вверх
                self._hero.move("up")
            if key[pygame.K_DOWN] or key[pygame.K_s]:  # Клавиша передвижение вниз
                self._hero.move("down")
            if key[pygame.K_SPACE]:
                self._hero.attack(self._hero.find_nearest_enemy())
            if len(self._map.objects) > 1:  # Передвижение мобов
                enemy = self._map.objects[random.randint(1, len(self._map.objects) - 1)]
                if isinstance(enemy, Enemy): enemy.wander()
            if self.timer != int(time.time()):  # Охота мобов на перса
                self.timer = int(time.time())
                for unit in self._map.objects[1:]:
                    if isinstance(unit, Enemy): unit.haunt(self._hero)

            # <<< Управление
            if self._hero.health == 0:
                if Events.isLose == False:
                    self._map.lose_game()
                    self.player_bar.update()
                    colour = 105
                    clock = pygame.time.Clock()
                    while colour > -5:
                        clock.tick(10)
                        self.game.lose(colour)
                        colour -= 10
                        pygame.display.flip()  # Обновление дисплея окна игры
                    Events.isLose = True
            else:
                self.game.update()
                self.game_bar.update()
                self.player_bar.update()
                pygame.display.flip()


if __name__ == "__main__":
    engine = GameEngine()
    engine.start()
