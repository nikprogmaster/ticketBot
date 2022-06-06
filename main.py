import requests
from bs4 import BeautifulSoup as bs
import time
import telebot
from threading import Thread
import datetime
import os

BOT_TOKEN = ""
BOT_INTERVAL = 3
BOT_TIMEOUT = 30
bot = telebot.TeleBot(BOT_TOKEN)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

URLS = [
    "https://www.ticketswap.com/event/coldplay-music-of-spheres-world-tour-2022/8464a34f-4d58-47e8-9de3-2088a65f8e67",
    "https://www.ticketswap.com/coldplay-paris-17-julliet-2022",
    "https://www.ticketswap.com/coldplay-stade-de-france-19-julliet-2022",
    "https://www.ticketswap.com/event/coldplay-music-of-spheres-world-tour-2022/abad00c5-8f5b-42a9-ba61-d9323e9da375"
]

members = []


def start_listening_page():
    print("Started new listening thread")
    while True:
        not_zero_tickets_urls = URLS
        for u in URLS:
            try:
                resp = requests.get(u, headers=headers)
                soup = bs(resp.text, features="html.parser")
                value = soup.select('#__next > header > div.css-1z0k1xw.e1gtd2333 > div > div:nth-child(1) > span')[0].contents[0]
                if value != '0':
                    if u not in not_zero_tickets_urls:
                        send_everyone(u)
                        log("Notification sended")
                        not_zero_tickets_urls.append(u)
                else:
                    if u in not_zero_tickets_urls:
                        not_zero_tickets_urls.remove(u)
            except Exception as ex:
                log("Page requesting failed. Error:\n{}".format(ex.with_traceback()))

        time.sleep(5)


def log(message):
    f = open('res/logs.txt', 'a', encoding="utf-8")
    f.write(str(datetime.datetime.now()) + ": " + message + "\n")
    f.close()


def add_new_member(user_id):
    f = open('res/user_ids.txt', 'a', encoding="utf-8")
    f.write(str(user_id) + "\n")
    f.close()
    members.append(user_id)


def init_members():
    global members
    f = open('res/user_ids.txt', 'r', encoding="utf-8")
    for line in f:
        members.append(line)
    members = [line.rstrip() for line in members]
    f.close()


def bot_polling():
    global bot
    print("Starting bot polling now")
    while True:
        try:
            log("New bot instance started")
            init_members()
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
        except Exception as ex:
            log("Bot polling failed, restarting in {}sec. Error:\n{}".format(BOT_TIMEOUT, ex))
            bot.stop_polling()
            time.sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            log("Bot polling loop finished")
            break


@bot.message_handler(commands=['start'], content_types=['text'])
def send_welcome(message):
    global members
    if message.chat.type == "private":
        if message.from_user.id not in members:
            add_new_member(message.from_user.id)
            bot.send_message(message.from_user.id, "Ну здарова! Будем билетики тебе искать!")


def send_everyone(url: str):
    for m in members:
        try:
            bot.send_message(m, "Появился новый билет на странице " + url)
        except Exception as error:
            print(error)


polling_thread = Thread(target=bot_polling)
polling_thread.daemon = True
t1 = Thread(target=start_listening_page)
t1.daemon = True
polling_thread.start()
t1.start()

# Keep main program running while bot runs threaded
if __name__ == "__main__":
    while True:
        try:
            time.sleep(120)
        except KeyboardInterrupt:
            break

