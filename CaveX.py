# Необходимие библиотеки >>>
import pygame
import time
import os
from PIL import Image
from maze import *
# Необходимые библиотеки <<<

# Константы
LOGGING = True              # Логи разработчика
ENEMIES_RANGE = (25, 100)   # Количество мобов на карте (от, до)
VERSION = "0.5.1"

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
YELLOW = (255, 255, 0)
BLUE = (29, 32, 76)
PINK = (230, 50, 230)

# Размеры
PIXEL_SIZE = 10
MARGIN = 6
display_width = 510
display_height = 560 + (10 * (MARGIN+1))

# Инициализация игры
pygame.init()
sc = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption(f"CaveX v{VERSION}")
font = pygame.font.Font("font.ttf", 35)


# Воспомогательные функции >>>
def get_time(): return time.strftime('%x_%X')  # Время в консоли


def log(text):  # Логи разработчика
    if LOGGING: print(f"[{get_time()}] LOG: {text}")
# <<< Воспомогательные функции


class Position:  # Координаты объектов
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def change(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y


class Unit:  # Общий класс для юнитов
    def __init__(self, map, name, hp, ar, dmg):
        self.pos = Position()
        self.__map = map
        self._name = name
        self._health = hp
        self._armor = ar
        self._damage = dmg
        self._MAXHEALTH = 200.0

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
    def attack(self):
        positions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1)]
        for pos in positions:
            unit = map[self.pos.x + pos[0]][self.pos.y + pos[1]]
            if isinstance(unit, Unit) or (isinstance(self, Enemy) and isinstance(unit, Hero)):
                damage = (self._damage + random.randint(0, 3) - unit._armor) * (0 if random.randint(0, 100) <= 10 else 1)
                unit.health -= damage
                if damage: print(f"[{get_time()}] {self.name} inflict {damage} damage to {unit.name} (HP: {unit.health}).")
                else: print(f"[{get_time()}] {self.name} missed (HP: {unit.health}).")
                if unit.health <= 0:
                    unit.die(self.name)
                    if isinstance(self, Hero) and isinstance(unit, Enemy):
                        self.score += unit.points
                        print(f"[{get_time()}] {self.name} scored {unit.points} point (Total score: {self.score}).")

    def die(self, reason):
        print(f"[{get_time()}] {self.name} died - reason: {reason}.")
        cords = self.pos.get_position()
        map[cords[0]][cords[1]] = 1
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
    def move(self, way):
        ways = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        x, y = self.pos.x + ways[way][0], self.pos.y + ways[way][1]
        if map.isWall(x, y):
            return
        elif map.isExit(x, y) and isinstance(self, Hero):
            map.update_map()
        elif map.isFree(x, y):
            map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            map[self.pos.x][self.pos.y] = self
            map.render_map()
        else:
            log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def teleport(self, x, y):
        map[self.pos.x][self.pos.y] = 1
        self.pos.change(x, y)
        map[self.pos.x][self.pos.y] = self
        map.render_map()

    def get_distance(self, object):
        if object not in map.objects:
            log(f"{object} isn't on the current map (level: {map.get_current_level()}.")
        else:
            return ((self.pos.x - object.pos.x) ** 2 + (self.pos.y - object.pos.y) ** 2) ** (1 / 2)
    # <<< Передвижение


class Hero(Unit):  # Класс отвечающий за параметры главного героя
    def __init__(self, map):
        super().__init__(map, "Hero", hp=200.0, ar=0.0, dmg=5.0)
        map.spawnObject(self)
        self._score = 0

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    def say(self, text):
        print(f"[{get_time()}] {self} said: '{text}'")


