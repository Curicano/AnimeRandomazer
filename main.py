from os import environ
from requests import Session, get
from random import choice

from telebot import TeleBot
from telebot.formatting import hlink
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from fake_useragent import FakeUserAgent

import keyboards

load_dotenv()
bot = TeleBot(environ.get("TOKEN"))

user_dict = {}


class UserSession:
    def __init__(self, login) -> None:
        self.login = login
        self.password = None
        self.session = Session()

    def auth(self) -> bool:
        data = {
            "login_name": self.login,
            "login_password": self.password,
            "login": "submit"
        }
        header = {
            "user-agent": FakeUserAgent.random
        }
        self.response = self.session.post(
            "https://animego.online", data, header)
        return True

    def unauth(self) -> bool:
        self.session.close()
        return True

    # def update(self):
    #     pass

    def getProfile(self) -> dict:
        self.response = self.session.get(
            "https://animego.online/user/" + self.login)
        soup = bs(self.response.text, "lxml")
        info = {}
        info["name"] = soup.find("h2", class_="usp__name").text
        info["group"] = soup.find("div", class_="usp__group").text
        activity = soup.find(
            "div", class_="usp__activity d-flex jc-flex-start stretch-free-width")
        info["friends"] = activity.find_all("div")[1].text
        info["comments"] = activity.find_all("div")[3].text
        usp_list = soup.find("ul", class_="usp__list d-flex jc-space-between")
        keys = ["register", "visit", "fullname", "gender"]
        for key, value in zip(keys, usp_list.find_all("li")):
            info[key] = value.text
        tabs = soup.find("ul", class_="tabs__caption")
        keys = ["see", "viewed", "abandoned", "planned",
                "postponed", "reviewing", "favorites"]
        for key, value in zip(keys, tabs.find_all("li")):
            info[key] = self.extractInt(value.text)
        return info

    def extractInt(self, text: str) -> int | None:
        length = len(text)

        integers = None
        i = 0

        while i < length:
            s_int = ''
            while i < length and '0' <= text[i] <= '9':
                s_int += text[i]
                i += 1
            i += 1
            if s_int != '':
                integers = int(s_int)
        return integers

    def getRandomAnime(self):
        self.response = self.session.get(
            "https://animego.online/user/" + self.login)
        soup = bs(self.response.text, "lxml")
        tab4 = soup.find("div", id="tabz-4")
        animes = []
        for anime in tab4.find_all(
                "div", class_="popular-item d-flex ai-center popular-item__last newlist-item"):
            a = {}
            title = anime.find(
                "a", class_="popular-item__title ws-nowrap").text
            a["title"] = title
            url = anime.find(
                "a", class_="popular-item__img img-fit-cover", href=True)
            a["url"] = url.get("href")
            rate = anime.find(
                "div", class_="th-meta-rate d-flex ai-center").text
            a["rate"] = rate.strip("\n \t")
            category = anime.find("small").text
            a["category"] = category
            animes.append(a)
        return choice(animes)


def process_login_step(message) -> None:
    try:
        chat_id = message.chat.id
        login = message.text
        user = UserSession(login)
        user_dict[chat_id] = user
        msg = bot.send_message(chat_id, "Ага, теперь введи пароль:")
        bot.register_next_step_handler(msg, process_password_step)
    except Exception as exc:
        bot.reply_to(message, 'oooops')


def process_password_step(message) -> None:
    try:
        chat_id = message.chat.id
        password = message.text
        user = user_dict[chat_id]
        user.password = password
        if user.auth():
            bot.send_message(chat_id, "Успешно!",
                             reply_markup=keyboards_layout.mainMenu())
        else:
            bot.send_message(chat_id, "Ошибка!")
    except Exception as exc:
        bot.reply_to(message, 'oooops')
        print(exc)


def getTopPopular() -> list:
    response = get("https://animego.online")
    soup = bs(response.text, "lxml")
    popular = soup.find("div", id="owl-popular")
    popular_animes = []
    for poster in popular.find_all("a", class_="poster-item grid-item", href=True):
        a = {}
        a["title"] = poster.text.strip("\n")
        a["url"] = "https://animego.online" + poster["href"]
        popular_animes.append(a)
    return popular_animes


def isAuth(chat_id: str | int) -> bool:
    if user_dict.get(chat_id):
        return True
    else:
        bot.send_message(
            chat_id, "Ты не авторизован!\nВведи /start или выбери из меню команд для перезапуска бота")
        return False


@bot.message_handler(["start", "test"])
def commandsHandler(message) -> None:
    chat_id = message.chat.id
    text = message.text
    match text:
        case "/start":
            bot.send_message(
                chat_id, f"Привет {message.from_user.first_name}!", reply_markup=keyboards_layout.authMenu())
        case "/test":
            pass


@bot.message_handler(func=lambda m: True)
def messageHandler(message) -> None:
    chat_id = message.chat.id
    text = message.text
    match text:
        case "Авторизоваться":
            msg = bot.send_message(chat_id, "Хорошо, напиши мне свой логин:")
            bot.register_next_step_handler(msg, process_login_step)
        case "Профиль":
            if isAuth(chat_id):
                info = user_dict.get(chat_id).getProfile()
                bot.send_message(chat_id, f"👤Профиль\n ├ Ваш юзернейм: {info['name']}\n ├ Группа: {info['group']}\n ├ Друзей: {info['friends']}\n ├ Комментариев: {info['comments']}\n ├ {info['visit']}\n ├ {info['register']}\n ├ {info['fullname']}\n └ {info['gender']}\n\nℹ️ Статистика\n ├ Смотрю: {info['see']}\n ├ Просмотрено: {info['viewed']}\n ├ Брошено: {info['abandoned']}\n ├ Запланировано: {info['planned']}\n ├ Отложено: {info['postponed']}\n ├ Пересматриваю: {info['reviewing']}\n └ В избранном: {info['favorites']}")
        case "Выйти":
            if isAuth(chat_id):
                user_dict.get(chat_id).unauth()
                del user_dict[chat_id]
                bot.send_message(chat_id, "Успешно!",
                                 reply_markup=keyboards_layout.authMenu())
        case "Случайное":
            if isAuth(chat_id):
                anime = user_dict.get(chat_id).getRandomAnime()
                bot.send_message(
                    chat_id, f"Случайно выбранное аниме:\n\n{anime['title']} ({hlink('ссылка', anime['url'])})\n🔖Категории: {anime['category']}\n⭐Рейтинг: {anime['rate']}", parse_mode="HTML")
        case "Топ популярных":
            animes = getTopPopular()
            text = "🔥 Популярные аниме\n\n"
            for anime in animes:
                text += f"{anime['title']} ({hlink('ссылка', anime['url'])})\n"
            bot.send_message(chat_id, text, parse_mode="HTML",
                             disable_web_page_preview=True)


if __name__ == '__main__':
    keyboards_layout = keyboards.ReplyKeyboardsLayout()
    bot.infinity_polling(skip_pending=True)
