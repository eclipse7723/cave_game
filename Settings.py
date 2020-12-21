import time

VERSION = "0.7"
# Описание в README.md

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
PIXEL_SIZE = 10
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


# Воспомогательные функции >>>
def get_time(): return time.strftime('%x_%X')  # Время в консоли


def log(text):  # Логи разработчика
    if LOGGING: print(f"[{get_time()}] LOG: {text}")


def get_draw_position(x, y, size):  # Позиция блока на карте
    return x * size, y * size, size, size


def get_mod_color(color: tuple, mod: int):  # Изменение RGB цвета (x, y, z)
    c1, c2, c3 = (c + mod for c in color)
    c1 = 255 if c1 > 255 else 0 if c1 < 0 else color[0] + mod
    c2 = 255 if c2 > 255 else 0 if c2 < 0 else color[1] + mod
    c3 = 255 if c3 > 255 else 0 if c3 < 0 else color[2] + mod
    return c1, c2, c3
# <<< Воспомогательные функции
