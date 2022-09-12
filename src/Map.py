import random
import os
from PIL import Image

from pygame.draw import rect

from src.utils.get_engine import get_engine
from src.maze.maze import Maze
from src.Settings import *

from src.ui.content.Statistic import Statistic

from src.entities.BaseEntity import BaseEntity
from src.entities.Enemy import Enemy
from src.entities.Ork import Ork


class Map(list):
    created_maps = 0

    def __init__(self):
        super().__init__()
        self.size = 51
        self.objects = []
        self.hero = None
        self.create_map(FIRST_MAP_PATH)
        self.spawn = None

    # utils

    def isWall(self, x, y):
        return True if self[x][y] == 0 else False

    def isExit(self, x, y):
        return True if self[x][y] == "exit" else False

    def isFree(self, x, y):
        return True if self[x][y] == 1 or self[x][y] == 2 else False

    def isVisited(self, x, y):
        return True if self[x][y] == 2 else False

    def get_random_point(self):
        # todo: optimize
        random.seed(time.time())
        while True:
            x = random.randint(1, self.size - 1)
            y = random.randint(1, self.size - 1)
            if self.isFree(x, y):
                break
        return x, y

    def find_pos(self, obj):
        """ returns position of inputted object on the map
            if position doesn't found - returns (None, None) """
        for x in range(self.size):
            try:
                y = self[x].index(obj)
            except ValueError:
                continue
            else:
                return x, y
        return None, None

    def find_nearest_enemy(self):
        """ returns the nearest enemy to hero or None if no enemies near """

        hero = self.hero
        positions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1)]

        for pos in positions:
            x = hero.pos.x + pos[0]
            y = hero.pos.y + pos[1]
            obj = self[x][y]

            if isinstance(obj, Enemy):
                return obj

        return None

    # === render =======================================================================================================

    def render(self):
        player = self.objects[0]

        def check_point(unit, x, y):
            face = unit.face
            if (face == "up" or face == "down") and y-player.pos.y==0 and abs(x-player.pos.x)==1:
                return True
            elif (face == "right" or face == "left") and x-player.pos.x==0 and abs(y-player.pos.y)==1:
                return True
            if abs(y-player.pos.y) >= abs(x-player.pos.x):
                if face == "up" and abs(x-player.pos.x) <= 5 and 0 >= y-player.pos.y >= -5:
                    return True
                elif face == "down" and abs(x-player.pos.x) <= 5 and 0 <= y-player.pos.y <= 5:
                    return True
            if abs(y-player.pos.y) <= abs(x-player.pos.x):
                if face == "left" and abs(y-player.pos.y) <= 5 and -5 <= x-player.pos.x <= 0:
                    return True
                elif face == "right" and abs(y-player.pos.y) <= 5 and 0 <= x-player.pos.x <= 5:
                    return True
            else:
                return False

        engine = get_engine()
        engine.game.surf.fill(DARK_GREEN)
        for y, j in zip(range(player.pos.y - radius//2, player.pos.y + radius//2), range(radius)):
            for x, i in zip(range(player.pos.x - radius//2, player.pos.x + radius//2), range(radius)):
                if x < 0 or x > 50 or y < 0 or y > 50:
                    continue
                if check_point(player, x, y):
                    if self[x][y] == 1 or self[x][y] == 2:
                        rect(engine.game.surf, WHITE, get_draw_position(i, j, PIXEL))
                    elif self[x][y] == "exit":
                        rect(engine.game.surf, BLACK, get_draw_position(i, j, PIXEL))
                    elif self[x][y] == 0:
                        rect(engine.game.surf, GREEN, get_draw_position(i, j, PIXEL))
                    elif isinstance(self[x][y], BaseEntity):
                        obj = self[x][y]
                        rect(engine.game.surf, obj.color, get_draw_position(i, j, PIXEL))
                        rect(engine.game.surf, get_mod_color(obj.color, -50),
                                         ((i * PIXEL) + FACE[obj.face][0], (j * PIXEL) + FACE[obj.face][1],
                                          PIXEL - TAIL[obj.face][0], PIXEL - TAIL[obj.face][1]))
                else:
                    if self[x][y] == 2 or isinstance(self[x][y], Enemy) and self[x][y].isOnVisited():
                        rect(engine.game.surf, VISITED, get_draw_position(i, j, PIXEL))
                    else:
                        rect(engine.game.surf, DARK_GREEN_2, get_draw_position(i, j, PIXEL))

    # === map setup ====================================================================================================

    def create_map(self, path):
        """ Создание карты по картинке """
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

        if self.spawn is None:
            self.spawn = (1, 1)

        Map.created_maps += 1

    def gen_map(self):
        """ Генерация нового лабиринта """

        m = Maze()
        m.create(self.size, self.size, Maze.Create.KRUSKAL)
        m.save_maze()

        im = Image.open(MAZE_PATH)
        pix = im.load()
        for i in range(self.size):
            self.append([])
            for j in range(self.size):
                if pix[i, j][:3] == BLACK:
                    im.putpixel((i, j), GREEN)

        # add spawn point
        im.putpixel((1, 1), YELLOW)
        # add exit point
        im.putpixel((MAP_SIZE - 2, MAP_SIZE - 2), BLACK)

        im.save(MAZE_PATH)

    def update_map(self):
        """ Обновить карту (заново отрегенить, расставить мобов итд) """

        print(f"[{get_time()}] Level {Map.created_maps} has been passed.")
        self.kill_all("level passed")

        if os.path.exists(MAZE_PATH):
            os.remove(MAZE_PATH)
        self.gen_map()
        for i in range(len(self)):
            self.pop()
        self.create_map(MAZE_PATH)

        self.objects[0].teleport(self.spawn[0], self.spawn[1])

        self.generate_enemies()

        Statistic.passed_levels += 1
        log(f"Level {Map.created_maps} has been started.")
        Statistic.score += 10

    # === map interact =================================================================================================

    def generate_enemies(self):
        for i in range(random.randint(ENEMIES_RANGE[0], ENEMIES_RANGE[1])):
            Ork(self, random.randint(2, 5), 5.0)

    def _get_hero_spawn_position(self):
        spawnCords = self.find_pos("spawn")
        if spawnCords is None:
            randPoint = self.get_random_point()
            x, y = randPoint[0], randPoint[1]
        else:
            x, y = spawnCords[0], spawnCords[1]
        return x, y

    def spawn_hero(self, obj):
        """ Герой всегда на спавн-точке """
        x, y = self._get_hero_spawn_position()
        self.spawn_object(obj, x, y)
        self.hero = obj

    def spawn_object(self, obj, x=0, y=0):
        """ Спавн объекта на определённых координатах """
        self.objects.append(obj)
        obj.map = self
        self[x][y] = obj
        obj.pos.change(x, y)

    def kill_all(self, reason: str):
        for entity in self.objects[1:]:
            entity.die(reason)
