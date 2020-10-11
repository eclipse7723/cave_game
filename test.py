import time
import random

from PIL import Image
import numpy as np

def get_time():	return time.strftime('%x_%X')


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 177, 76)
YELLOW = (255, 255, 0)

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
	def attack(self, unit):
		if not isinstance(unit, Unit):
			print(f"[{get_time()}] Error! {type(unit)} is not a {Unit}.")
		elif self.get_distance(unit) >= 2:
			print(f"[{get_time()}] {unit.name} too far (!TEMPORARY! {self.get_distance(unit)} steps from you).")
		else:
			damage = self._damage + random.randint(0, 3) - unit._armor
			unit.health -= damage
			print(f"[{get_time()}] {self.name} inflict {damage} damage to {unit} (HP: {unit.health}).")
			if unit.health <= 0: unit.die(self)

	def die(self, reason):
		print(f"[{get_time()}] {self.name} died - reason: {reason}.")
		cords = self.pos.get_position()
		map[cords[1]][cords[0]] = 1
		del self

	def heal(self, hp):
		if self._health >= self.MAX_HEALTH:
			print(f"[{get_time()}] {self.name} already has max health ({self._health}/{self.MAX_HEALTH}).")
		else:
			print(f"[{get_time()}] {self.name}: +{hp} ({self._health}/{self.MAX_HEALTH}).")
			self._health += hp
	# <<< Действия

	# Передвижение >>>
	def move(self, way):
		way = way.lower()
		ways = {"up": [0, -1], "down": [0, 1], "left": [-1, 0], "right": [1, 0]}
		if way not in ways.keys():
			print(f"[{get_time()}] way '{way}' is not defined.")
		else:
			x, y = self.pos.x+ways[way][0], self.pos.y+ways[way][1]
			if map.isWall(x, y):
				print(f"[{get_time()}] {self} couldn't go on the wall (x:{x}, y:{y}).")
			elif map.isExit(x, y):
				map.update_map()
			elif map.isFree(x, y):
				map[self.pos.y][self.pos.x] = 1
				self.pos.change(x, y)
				map[self.pos.y][self.pos.x] = self
				print(f"[{get_time()}] {self} successfully went {way}.")
				map.print_map()
			else:
				print(f"[{get_time()}] {self} cannot go this way (x:{x}, y:{y}).")

	def get_distance(self, object):
		if object not in map.objects:
			print(f"[{get_time()}] {object} isn't on the current map (level: {map.get_current_level()}.")
		else: 
			return ((self.pos.x - object.pos.x)**2 + (self.pos.y - object.pos.y)**2)**(1/2)
	# <<< Передвижение


class Hero(Unit):
	def __init__(self, map):
		super().__init__(map, "HERO", hp=200.0, ar=0.0, dmg=5.0)
		map.spawnObject(self)

	def say(self, text):
		print(f"[{get_time()}] {self} said: '{text}'")


class Enemy(Unit):
	def __init__(self, map, name):
		super().__init__(map, name, hp=100.0, ar=3.0, dmg=10.0)
		randPoint = map.get_randomPoint()
		map.spawnObject(self, randPoint[0], randPoint[1])


class Map(list):
	size_list = {"S": 17, "M": 27, "L": 52}
	created_maps = 0

	def __init__(self, size):
		self.size = Map.size_list[size]
		self.objects = []
		self.create_map()

	# Воспомогательные функции >>>
	def get_current_level(self):
		return created_maps

	def isWall(self, x, y):
		if self[y][x] == 0: return True
		return False

	def isExit(self, x, y):
		if self[y][x] == "exit": return True
		return False

	def isFree(self, x, y):
		if self[y][x] == 1: return True
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
		# for i in range(self.size):
		# 	self.append([])
		# 	for j in range(self.size):
		# 		if (i == 0 or i == self.size-1) or (j == 0 or j == self.size-1): 
		# 			self[i].append(0)
		# 		elif i == 1 and j == self.size-2:
		# 			self[i].append("exit")
		# 		elif i == self.size-2 and j == 1:
		# 			self[i].append("spawn")
		# 		else:
		# 			self[i].append(1)
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
				else: self[i].append(0)
		Map.created_maps += 1
		print(f"[{get_time()}] Level {Map.created_maps} has been created.")

	def print_map(self):
		for i in range(self.size): print(self[i])

		# Обновить карту (заново отрегенить, расставить мобов итд)
	def update_map(self):
		print(f"[{get_time()}] Level {Map.created_maps} has been passed.")
		pass
	# <<< Настройки карты

		# Спавн объекта на определённых координатах
	def get_randomPoint(self):
		random.seed(time.time())
		while True:
			x = random.randint(1, self.size-1)
			y = random.randint(1, self.size-1)
			if self.isFree(x, y): break
		return [x, y]

	def spawnObject(self, object, x=0, y=0):
		if isinstance(object, Hero): 	# Герой всегда на спавн-точке
			spawnCords = self.find_pos("spawn")
			x, y = spawnCords[0], spawnCords[1]
		elif self[y][x] == 0:
			return print(f"[{get_time()}] {object} couldn't spawn on the wall (x:{x}, y:{y}).")
		self.objects.append(object)
		object.map = self
		self[y][x] = object
		object.pos.change(x, y)
		print(f"[{get_time()}] {object} has been spawned at x:{x}, y:{y}.")


if __name__ == '__main__':
	map = Map("S")
	hero = Hero(map)
	enemy1 = Enemy(map, "Ork")
	map.print_map()
	
	isGame = True
	while isGame:
		moving = {"w": "up", "s": "down", "a": "left", "d": "right"}
		command = input("Type command: ").lower()
		if command == "stop": isGame = False
		elif command in moving.keys(): hero.move(moving[command])
		elif command[:6] == "attack": 
			if command[7:] == "ork": hero.attack(enemy1)
			else: print("<Temporary Error> Do a search by object name.")
		elif command[:3] == "say": hero.say(command[4:])
		else: print("<Error> Command not found.")

