# Необходимие библиотеки >>>
from abc import ABC, abstractmethod
import pygame
import time
import os
from PIL import Image
from maze import *
# Необходимые библиотеки <<<

# Константы
LOGGING = True              # Логи разработчика
ENEMIES_RANGE = (25, 100)   # Количество мобов на карте (от, до)
VERSION = "0.5.2.3"
# улучшена производительность (оптимизация рисовки): 6-8% to <2%
# Статус бары разделены на отдельные классы, но рисуется пока что только верхняя панель
# для проверок создан класс Event
# TODO: Разобраться с нижней панелькой (она не рисуется)
# TODO: Перенести кусок про энеми (идут к герою) в класс энеми
# TODO: Подумать над интерфейсами

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
YELLOW = (255, 255, 0)
BLUE = (29, 32, 76)
PINK = (230, 50, 230)

# Размеры
MAP_SIZE = 51
PIXEL_SIZE = 10
STATUS_BAR = (MAP_SIZE * PIXEL_SIZE, 10 * PIXEL_SIZE)
DISPLAY_SIZE = (MAP_SIZE * PIXEL_SIZE, MAP_SIZE * PIXEL_SIZE + (2 * (STATUS_BAR[1])))
GAME_BAR = {"SIZE": STATUS_BAR, "POSITION": (0, 0)}
GAME = {"SIZE": (MAP_SIZE * PIXEL_SIZE, MAP_SIZE * PIXEL_SIZE), "POSITION": (0, GAME_BAR["SIZE"][1])}
PLAYER_BAR = {"SIZE": STATUS_BAR, "POSITION": (0, GAME["SIZE"][1] + GAME_BAR["SIZE"][1])}
print(PLAYER_BAR["POSITION"])


# Воспомогательные функции >>>
def get_time(): return time.strftime('%x_%X')  # Время в консоли


def log(text):  # Логи разработчика
    if LOGGING: print(f"[{get_time()}] LOG: {text}")
# <<< Воспомогательные функции


