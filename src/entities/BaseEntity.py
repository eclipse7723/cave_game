from abc import ABC, abstractmethod

from src.Position import Position
from src.Settings import *
from src.events.Events import Events


class BaseEntity(ABC):
    """ Главный класс живых объектов на карте """

    def __init__(self, map, name, hp, ar, dmg, color):
        self.pos = Position()
        self.map = map
        self._name = name
        self.health = hp
        self.armor = ar
        self.damage = dmg
        self._MAXHEALTH = 200.0
        self.color = color
        self.face = 'down'

    @property
    def name(self):
        return self._name

    @property
    def MAXHEALTH(self):
        return self._MAXHEALTH

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
            log(f"{obj} isn't on the current map (level: {self.map.created_maps}).")
        else:
            return ((self.pos.x - obj.pos.x) ** 2 + (self.pos.y - obj.pos.y) ** 2) ** (1 / 2)

    # <<< Передвижение
