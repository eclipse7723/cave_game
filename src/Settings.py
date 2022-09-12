import time

VERSION = "0.7.4"

# Константы
LOGGING = True               # Логи разработчика
DEBUG = False                # Дебаг режим
ENEMIES_RANGE = (50, 100)    # Количество мобов на карте (от, до)
FPS = 15                     # Количество кадров в секунду
WAYS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}    # Возможные пути движения

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
VISITED = (70, 100, 70)
RED = (255, 0, 0)
GREEN = (35, 180, 75)
DARK_GREEN = (30, 60, 30)
DARK_GREEN_2 = (60, 90, 60)
YELLOW = (255, 255, 0)
BLUE = (0, 130, 255)
PINK = (230, 50, 230)

# Размеры и кооринаты
PIXEL_SIZE = 13
FONT_SIZE = PIXEL_SIZE*4
STAT_FONT_SIZE = PIXEL_SIZE*2
MAP_SIZE = 51
STATUS_BAR = (MAP_SIZE * PIXEL_SIZE + PIXEL_SIZE, PIXEL_SIZE ** 2)
GAME_BAR = {"SIZE": STATUS_BAR, "POSITION": (0, 0)}
GAME = {"SIZE": (MAP_SIZE * PIXEL_SIZE, MAP_SIZE * PIXEL_SIZE), "POSITION": (0, GAME_BAR["SIZE"][1])}
PLAYER_BAR = {"SIZE": STATUS_BAR, "POSITION": (0, GAME["SIZE"][1] + GAME_BAR["SIZE"][1])}
DISPLAY_SIZE = (GAME["SIZE"][0], GAME["SIZE"][1] + (2 * (STATUS_BAR[1])))
radius = 20
PIXEL = 520 // radius
__FACE_NUM = PIXEL - int(radius/2**(radius//10-0.5) if radius == 10 else radius/2**(radius//10))
FACE = {"up": (0, 0), "down": (0, __FACE_NUM), "left": (0, 0), "right": (__FACE_NUM, 0)}      # Лицо
TAIL = {"up": (0, __FACE_NUM), "down": (0, __FACE_NUM), "left": (__FACE_NUM, 0), "right": (__FACE_NUM, 0)}
SIZE_PAUSE_BUTTON = [(164, 61), (269, 61), (125, 61)]
LUC_PAUSE_BUTTON = [(236, 374), (186, 474), (256, 574)]
SAVE_MENU_BUTTON = [(571, 61*2), (571, 61*2), (571, 61*2)]
LUC_SAVE_BUTTON = [(46, 374), (46, 524), (46, 674)]
SIZE_MENU_BUTTON = [(144, 61), (160, 61), (269, 61), (125, 61)]
LUC_MENU_BUTTON = [(236, 374), (256, 474), (186, 574), (256, 674)]

# path
RESOURCES_PATH = "src/resources"
FONT_PATH = RESOURCES_PATH + "/font.ttf"
MAZE_PATH = RESOURCES_PATH + "/maze.png"
FIRST_MAP_PATH = RESOURCES_PATH + "/map.png"


def get_time():
    return time.strftime('%x_%X')


def log(text):
    if LOGGING is False:
        return
    print(f"[{get_time()}] LOG: {text}")


def get_draw_position(x, y, size):
    """ Позиция блока на карте """
    pos = x * size, y * size, size, size
    return pos


def get_mod_color(color: tuple, mod: int):
    """ Изменение RGB цвета в промежутке от 0 до 255
        :param color: (r, g, b) tuple of color
        :param mod: int that would be added to color
    """
    r, g, b = (c + mod for c in color)

    r = 255 if r > 255 else 0 if r < 0 else color[0] + mod
    g = 255 if g > 255 else 0 if g < 0 else color[1] + mod
    b = 255 if b > 255 else 0 if b < 0 else color[2] + mod

    return r, g, b