class Enemy(Unit):
    def __init__(self, map, name, points, agr):
        super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0)
        randPoint = map.get_randomPoint()
        map.spawnObject(self, randPoint[0], randPoint[1])
        self.points = points
        self.agr_radius = agr

    @staticmethod
    def get_OrkName():
        start = ["Slog", "Ra", "Ro", "Og", "Kegi", "Zor", "Un", "Yag", "Black", "Mug", "Gud"]
        middle = "abcdeghklmnopqrst"
        end = ["ka", "rana", "all", "mash", "tan", "gu", "tag", "ge", "rim"]
        return start[random.randint(0, len(start))-1] + middle[random.randint(0, len(middle)-1)]*random.randint(0,1) + end[random.randint(0, len(end)-1)]


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
                if self[i][j] == 0:
                    pygame.draw.rect(sc, GREEN, (i * PIXEL_SIZE, (j + MARGIN) * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == 1:
                    pygame.draw.rect(sc, WHITE, (i * PIXEL_SIZE, (j + MARGIN) * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif isinstance(self[i][j], Hero):
                    pygame.draw.rect(sc, RED, (i * PIXEL_SIZE, (j + MARGIN) * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "exit":
                    pygame.draw.rect(sc, BLACK, (i * PIXEL_SIZE, (j + MARGIN) * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "spawn":
                    pygame.draw.rect(sc, YELLOW, (i * PIXEL_SIZE, (j + MARGIN) * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif isinstance(self[i][j], Enemy):
                    pygame.draw.rect(sc, PINK, (i * PIXEL_SIZE, (j + MARGIN) * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

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


if __name__ == "__main__":
    map = Map("S")
    hero = Hero(map)
    [Enemy(map, f"Ork {Enemy.get_OrkName()}", random.randint(2, 5), 5.0) for i in range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1]))]
    time_in_sec = int(time.strftime("%S"))

    isGame = True
    while isGame:
        pygame.time.delay(60)  # Задержка обновления экрана игры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isGame = False
        sc.fill(GREEN)  # Зарисовка фона

        map.render_map()  # Прорисовывает каждый объект программы
        # Интерфейс >>>
        heroScore = font.render(f"Score: {hero.score}", True, WHITE)                        # Очки героя
        mapLevel = font.render(f"LVL: {map.get_current_level()}", True, WHITE)              # Пройденных уровней
        heroHP = font.render(f"HP: {int(hero.health)}/{int(hero.MAXHEALTH)}", True, WHITE)  # Здоровье героя
        heroAR = font.render(f"AR: {hero.armor}", True, WHITE)                              # Защита героя
            # Отрисовка текста
        sc.blit(heroScore, (PIXEL_SIZE, PIXEL_SIZE*2))
        sc.blit(mapLevel, (display_width - display_width//3 + PIXEL_SIZE, PIXEL_SIZE*2))
        sc.blit(heroHP, (PIXEL_SIZE, display_height - PIXEL_SIZE * (MARGIN - 1)))
        sc.blit(heroAR, (display_width - display_width//3 + PIXEL_SIZE, display_height - PIXEL_SIZE * (MARGIN - 1)))
        # <<< Интерфейс

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
            hero.attack()
        if len(map.objects) > 1:    # Передвижение мобов
            map.objects[random.randint(1, len(map.objects)-1)].move(["left", "right", "up", "down"][random.randint(0, 3)])
        # <<< Управление

        # Идея такая, но надо передалать во что-то адекватное
        # Энеми идут к герою, если тот попадает в их поле зрения (увы, сквозь стену тоже)
        if time_in_sec != int(time.strftime("%S")):
            time_in_sec = int(time.strftime("%S"))
            for unit in map.objects:
                if not isinstance(unit, Enemy): continue
                cur_dist = unit.get_distance(hero)
                if unit.agr_radius < cur_dist: continue
                ways = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
                # hero = map.objects[0] // это для переноса этого ужаса в нормальный класс
                for way in ways.items():
                    possibly_pos = (unit.pos.x + way[1][0], unit.pos.y + way[1][1])
                    if not map.isFree(possibly_pos[0], possibly_pos[1]): continue
                    possibly_dist = ((hero.pos.x - possibly_pos[0])**2 + (hero.pos.y - possibly_pos[1])**2) ** (1/2)
                    if possibly_dist < cur_dist: unit.move(way[0])

        pygame.display.update()  # Обновление дисплея окна игры
