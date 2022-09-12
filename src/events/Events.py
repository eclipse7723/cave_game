# todo: turn it to real Events class

class Events:
    """ Игровые события """

    isScoredPoints = False          # Получены ли баллы
    isPassedLevel = False           # Пройден ли уровень
    isHealthModified = False        # Изменилось ли HP героя
    isArmorModified = False         # Изменилось ли AR героя
    isSomeoneMoved = False          # Двинулся ли кто-то
    isHeroMoved = False             # Двинулся ли герой
    isSomeoneDied = False           # Умер ли кто-то
    isHeroDied = False              # Умер ли герой
    isGameLoosed = False            # Проиграна ли игра
    isStatisticShown = False        # Отображена ли статистика
    isPause = False                 # Открыто ли меню паузы
    isGameStart = False
    isSaveMenu = False
    isSettingsMenu = False
    isMenu = True

    @staticmethod
    def get_game_events():          # Ивенты игрового блока
        return Events.isSomeoneDied, Events.isSomeoneMoved, Events.isHeroMoved, Events.isHeroDied

    @staticmethod
    def get_playerbar_events():     # Ивенты статусбара игрока
        return Events.isHealthModified, Events.isArmorModified

    @staticmethod
    def get_gamebar_events():       # Ивенты статусбара игры
        return Events.isScoredPoints, Events.isPassedLevel
