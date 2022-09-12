import random

from src.Settings import *
from src.events.Events import Events
from src.entities.BaseEntity import BaseEntity
from src.ui.content.Statistic import Statistic


class Hero(BaseEntity):  # Класс отвечающий за параметры главного героя

    def __init__(self, map):
        super().__init__(map, "Hero", hp=200.0, ar=3.0, dmg=5.0, color=RED)
        map.spawn_hero(self)
        self._heal_cooldown = 0

    # Передвижение >>>

    def move(self, way):
        x, y = self.pos.x + WAYS[way][0], self.pos.y + WAYS[way][1]
        self.face = way
        if self.map.isExit(x, y):
            Events.isPassedLevel = True
            self.map.update_map()
        elif self.map.isFree(x, y):
            self.map[self.pos.x][self.pos.y] = 2
            self.pos.change(x, y)
            self.map[self.pos.x][self.pos.y] = self
            Events.isHeroMoved = True
        # else: log(f"{self.name} ({self}) cannot go this way (x:{x}, y:{y}).")

    def heal(self, hp):
        if self.health >= self.MAXHEALTH:
            print(f"[{get_time()}] {self.name} already has max health ({self.health}/{self.MAXHEALTH}).")
        elif int(time.time()) < self._heal_cooldown + 5:
            print("Not now")
        else:
            print(f"[{get_time()}] {self.name}: +{hp} ({self.health}/{self.MAXHEALTH}).")
            self.health += hp
            Statistic.received_heal += hp
            self._heal_cooldown = int(time.time())
            Events.isHealthModified = True

    def teleport(self, x, y):
        self.map[self.pos.x][self.pos.y] = 1
        self.pos.change(x, y)
        self.map[self.pos.x][self.pos.y] = self

    # <<< Передвижение

    # Атака >>>

    def attack(self, enemy):
        if enemy is None:
            return

        damage = (self.damage + random.randint(0, 3) - enemy.armor) * (0 if random.randint(0, 100) <= 10 else 1)
        enemy.health -= damage
        enemy.color = get_mod_color(enemy.color, -damage)
        Statistic.caused_damage += damage

        if damage:
            print(f"[{get_time()}] {self.name} inflict {damage} damage to {enemy.name} (HP: {enemy.health}).")
        else:
            print(f"[{get_time()}] {self.name} missed (HP: {enemy.health}).")
        if enemy.health <= 0:
            enemy.die(self.name)
            Statistic.killed_mobs += 1
            Statistic.score += enemy.points
            Events.isScoredPoints = True
            print(f"[{get_time()}] {self.name} scored {enemy.points} point (Total score: {Statistic.score}).")

    # <<< Атака
