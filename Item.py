from abc import ABC
import pygame


# Возможные ошибки >>>
class WrongItemCategory(Exception):
    def __init__(self, txt):
        self.txt = txt


class AmountMismatch(Exception):
    def __init__(self, txt):
        self.txt = txt
# <<< Возможные ошибки


class Item:
    categories = ("potion", "weapon", "armor")
    max_id = 0

    def __init__(self, category: str, amount: int, max_amount: int, title: str):
        if category.lower() not in Item.categories:
            raise WrongItemCategory(f"Category must be from {Item.categories}, but '{category}' was given.")
        if amount > max_amount:
            raise AmountMismatch(f"Max amount of '{title}' is {max_amount}, but {amount} was given.")
        if amount < 1:
            raise AmountMismatch(f"At least 1 '{title}' must exist (amount must be from 1 to {max_amount}).")
        self.__category = category.lower()
        self.amount = amount
        self.MAX_AMOUNT = max_amount
        self.title = title
        self.__id = Item.max_id
        Item.max_id += 1
        # self.sprite = sprite

    @property
    def id(self):
        return self.__id

    @property
    def category(self):
        return self.__category


class Potion(Item):
    def __init__(self, amount, title):
        super().__init__("potion", amount, 5, title)
        self.__health_points = 25
        self.sprite = pygame.image.load('sprites/Item/hp_potion.png').convert()


    # def use(self):
    #     owner.heal(self.__health_points)


class Weapon(Item):
    pass


class Armor(Item):
    pass


class Inventory:
    def __init__(self, max_items, money):
        self.slots = []
        self.MAX_ITEMS = max_items
        self.__money = money

    @property
    def money(self):
        return self.__money

    def open(self):
        return self.slots

    def close(self):
        pass

    def get_item_by_category(self, category):
        return (item for item in self.slots if item.category is category)

    def get_item_by_id(self, id):
        return (item for item in self.slots if item.id is id)

    def throw_item(self, item):
        # print(f"{owner} throw out {item.name}")
        self.slots.remove(item)
        del item


