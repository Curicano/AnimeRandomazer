from os import environ#, _exit
from requests import Session
from random import choice

from telebot import TeleBot
# from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import apihelper
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

import keyboards

load_dotenv()
CHAT_ID = environ.get("chatId")
apihelper.proxy = {"http": environ.get("proxy")}
bot = TeleBot(token=environ.get("token"))

keyboards_layout = keyboards.ReplyKeyboardsLayout()


class S():
    def __init__(self) -> None:
        self.session = Session()

    def auth(self, chat_id):
        data = {
            "login_name": environ.get("login_name"),
            "login_password": environ.get("login_password"),
            "login": environ.get("login")
        }
        header = {
            "user-agent": environ.get("userAgent")
        }
        self.response = self.session.post(environ.get("url"), data, header)
        bot.send_message(chat_id, "Успешно",
                         reply_markup=keyboards_layout.menu())

    def update(self, chat_id):
        self.session.close()
        self.auth(chat_id)

    def getRandomAnime(self, chat_id):
        soup = bs(self.response.text, "lxml")
        tab4 = soup.find("div", id="tabz-4")
        animes = []
        for anime in tab4.find_all(
                "div", class_="popular-item d-flex ai-center popular-item__last newlist-item"):
            title = anime.find(
                "a", class_="popular-item__title ws-nowrap").text
            url = anime.find(
                "a", class_="popular-item__img img-fit-cover", href=True)
            a = {
                "title": title,
                "url": url["href"]
            }
            animes.append(a)
        r = choice(animes)
        bot.send_message(
            chat_id, f"Всего запланированных аниме: {len(animes)}")
        bot.send_message(
            chat_id, f"Рандомно выбранное:\n{r['title']} (<a href='{r['url']}'>ссылка</a>)", parse_mode="HTML")


session = S()


@bot.message_handler(commands=["start", "quit"])
def commandsHandler(message):
    chat_id = str(message.chat.id)
    text = message.text
    if chat_id == CHAT_ID:
        match text:
            case "/start":
                bot.send_message(
                    chat_id, f"Привет {message.from_user.first_name}!", reply_markup=keyboards_layout.mainMenu())
            # case "/quit":
            #     _exit(999)
    else:
        pass


@bot.message_handler()
def messageHandler(message):
    chat_id = str(message.chat.id)
    text = message.text
    if chat_id == CHAT_ID:
        match text:
            case "Авторизоваться":
                session.auth(chat_id)
            case "Random":
                session.getRandomAnime(chat_id)


bot.polling(none_stop=True, interval=5)
