import pygame
import numpy as np
import time
import random

from PIL import Image


def get_time():
    return time.strftime('%x_%X')


pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
YELLOW = (255, 255, 0)
BLUE = (29, 32, 76)
PINK = (230, 50, 230)

display_width = 510
display_height = 510
x = 475
y = 475
player_width = 10
player_height = 10
wall_width = 10
wall_height = 10
speed = 1

sc = pygame.display.set_mode((display_width, display_height))

class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def change(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return [self.x, self.y]


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

    # <<< Характеристики

    # Действия >>>
    def attack(self):

        positions = [[0,1],[1,0],[1,1],[0,-1],[-1,0],[-1,-1],[-1,1],[1,-1]]
        for pos in positions:
            unit = map[self.pos.x+pos[0]][self.pos.y+pos[1]]
            if isinstance(unit, Unit):
                damage = self._damage + random.randint(0, 3) - unit._armor
                unit.health -= damage
                print(f"[{get_time()}] {self.name} inflict {damage} damage to {unit} (HP: {unit.health}).")
                if unit.health <= 0: unit.die(self)

            # else:
            #     damage = self._damage + random.randint(0, 3) - unit._armor
            #     unit.health -= damage
            #     print(f"[{get_time()}] {self.name} inflict {damage} damage to {unit} (HP: {unit.health}).")
            #     if unit.health <= 0: unit.die(self)

    def die(self, reason):
        print(f"[{get_time()}] {self.name} died - reason: {reason}.")
        cords = self.pos.get_position()
        map[cords[0]][cords[1]] = 1
        del self

    def heal(self, hp):
        if self._health >= self.MAX_HEALTH:
            print(f"[{get_time()}] {self.name} already has max health ({self._health}/{self.MAX_HEALTH}).")
        else:
            print(f"[{get_time()}] {self.name}: +{hp} ({self._health}/{self.MAX_HEALTH}).")
            self._health += hp

    # <<< Действия

    # Передвижение >>>
    def move(self, way, sc):
        ways = {"up": [0, -1], "down": [0, 1], "left": [-1, 0], "right": [1, 0]}
        x, y = self.pos.x + ways[way][0], self.pos.y + ways[way][1]
        if map.isWall(x, y):
            print(f"[{get_time()}] {self} couldn't go on the wall (x:{x}, y:{y}).")
        elif map.isExit(x, y):
            map.update_map()
        elif map.isFree(x, y):
            map[self.pos.x][self.pos.y] = 1
            self.pos.change(x, y)
            map[self.pos.x][self.pos.y] = self
            print(f"[{get_time()}] {self} successfully went {way}.")
            map.print_map(sc)
        else:
            print(f"[{get_time()}] {self} cannot go this way (x:{x}, y:{y}).")

    def get_distance(self, object):
        if object not in map.objects:
            print(f"[{get_time()}] {object} isn't on the current map (level: {map.get_current_level()}.")
        else:
            return ((self.pos.x - object.pos.x) ** 2 + (self.pos.y - object.pos.y) ** 2) ** (1 / 2)
# <<< Передвижение


class Hero(Unit):
    def __init__(self, map, sc):
        super().__init__(map, "Hero", hp=200.0, ar=0.0, dmg=5.0)
        map.spawnObject(self)


    def say(self, text):
        print(f"[{get_time()}] {self} said: '{text}'")


class Enemy(Unit):
    def __init__(self, map, name):
        super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0)
        randPoint = map.get_randomPoint()
        map.spawnObject(self, randPoint[0], randPoint[1])


class Map(list):
    size_list = {"S": 51, "M": 27, "L": 52}
    created_maps = 0

    def __init__(self, size):
        self.size = Map.size_list[size]
        self.objects = []
        self.create_map()

    # Воспомогательные функции >>>
    def get_current_level(self):
        return created_maps

    def isWall(self, x, y):
        if self[x][y] == 0: return True
        return False

    def isExit(self, x, y):
        if self[x][y] == "exit": return True
        return False

    def isFree(self, x, y):
        if self[x][y] == 1: return True
        return False

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
    # Создание пустой карты
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
        Map.created_maps += 1



    def print_map(self, sc):
        for j in range(self.size):
            for i in range(self.size):
                if self[i][j] == 0:
                    pygame.draw.rect(sc, GREEN, (i * wall_width, j * wall_height, wall_width, wall_height))
                elif self[i][j] == 1:
                    pygame.draw.rect(sc, WHITE, (i * wall_width, j * wall_height, wall_width, wall_height))
                elif isinstance(self[i][j], Hero):
                    pygame.draw.rect(sc, RED, (i * wall_width, j * wall_height, wall_width, wall_height))
                elif self[i][j] == "exit":
                    pygame.draw.rect(sc, BLACK, (i * wall_width, j * wall_height, wall_width, wall_height))
                elif self[i][j] == "spawn":
                    pygame.draw.rect(sc, YELLOW, (i * wall_width, j * wall_height, wall_width, wall_height))
                elif isinstance(self[i][j], Enemy):
                    pygame.draw.rect(sc, PINK, (i * wall_width, j * wall_height, wall_width, wall_height))


    # Обновить карту (заново отрегенить, расставить мобов итд)
    def update_map(self):
        print(f"[{get_time()}] Level {Map.created_maps} has been passed.")
        pass

    # <<< Настройки карты

    # Спавн объекта на определённых координатах
    def get_randomPoint(self):
        random.seed(time.time())
        while True:
            x = random.randint(1, self.size - 1)
            y = random.randint(1, self.size - 1)
            if self.isFree(x, y): break
        return [x, y]

    def spawnObject(self, object, x=0, y=0):
        if isinstance(object, Hero):  # Герой всегда на спавн-точке
            spawnCords = self.find_pos("spawn")
            x, y = spawnCords[0]+1, spawnCords[1]+1
            self[x][y]="*"
        elif self[x][y] == 0:
            return print(f"[{get_time()}] {object} couldn't spawn on the wall (x:{x}, y:{y}).")
        self.objects.append(object)
        object.map = self
        self[x][y] = object
        object.pos.change(x, y)




pygame.display.set_caption("TestGame")
isGame = True
map = Map("S")
hero = Hero(map, sc)
[Enemy(map, f"Ork {i}") for i in range(random.randint(1,5))]
while isGame:
    pygame.time.delay(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isGame = False
    sc.fill((BLUE))
    map.print_map(sc)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        hero.move("left",sc)
    if keys[pygame.K_RIGHT]:
        hero.move("right",sc)
    if keys[pygame.K_UP]:
        hero.move("up",sc)
    if keys[pygame.K_DOWN]:
        hero.move("down",sc)
    if keys[pygame.K_SPACE] :
        hero.attack()

# command = input("Type command: ").lower()
# if command == "stop": isGame = False
# elif command in moving.keys(): hero.move(moving[command])
# elif command[:6] == "attack":
# 	if command[7:] == "ork": hero.attack(enemy1)
# 	else: print("<Temporary Error> Do a search by object name.")
# elif command[:3] == "say": hero.say(command[4:])
# else: print("<Error> Command not found.")
    pygame.display.update()
