import random

from src.events.Events import Events
from src.Settings import *
from src.entities.BaseEntity import BaseEntity
from src.ui.content.Statistic import Statistic


class Enemy(BaseEntity):

    def __init__(self, map, name, points, agr):
        super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0, color=BLUE)
        randPoint = map.get_random_point()
        map.spawn_object(self, randPoint[0], randPoint[1])
        self.points = points
        self.agr_radius = agr
        self._onVisited = False

    def isOnVisited(self):
        return self._onVisited

    # Передвижение >>>
    def move(self, way):
        x, y = self.pos.x + WAYS[way][0], self.pos.y + WAYS[way][1]
        self.face = way
        if self.map.isFree(x, y):
            self.map[self.pos.x][self.pos.y] = 2 if self._onVisited else 1
            self._onVisited = True if self.map.isVisited(x, y) else False
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
        damage = (self.damage + random.randint(0, 3) - player.armor) * (0 if random.randint(0, 100) <= 10 else 1)
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


