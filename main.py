from os import environ
from requests import Session
from random import choice

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.apihelper import proxy
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

load_dotenv()
CHAT_ID = environ.get("chatId")
proxy = {"http": environ.get("proxy")}
bot = TeleBot(token=environ.get("token"))


def randomAnime(chat_id):
    session = Session()
    data = {
        "login_name": environ.get("login_name"),
        "login_password": environ.get("login_password"),
        "login": environ.get("login")
    }
    header = {
        "user-agent": environ.get("userAgent")
    }
    response = session.post(environ.get("url"), data, headers=header)
    soup = bs(response.text, "lxml")
    tab4 = soup.find("div", id="tabz-4")
    animes = []
    for anime in tab4.find_all(
            "div", class_="popular-item d-flex ai-center popular-item__last newlist-item"):
        text = anime.find(
            "a", class_="popular-item__title ws-nowrap").text
        animes.append(text)
    bot.send_message(
        chat_id, f"Всего запланированных аниме: {animes.__len__()}")
    bot.send_message(
        chat_id, f"Рандомно выбранное: \"{choice(animes)}\"")


@bot.message_handler(commands=["start"])
def commandsHandler(message):
    chat_id = str(message.chat.id)
    text = message.text
    if chat_id == CHAT_ID:
        match text:
            case "/start":
                markup = ReplyKeyboardMarkup(True)
                markup.add(KeyboardButton("Рандом"))
                bot.send_message(
                    chat_id, f"Привет {message.from_user.first_name}!", reply_markup=markup)
    else:
        pass


@bot.message_handler()
def messageHandler(message):
    chat_id = str(message.chat.id)
    text = message.text
    if chat_id == CHAT_ID:
        match text:
            case "Рандом":
                randomAnime(chat_id)


bot.polling(none_stop=True, interval=5)