class Position(ABC):  # Координаты объектов
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
        self.__map = map
        self._name = name
        self._health = hp
        self._armor = ar
        self._damage = dmg
        self._MAXHEALTH = 200.0
        self.color = color

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
        pygame.draw.rect(game, WHITE, (self.pos.x * PIXEL_SIZE, self.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
        map[self.pos.x][self.pos.y] = 1
        map.objects.remove(self)
        del self

    def heal(self, hp):
        if self.health >= self.MAXHEALTH:
            print(f"[{get_time()}] {self.name} already has max health ({self.health}/{self.MAXHEALTH}).")
        else:
            print(f"[{get_time()}] {self.name}: +{hp} ({self.health}/{self.MAXHEALTH}).")
            self.health += hp
    # <<< Действия

    # Передвижение >>>
    @abstractmethod
    def move(self, direction):
        """Передвижение юнита"""
        raise NotImplementedError("Необходимо переопределить метод move")

    def get_distance_to(self, obj):
        if obj not in map.objects:
            log(f"{obj} isn't on the current map (level: {map.get_current_level()}).")
        else:
            return ((self.pos.x - obj.pos.x) ** 2 + (self.pos.y - obj.pos.y) ** 2) ** (1 / 2)
    # <<< Передвижение


class Hero(Unit):  # Класс отвечающий за параметры главного героя
    def __init__(self, map):
        super().__init__(map, "Hero", hp=200.0, ar=0.0, dmg=5.0, color=RED)
        map.spawnObject(self)
        self.score = 0

    # Передвижение >>>
    def move(self, way):
        ways = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        x, y = self.pos.x + ways[way][0], self.pos.y + ways[way][1]
        if map.isExit(x, y):
            map.update_map()
            Events.isPassedLevel = True
        elif map.isFree(x, y):
            pygame.draw.rect(game, WHITE, (self.pos.x * PIXEL_SIZE, self.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            map[self.pos.x][self.pos.y] = self
            map.render_object(self)
        # else: log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def teleport(self, x, y):
        map[self.pos.x][self.pos.y] = 1
        self.pos.change(x, y)
        map[self.pos.x][self.pos.y] = self
    # <<< Передвижение

    # Атака >>>
    def find_nearest_enemy(self):
        positions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1)]
        for pos in positions:
            enemy = map[self.pos.x + pos[0]][self.pos.y + pos[1]]
            if isinstance(enemy, Enemy): return enemy
        return None

    def attack(self, enemy):
        if enemy is None: return
        damage = (self.damage + random.randint(0, 3) - enemy.armor) * (0 if random.randint(0, 100) <= 10 else 1)
        enemy.health -= damage
        if damage: print(f"[{get_time()}] {self.name} inflict {damage} damage to {enemy.name} (HP: {enemy.health}).")
        else: print(f"[{get_time()}] {self.name} missed (HP: {enemy.health}).")
        if enemy.health <= 0:
            enemy.die(self.name)
            self.score += enemy.points
            Events.isScoredPoints = True
            print(f"[{get_time()}] {self.name} scored {enemy.points} point (Total score: {self.score}).")
    # <<< Атака


class Enemy(Unit):
    def __init__(self, map, name, points, agr):
        super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0, color=PINK)
        randPoint = map.get_randomPoint()
        map.spawnObject(self, randPoint[0], randPoint[1])
        self.points = points
        self.agr_radius = agr

    def move(self, way):
        ways = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        x, y = self.pos.x + ways[way][0], self.pos.y + ways[way][1]
        if map.isFree(x, y):
            pygame.draw.rect(game, WHITE, (self.pos.x * PIXEL_SIZE, self.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            map[self.pos.x][self.pos.y] = self
            map.render_object(self)
        # else: log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def attack(self, player):
        damage = (self._damage + random.randint(0, 3) - player.armor) * (0 if random.randint(0, 100) <= 10 else 1)
        player.health -= damage
        if damage:
            print(f"[{get_time()}] {self.name} inflict {damage} damage to {player.name} (HP: {player.health}).")
            Events.isHealthModified = True
        else: print(f"[{get_time()}] {self.name} missed (HP: {hero.health}).")
        if hero.health <= 0: hero.die(self.name)

    @staticmethod
    def get_OrkName():
        start = ["Slog", "Ra", "Ro", "Og", "Kegi", "Zor", "Un", "Yag", "Black", "Mug", "Gud"]
        middle = "abcdeghklmnopqrst"
        end = ["ka", "rana", "all", "mash", "tan", "gu", "tag", "ge", "rim"]
        return start[random.randint(0, len(start))-1] + middle[random.randint(0, len(middle)-1)]*random.randint(0, 1) + end[random.randint(0, len(end)-1)]


class Map(list):
    size_list = {"S": 51}
    created_maps = 1

    def __init__(self, size):
        super().__init__()
        self.size = Map.size_list[size]
        self.objects = []
        self.create_map('map.png')
        self.spawn = None

    # Воспомогательные функции >>>
    @staticmethod
    def get_current_level():
        return Map.created_maps

    def isWall(self, x, y):
        if self[x][y] == 0: return True
        return False

    def isExit(self, x, y):
        if self[x][y] == "exit": return True
        return False

    def isFree(self, x, y):
        if self[x][y] == 1: return True
        return False

    def get_randomPoint(self):
        random.seed(time.time())
        while True:
            x = random.randint(1, self.size - 1)
            y = random.randint(1, self.size - 1)
            if self.isFree(x, y): break
        return x, y

    def find_pos(self, obj):    # Найти позицию определённого объекта на карте
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
                # elif pix[i, j][:3] == RED:
                # 	self[i].append(Enemy(map, f"Ork {Enemy.get_OrkName()}", random.randint(2, 5)))
                else:
                    self[i].append(0)
        if self.spawn is None: self.spawn = (1, 1)

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
        im.putpixel((49, 49), BLACK)
        im.save("maze.png")

    def render_map(self):   # Отрисовка карты
        for j in range(self.size):
            for i in range(self.size):
                if self[i][j] == 1:
                    pygame.draw.rect(game, WHITE, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                # elif isinstance(self[i][j], Unit):
                #     pygame.draw.rect(game, self[i][j].color, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "exit":
                    pygame.draw.rect(game, BLACK, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "spawn":
                    pygame.draw.rect(game, YELLOW, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                else:
                    pygame.draw.rect(game, GREEN, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

    def render_objects(self):
        for obj in self.objects:
            self.render_object(obj)

    def render_object(self, obj):
        if obj not in self.objects:
            log(f"{obj} has not been spawned (not in map.objects)")
            return
        pygame.draw.rect(game, obj.color, (obj.pos.x * PIXEL_SIZE, obj.pos.y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

    def update_map(self):    # Обновить карту (заново отрегенить, расставить мобов итд)
        print(f"[{get_time()}] Level {Map.created_maps} has been passed.")
        for i in range(len(self.objects)-1):
            self.objects[-1].die("level passed")
            # self.objects.pop()
        os.remove("maze.png")
        self.gen_map()
        for i in range(len(self)):
            self.pop()
        self.create_map("maze.png")
        self.objects[0].teleport(self.spawn[0], self.spawn[1])
        self.render_map()
        [Enemy(map, f"Ork {Enemy.get_OrkName()}", random.randint(2, 5), 5.0) for i in range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1]))]
        self.render_objects()
        Map.created_maps += 1
        log(f"Level {Map.created_maps} has been started.")
        self.objects[0].score += 10

    # <<< Настройки карты
    def spawnObject(self, object, x=0, y=0):    # Спавн объекта на определённых координатах
        if isinstance(object, Hero):  # Герой всегда на спавн-точке
            spawnCords = self.find_pos("spawn")
            if spawnCords is None:
                randPoint = self.get_randomPoint()
                x, y = randPoint[0], randPoint[1]
            else: x, y = spawnCords[0], spawnCords[1]
        elif self[x][y] != 1:
            return log(f"{object} couldn't spawn on the wall (x:{x}, y:{y}).")
        self.objects.append(object)
        object.map = self
        self[x][y] = object
        object.pos.change(x, y)


class Events:
    isScoredPoints = False
    isPassedLevel = False
    isHealthModified = False
    isArmorModified = False


class StatusBar(ABC):
    def __init__(self, screen, size, position):
        self.screen = screen
        self.size = size
        self.position = position
        self.surf = pygame.Surface(size)
        self.surf.fill(GREEN)
        self.margin = (30, 10)

    def update(self):
        """Обновление данных"""
        raise NotImplementedError("Необходимо переопределить метод update")

    def blit(self):
        """Отрисовка статусбара"""
        raise NotImplementedError("Необходимо переопределить метод blit")


class GameBar(StatusBar):
    def __init__(self, screen, player):
        super().__init__(screen, GAME_BAR["SIZE"], GAME_BAR["POSITION"])
        self.player = player
        self.score = None
        self.level = None

        self.__scoreSize = ((self.size[0] - self.margin[1] * 2) * 2 // 3, self.size[1] - self.margin[0] * 2)
        self.__scorePosition = (self.position[0]+self.margin[1], self.position[1]+self.margin[0])
        self.__levelSize = ((self.size[0] - self.margin[1] * 2) // 3, self.size[1] - self.margin[0] * 2)
        self.__levelPosition = (self.__scoreSize[0] + self.margin[1], self.position[1] + self.margin[0])

        # dev logs
        print(self)
        print(self.__scoreSize, self.__scorePosition)
        print(self.__levelSize, self.__levelPosition)

        self.blit()

    def update(self):
        if Events.isScoredPoints or Events.isPassedLevel:
            if Events.isScoredPoints: Events.isScoredPoints = False
            if Events.isPassedLevel: Events.isPassedLevel = False
            self.blit()

    def blit(self):
        self.surf.fill(GREEN)
        self.score = font.render(f"Score: {self.player.score}", True, WHITE)
        self.level = font.render(f"LVL: {Map.get_current_level()}", True, WHITE)
        self.surf.blit(self.score, self.__scorePosition)
        self.surf.blit(self.level, self.__levelPosition)
        self.screen.blit(self.surf, self.position)


class PlayerBar(StatusBar):
    def __init__(self, screen, player):
        super().__init__(screen, PLAYER_BAR["SIZE"], PLAYER_BAR["POSITION"])
        self.player = player
        self.heroHP = None
        self.heroAR = None

        self.__HPSize = ((self.size[0] - self.margin[1] * 2) * 2 // 3, self.size[1] - self.margin[0] * 2)
        self.__HPPosition = (self.position[0] + self.margin[1], self.position[1] + self.margin[0])
        self.__ARSize = ((self.size[0] - self.margin[1] * 2) // 3, self.size[1] - self.margin[0] * 2)
        self.__ARPosition = (self.__HPSize[0] + self.margin[1], self.position[1] + self.margin[0])

        # dev logs
        print(self)
        print(self.__HPSize, self.__HPPosition)
        print(self.__ARSize, self.__ARPosition)

        self.blit()

    def update(self):
        if Events.isHealthModified or Events.isArmorModified:
            if Events.isHealthModified: Events.isHealthModified = False
            if Events.isArmorModified: Events.isArmorModified = False
            self.blit()

    def blit(self):
        self.surf.fill(GREEN)
        self.heroHP = font.render(f"HP: {int(self.player.health)}/{int(self.player.MAXHEALTH)}", True, WHITE)
        self.heroAR = font.render(f"AR: {self.player.armor}", True, WHITE)
        self.surf.blit(self.heroHP, self.__HPPosition)
        self.surf.blit(self.heroAR, self.__ARPosition)
        self.screen.blit(self.surf, self.position)


if __name__ == "__main__":
    map = Map("S")
    hero = Hero(map)
    [Enemy(map, f"Ork {Enemy.get_OrkName()}", random.randint(2, 5), 5.0) for i in range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1]))]
    time_in_sec = int(time.strftime("%S"))

    # Инициализация игры
    pygame.init()
    sc = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption(f"CaveX v{VERSION}")
    font = pygame.font.Font("font.ttf", 40)

    game_bar = GameBar(sc, hero)
    game = pygame.Surface(GAME["SIZE"])
    player_bar = PlayerBar(sc, hero)

    sc.fill(GREEN)  # Зарисовка фона
    map.render_map()  # Рисуем карту
    map.render_objects()  # Рисуем каждый объект
    sc.blit(game, GAME["POSITION"])
    sc.blit(game_bar.surf, game_bar.position)
    sc.blit(player_bar.surf, player_bar.position)

    isGame = True
    while isGame:
        pygame.time.delay(60)  # Задержка обновления экрана игры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isGame = False

        # Управление >>>
        key = pygame.key.get_pressed()  # Выполнение передвижение пока зажата клавиша
        if key[pygame.K_LEFT] or key[pygame.K_a]:  # Клавиша передвижение влево
            hero.move("left")
        if key[pygame.K_RIGHT] or key[pygame.K_d]:  # Клавиша передвижение вправо
            hero.move("right")
        if key[pygame.K_UP] or key[pygame.K_w]:  # Клавиша передвижение вверх
            hero.move("up")
        if key[pygame.K_DOWN] or key[pygame.K_s]:  # Клавиша передвижение вниз
            hero.move("down")
        if key[pygame.K_SPACE]:
            hero.attack(hero.find_nearest_enemy())
        if len(map.objects) > 1:    # Передвижение мобов
            map.objects[random.randint(1, len(map.objects)-1)].move(["left", "right", "up", "down"][random.randint(0, 3)])
        # <<< Управление

        # Идея такая, но надо передалать во что-то адекватное
        # Энеми идут к герою, если тот попадает в их поле зрения (увы, сквозь стену тоже)
        if time_in_sec != int(time.strftime("%S")):
            time_in_sec = int(time.strftime("%S"))
            for unit in map.objects:
                if not isinstance(unit, Enemy): continue
                cur_dist = unit.get_distance_to(hero)
                if cur_dist is None or unit.agr_radius < cur_dist: continue
                ways = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
                # hero = map.objects[0] // это для переноса этого ужаса в нормальный класс
                for way in ways.items():
                    possibly_pos = (unit.pos.x + way[1][0], unit.pos.y + way[1][1])
                    if not map.isFree(possibly_pos[0], possibly_pos[1]): continue
                    possibly_dist = ((hero.pos.x - possibly_pos[0])**2 + (hero.pos.y - possibly_pos[1])**2) ** (1/2)
                    if possibly_dist < cur_dist: unit.move(way[0])

        sc.blit(game, GAME["POSITION"])
        game_bar.update()
        player_bar.update()
        pygame.display.flip()  # Обновление дисплея окна игры
