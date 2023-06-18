from telebot.types import ReplyKeyboardMarkup, KeyboardButton


class ReplyKeyboardsLayout:
    def __init__(self) -> None:
        self._current_layout = 0

    def authMenu(self):
        markup = ReplyKeyboardMarkup(True)
        markup.add(KeyboardButton("Авторизоваться"),
                   KeyboardButton("Топ популярных"))
        return markup

    def mainMenu(self):
        markup = ReplyKeyboardMarkup(True)
        markup.add(KeyboardButton("Профиль"),
                   KeyboardButton("Случайное"),
                   KeyboardButton("Выйти"))
        return markup

    def currentLayout(self):
        return self._current_layout
