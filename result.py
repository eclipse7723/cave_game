import pygame
import time
import random
from PIL import Image


def get_time():
    return time.strftime('%x_%X')


VERSION = "0.4"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
YELLOW = (255, 255, 0)
BLUE = (29, 32, 76)
PINK = (230, 50, 230)

display_width = 510
display_height = 560
PIXEL_SIZE = 10

pygame.init()
sc = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption(f"CaveX v{VERSION}")

font = pygame.font.Font(None, 50)


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def change(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y


class Unit:
    def __init__(self, map, name, hp, ar, dmg):
        self.pos = Position()
        self.__map = map
        self._name = name
        self._health = hp
        self._armor = ar
        self._damage = dmg
        self._MAXHEALTH = 200.0

    def __repr__(self):
        return self._name

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
        positions = [[0, 1], [1, 0], [1, 1], [0, -1], [-1, 0], [-1, -1], [-1, 1], [1, -1]]
        for pos in positions:
            unit = map[self.pos.x + pos[0]][self.pos.y + pos[1]]
            if isinstance(unit, Unit):
                damage = self._damage + random.randint(0, 3) - unit._armor
                unit.health -= damage
                print(f"[{get_time()}] {self.name} inflict {damage} damage to {unit} (HP: {unit.health}).")
                if unit.health <= 0:
                    unit.die(self)
                    if isinstance(self, Hero) and isinstance(unit, Enemy):
                        self.score += unit.points
                    print(f"[{get_time()}] {self.name} scored {unit.points} point (Total score: {self.score}).")

    def die(self, reason="Cheats"):
        print(f"[{get_time()}] {self.name} died - reason: {reason}.")
        cords = self.pos.get_position()
        map[cords[0]][cords[1]] = 1
        del self

    def heal(self, hp):
        if self._health >= self.MAXHEALTH:
            print(f"[{get_time()}] {self.name} already has max health ({self._health}/{self.MAXHEALTH}).")
        else:
            print(f"[{get_time()}] {self.name}: +{hp} ({self._health}/{self.MAXHEALTH}).")
            self._health += hp
    # <<< Действия

    # Передвижение >>>
    def move(self, way):
        ways = {"up": [0, -1], "down": [0, 1], "left": [-1, 0], "right": [1, 0]}
        x, y = self.pos.x + ways[way][0], self.pos.y + ways[way][1]
        if map.isWall(x, y):
            print(f"[{get_time()}] {self} couldn't go on the wall (x:{x}, y:{y}).")
        elif map.isFree(x, y):
            if map.isExit(x, y):
                map.update_map()
            else:
                map[self.pos.x][self.pos.y] = 1
                self.pos.change(x, y)
                map[self.pos.x][self.pos.y] = self
                print(f"[{get_time()}] {self} successfully went {way}.")
                map.render_map()
        else:
            print(f"[{get_time()}] {self} cannot go this way (x:{x}, y:{y}).")

    def teleport(self, x, y):
        map[self.pos.x][self.pos.y] = 1
        self.pos.change(x, y)
        map[self.pos.x][self.pos.y] = self
        map.render_map()

    def get_distance(self, object):
        if object not in map.objects:
            print(f"[{get_time()}] {object} isn't on the current map (level: {map.get_current_level()}.")
        else:
            return ((self.pos.x - object.pos.x) ** 2 + (self.pos.y - object.pos.y) ** 2) ** (1 / 2)
    # <<< Передвижение


class Hero(Unit):
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
    def __init__(self, map, name, points):
        super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0)
        randPoint = map.get_randomPoint()
        map.spawnObject(self, randPoint[0], randPoint[1])
        self.points = points


class Map(list):
    size_list = {"S": 51}
    created_maps = 1

    def __init__(self, size):
        super().__init__()
        self.size = Map.size_list[size]
        self.objects = []
        self.create_map()

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
        if self[x][y] == 1 or self[x][y] == "exit": return True
        return False

    def get_randomPoint(self):
        random.seed(time.time())
        while True:
            x = random.randint(1, self.size - 1)
            y = random.randint(1, self.size - 1)
            if self.isFree(x, y): break
        return [x, y]

        # Найти позицию определённого объекта на карте
    def find_pos(self, obj):
        for y in range(self.size):
            try:
                x = self[y].index(obj)
            except ValueError:
                continue
            else:
                return [x, y]
        return [0, 0]

    # <<< Воспомогательные функции

    # Настройки карты >>>
        # Генерация карты по картинке
    def create_map(self):
        im = Image.open('map.png')
        pix = im.load()
        for i in range(self.size):
            self.append([])
            for j in range(self.size):
                if pix[i, j][:3] == WHITE:
                    self[i].append(1)
                elif pix[i, j][:3] == YELLOW:
                    self[i].append("spawn")
                elif pix[i, j][:3] == BLACK:
                    self[i].append("exit")
                # elif pix[i, j][:3] == RED:
                # 	self[i].append("enemy")
                else:
                    self[i].append(0)

    def render_map(self):
        for j in range(self.size):
            for i in range(self.size):
                if self[i][j] == 0:
                    pygame.draw.rect(sc, GREEN, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == 1:
                    pygame.draw.rect(sc, WHITE, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif isinstance(self[i][j], Hero):
                    pygame.draw.rect(sc, RED, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "exit":
                    pygame.draw.rect(sc, BLACK, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif self[i][j] == "spawn":
                    pygame.draw.rect(sc, YELLOW, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
                elif isinstance(self[i][j], Enemy):
                    pygame.draw.rect(sc, PINK, (i * PIXEL_SIZE, j * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

    # Обновить карту (заново отрегенить, расставить мобов итд)
    def update_map(self):
        print(f"[{get_time()}] Level {Map.created_maps} has been passed.")
        for i in range(len(self.objects)-1):
            self.objects[-1].die()
            self.objects.pop()
        self.objects[0].teleport(1, 1)
        [Enemy(map, f"Ork {i+1}", random.randint(2, 5)) for i in range(random.randint(5, 20))]
        Map.created_maps += 1
        print(f"[{get_time()}] Level {Map.created_maps} has been started.")
        self.objects[0].score += 10

    # <<< Настройки карты
    # Спавн объекта на определённых координатах
    def spawnObject(self, object, x=0, y=0):
        if isinstance(object, Hero):  # Герой всегда на спавн-точке
            spawnCords = self.find_pos("spawn")
            x, y = spawnCords[0], spawnCords[1]
            # x, y = 48, 48
        elif self[x][y] != 1:
            return print(f"[{get_time()}] {object} couldn't spawn on the wall (x:{x}, y:{y}).")
        self.objects.append(object)
        object.map = self
        self[x][y] = object
        object.pos.change(x, y)


map = Map("S")
hero = Hero(map)
[Enemy(map, f"Ork {i+1}", random.randint(2, 5)) for i in range(random.randint(10, 25))]
isGame = True
while isGame:
    pygame.time.delay(20)
    sc.fill(GREEN)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: isGame = False
    map.render_map()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        hero.move("left")
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        hero.move("right")
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        hero.move("up")
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        hero.move("down")
    if keys[pygame.K_SPACE]:
        hero.attack()
    score = font.render(f"Score: {hero.score} LVL: {map.get_current_level()}", True, WHITE)
    sc.blit(score, (10, display_height - 45))
    pygame.display.update()
