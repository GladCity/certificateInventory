import telebot
from DataBase import DataBase
import secrets
import datetime
import re
import os


def parse_date_and_time(dt: str):
    """Format: YYYY.MM.DD HH:MM"""
    print(dt)
    return datetime.datetime(int(dt[:4]), int(dt[5:7]), int(dt[8:10]), int(dt[11:13]), int(dt[14:]))


def export_to_date_and_time(dt: datetime.datetime):
    return "{}.{}.{} {}:{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)

db = DataBase()
# class telegram():
#     def __init__(self, token=None):
#         if token == None:

ip_types = ["file", "mask", "range"]

config = {"next_scan": datetime.datetime(1970, 1, 1, 0, 0, 0, 0),
          "scandelta": datetime.timedelta(1.5),
          "reportdelta": datetime.timedelta(0.2),
          "ip": ("range", "192.168.0.1-192.168.0.1")}
explainconfig = {"next_scan": "Время и дата ближайшего сканирования",
                 "scandelta": "Интервал между сканированиями (минимум - 1 час)",
                 "reportdelta": "Интервал между отправкой отчетов во время сканирования (минимум - 5 минут)",
                 "ip": "IP-адрес, может быть записан в трёх видах: в качестве маски (192.168.0.1/24),"
                       "в качестве диапазона (192.168.0.1-192.169.0.1), как файл с ip-адресами."}
bot = telebot.TeleBot('5894305427:AAE03pvAh-6u9p3nftQzYHlyx5E2Ra9GekM')

# Main keyboard
abilities = telebot.types.InlineKeyboardMarkup()
key1 = telebot.types.InlineKeyboardButton(text='Мои настройки', callback_data='config')
abilities.add(key1)
key2 = telebot.types.InlineKeyboardButton(text='Начать сканирование', callback_data='scan')
abilities.add(key2)
key3 = telebot.types.InlineKeyboardButton(text='Получить файл ip-адресов', callback_data='get')
abilities.add(key3)
key4 = telebot.types.InlineKeyboardButton(text='Отправить файл ip-адресов', callback_data='add')
abilities.add(key4)
key5 = telebot.types.InlineKeyboardButton(text='Удалить текущий список ip', callback_data='del')
abilities.add(key5)
key6 = telebot.types.InlineKeyboardButton(text='Добавить нового пользователя', callback_data='new')
abilities.add(key6)
key7 = telebot.types.InlineKeyboardButton(text='Выключить бота', callback_data='exit')
abilities.add(key7)

# key_no = telebot.types.InlineKeyboardButton(text='Хочу суши', callback_data='sushi')
# keyboard.add(key_no)
token = "12345678"

# 2022.01.01 00:00
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if str(message.chat.id) not in db.get_user_list():
        if message.text.strip() != token:
            bot.send_message(message.from_user.id, "Пожалуйста, пришли мне токен для авторизации!")
        else:
            bot.send_message(message.from_user.id, "Вы успешно авторизировались!")
            db.insert_user(str(message.from_user.id))
    else:
        text = [x.strip() for x in message.text.split(" ", 1)]
        if text[0].lower() in config and \
                re.fullmatch(r"((\d+ (час\S{,2}|минут\S{,2}|дня|дней|день))|"
                             r"\d\d\d\d\.\d\d\.\d\d \d\d:\d\d)", text[1]):
            if text[0] == "next_scan":
                print("Введен аргумент next_scan")
                config[text[0]] = parse_date_and_time(text[1])
                bot.reply_to(message, "Параметр next_scan изменен!")
            else:
                print("Введен аргумент " + text[1])
                bot.reply_to(message, "Параметр {} изменен!".format(text[1]))
                config[text[1]] = datetime.timedelta(seconds=int(text[1].split(" ", 1)[0]) * \
                                                             (60 if "мин" in text[1] else (
                    3600 if "час" in text[1] else 86400)))
        else:
            try:
                isdoc = message.document
            except:
                isdoc = None
            if isdoc:
                try:
                    file_info = bot.get_file(message.document.file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    with open("userfile", 'wb') as new_file:
                        new_file.write(downloaded_file)
                    bot.reply_to(message, "Поймал!")
                except Exception as e:
                    bot.reply_to(message, str(e))
            else:
                bot.send_message(message.from_user.id, "Смотри, что я умею: ", reply_markup=abilities)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "config":
        bot.send_message(call.message.chat.id, 'Держи свои настройки! Чтобы изменить любую из них,'
                                               'просто напиши этот параметр, а затем через пробел'
                                               ' значение, которое хочешь ему присвоить!')
        s = ""
        s += "next_scan = " + export_to_date_and_time(config["next_scan"]) + " - " + explainconfig["next_scan"] + "\n"
        s += "scandelta = " + str(config["scandelta"]).replace("day", "день").replace("days", "дней") + " - " + \
             explainconfig["scandelta"] + "\n"
        s += "reportdelta = " + str(config["reportdelta"]).replace("day", "день").replace("days", "дней") + " - " + \
             explainconfig["reportdelta"] + "\n"
        bot.send_message(call.message.chat.id, s)
        bot.send_message(call.message.chat.id, "Интервал указывается в следующем виде: N [дней | часов | минут]. Дата "
                                               "указывается в форме ГГГГ.ММ.ДД ЧЧ:ММ. IP-адреса, либо маски/диапазоны, "
                                               "указываются по одному в строке сообщения, либо файлом после нажатия "
                                               "кнопки \"Отправить файл\"")
    elif call.data == "scan":
        bot.send_message(call.message.chat.id, 'Сканирование началось!')
    elif call.data == "get":
        bot.send_message(call.message.chat.id, 'Лови файл!')
        bot.send_document(call.message.chat.id, "iplist.csv")
    elif call.data == "add":
        bot.send_message(call.message.chat.id, 'Кидай мне файл!')
    elif call.data == "del":
        f = open("iplist.csv", "w")
        f.write("")
        f.close()
        bot.send_message(call.message.chat.id, 'Список ip-адресов удален!')
    elif call.data == "new":
        bot.send_message(call.message.chat.id, 'Перешли мне сообщение от этого пользователя, либо скажи мне его ID!')

    elif call.data == "exit":
        bot.send_message(call.message.chat.id, 'Отвязываю тебя от сервера. Пока!')

@bot.message_handler(content_types=['text'])
def get_new_user(message):

bot.polling(none_stop=True, interval=0)
