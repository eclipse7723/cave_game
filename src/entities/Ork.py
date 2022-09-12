import random
from src.entities.Enemy import Enemy


class Ork(Enemy):

    def __init__(self, map, points, agr):
        name = self.get_ork_name()
        super(Ork, self).__init__(map, name, points, agr)

    @staticmethod
    def get_ork_name():
        start = ["Slog", "Ra", "Ro", "Og", "Kegi", "Zor", "Un", "Yag", "Blak", "Mug", "Gud"]
        middle = "abcdeghklmnopqrst"
        end = ["ka", "rana", "all", "mash", "tan", "gu", "tag", "ge", "rim"]

        name = random.choice(start) + (random.choice(middle) if random.randint(0, 1) else "") + random.choice(end)
        return name


