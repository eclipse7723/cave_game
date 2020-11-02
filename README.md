# cave_game
### Авторы игры
* eclipse7723: [Telegram](https://t.me/eclipse7723)
* BorysBohdan: [Telegram](https://t.me/BohBorysenko)
* OnlyOneTry: [Telegram](https://t.me/OnlyOneTry)
### Управление
Передвижение осуществляется на **WASD** или **стрелочки**.  
Атака ближайшего противника на **пробел**.  
Подлечить героя на **E** (перезарядка 5 секунд).
## История версий
### 0.6 `Oct 31, 2020`
* Исправлен краш при нулевом количестве мобов на карте
* Враги теперь идут в сторону героя, чтобы атаковать его, если тот в их радиусе зрения
* Если герой умерает (HP <= 0), то игра заканчивается
* Увеличена производительность (нагрузка на ЦП спала с 6-8% до менее 1%)
* У всех юнитов появилось "лицо", показывающие направление движения
* Улучшена архитектура игры, небольшие доработки
### 0.5 `Oct 12, 2020`
* Обновлён интерфейс (в т.ч. выводится HP и AR)
* Добавлена генерация лабиринта после первого уровна
* Все юниты, кроме ГГ, двигаются в хаотичном порядке
* Информация для разработчика теперь выключается (пока что только в коде):  
`LOGGING: True` нужно заменить на `LOGGING: False`
* ГГ теперь может с вероятностью 10% промахнуться при ударе
* Небольшие фиксы и доработки
### 0.4 `Oct 12, 2020`
* Добавлен графический интерфейс
* Управление на стрелочки, атака (по области) на SPACE
* За убийство врагов и прохождение уровня начисляются очки
* Исправлена карта
### 0.3 `Oct 11, 2020`
* Карта отрисовуется по картинке
### 0.2 `Oct 11, 2020`
* Добавлен общий класс юнитов - Unit. Он может:  
Атаковать (и умирать), передвигаться по карте, лечиться
* Подклассы: Hero, Enemy
* Правки в классе Map (проверки, обобщён спавн)
* Можно играть через консоль
### 0.1 `Oct 10, 2020`
* start
