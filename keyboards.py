from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class ReplyKeyboardsLayout:
    def __init__(self) -> None:
        self._current_layout = 0

    def mainMenu(self):
        markup = ReplyKeyboardMarkup(True)
        markup.add(KeyboardButton("Авторизоваться"))
        return markup

    def menu(self):
        markup = ReplyKeyboardMarkup(True)
        markup.add(KeyboardButton("Random"))
        return markup

    def currentLayout(self):
        return self._current_layout
