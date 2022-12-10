import telebot
from DataBase import DataBase
import secrets
import datetime
import re
import threading
from Scanner import Scanner


class telegram():
    def __init__(self, telegram_token: str = '5894305427:AAE03pvAh-6u9p3nftQzYHlyx5E2Ra9GekM',
                 db: DataBase = DataBase(),
                 scan: Scanner = Scanner()
                 ):
        self.scan = scan
        self.bot = telebot.TeleBot(telegram_token)
        self.conf_bools = ["ignore1y", "ignorekl", "ignorenvc", "ignoreexc", "ignorealgo"]
        self.tokens = dict()
        self.db = db
        self.config = telegram.savol_json_to_my(db.get_conf())
        # self.config = {"next_scan": next_scan,
        #                "scandelta": scandelta,
        #                "port": port,
        #                "ignore1y": ignore1y,
        #                "ignorekl": ignorekl,
        #                "ignorenvc": ignorenvc,
        #                "ignoreexc": ignoreexc,
        #                "ignorealgo": ignorealgo,
        #                "checkcenter": checkcenter,
        #                "checkdate": checkdate,
        #                #"reportdelta": reportdelta,
        #                "ip": ip
        #                #"is_alive": is_alive
        #                }
        self.explainconfig = {"next_scan": "Время и дата ближайшего сканирования",
                              "scandelta": "Интервал между сканированиями (минимум - 1 час)",
                              "reportdelta": "Интервал между отправкой отчетов во время сканирования (минимум - 5 минут)",
                              "ip": "IP-адрес, может быть записан в трёх видах: в качестве маски (192.168.0.1/24),"
                                    "в качестве диапазона (192.168.0.1-192.169.0.1), как файл с ip-адресами.",
                              "port": "Диапазон проверяемых портов",
                              "ignore1y": "Не выделять сертификаты, предоставленные больше, чем на год",
                              "ignorekl": "Не выделять сертификаты с ключом которкой длины",
                              "ignorenvc": "Не выделять самоподписанные сертификаты",
                              "ignoreexc": "Не выделять просроченные сертификаты",
                              "ignorealgo": "Не выделять сертификаты с просроченной алгоритмизацией",
                              "checkcenter": "Сертификационный центр",
                              "checkdate": "Считать сертификаты действительными, срок действия которых истекает позже заданной даты",
                              "is_alive": "Включена ли рассылка или нет"

                              }
        self.one_hour = datetime.timedelta(hours=1)
        self.five_minutes = datetime.timedelta(minutes=5)
        # self.db = DataBase()
        self.logger = telebot.logger
        telebot.logger.setLevel(telebot.logging.DEBUG)
        # Keyboards
        if True:
            # First keyboard
            self.abilities = telebot.types.InlineKeyboardMarkup()
            key0 = telebot.types.InlineKeyboardButton(text='Мои настройки', callback_data='config')
            self.abilities.add(key0)
            key1 = telebot.types.InlineKeyboardButton(text='Краткая справка', callback_data='help')
            self.abilities.add(key1)
            key2 = telebot.types.InlineKeyboardButton(text='Начать сканирование', callback_data='scan')
            self.abilities.add(key2)
            key3 = telebot.types.InlineKeyboardButton(text='Получить файл ip-адресов', callback_data='get')
            self.abilities.add(key3)
            key4 = telebot.types.InlineKeyboardButton(text='Отправить файл ip-адресов', callback_data='add')
            self.abilities.add(key4)
            key5 = telebot.types.InlineKeyboardButton(text='Удалить текущий список ip', callback_data='del')
            self.abilities.add(key5)
            key6 = telebot.types.InlineKeyboardButton(text='Добавить нового пользователя', callback_data='new')
            self.abilities.add(key6)
            # key7 = telebot.types.InlineKeyboardButton(text='Выключить рассылку', callback_data='stop')
            # self.abilities.add(key7)

            # Second keyboard
            self.abilities_poweron = telebot.types.InlineKeyboardMarkup(row_width=3)
            self.abilities_poweron.add(key0)
            self.abilities_poweron.add(key1)
            self.abilities_poweron.add(key2, row_width=3)
            self.abilities_poweron.add(key3, row_width=3)
            self.abilities_poweron.add(key4, row_width=3)
            self.abilities_poweron.add(key5, row_width=3)
            self.abilities_poweron.add(key6, row_width=3)
            # key7_2 = telebot.types.InlineKeyboardButton(text='Включить рассылку', callback_data='start')
            # self.abilities_poweron.add(key7_2, row_width=3)

            # Main menu keyboard
            self.markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            itembtn1 = telebot.types.KeyboardButton('Главное меню', )
            self.markup.add(itembtn1)

            # Config keyboard
            self.markup_config = telebot.types.InlineKeyboardMarkup(row_width=3)
            key8 = telebot.types.InlineKeyboardButton(text='ignore1y', callback_data='ignore1y')
            key9 = telebot.types.InlineKeyboardButton(text='ignorekl', callback_data='ignorekl')
            key10 = telebot.types.InlineKeyboardButton(text='ignorenvc', callback_data='ignorenvc')
            self.markup_config.add(key8, key9, key10, row_width=3)
            key11 = telebot.types.InlineKeyboardButton(text='ignoreexc', callback_data='ignoreexc')
            key12 = telebot.types.InlineKeyboardButton(text='ignorealgo', callback_data='ignorealgo')
            self.markup_config.add(key11, key12, row_width=2)

    @staticmethod
    def savol_json_to_my(d):
        conf = d
        if conf["next_scan"] != "":
            conf["next_scan"] = datetime.datetime(int(conf["next_scan"][0:4]), int(conf["next_scan"][4:6]),
            int(conf["next_scan"][6:8]), int(conf["next_scan"][8:10]), int(conf["next_scan"][10:]))
        if conf["checkdate"] != "":
            conf["checkdate"] = datetime.datetime(int(conf["checkdate"][0:4]), int(conf["checkdate"][4:6]),
            int(conf["checkdate"][6:8]), int(conf["checkdate"][8:10]), int(conf["checkdate"][10:]))
        conf["scandelta"] = datetime.timedelta(seconds=conf["scandelta"]*3600)
        return conf

    @staticmethod
    def add_char(c):
        return "0" + c if len(c) == 1 else c
    @staticmethod
    def my_json_to_savol(conf):

        conf["next_scan"] = telegram.add_char(str(conf["next_scan"].year)) + telegram.add_char(str(conf["next_scan"].month)) + \
        telegram.add_char(str(conf["next_scan"].day)) + telegram.add_char(str(conf["next_scan"].hour)) + telegram.add_char(str(conf["next_scan"].minute))
        if conf["checkdate"] != "":
            conf["checkdate"] = telegram.add_char(str(conf["checkdate"].year)) + telegram.add_char(str(conf["checkdate"].month)) + \
            telegram.add_char(str(conf["checkdate"].day)) + telegram.add_char(str(conf["checkdate"].hour)) + telegram.add_char(str(conf["checkdate"].minute))
        conf["scandelta"] = conf["scandelta"].seconds % 3600
        return conf




    @staticmethod
    def parse_date_and_time(dt: str):
        """Format: YYYY.MM.DD HH:MM"""
        return datetime.datetime(int(dt[:4]), int(dt[5:7]), int(dt[8:10]), int(dt[11:13]), int(dt[14:]))

    @staticmethod
    def export_to_date_and_time(dt: datetime.datetime):
        if type(dt) == type("!"):
            dt=datetime.datetime(int(dt[0:4]), int(dt[4:6]),
                              int(dt[6:8]), int(dt[8:10]), int(dt[10:]))
        return "{}.{}.{} {}:{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)

    def broadcast_string(self, s: str):
        for user in self.db.get_user_list():
            self.bot.send_message(int(user), s, reply_markup=self.markup)

    def broadcast_file(self, filename: str):
        for user in self.db.get_user_list():
            self.bot.send_message(int(user), 'Лови файл!')
            with open(filename, "rb") as misc:
                f = misc.read()
            self.bot.send_document(int(user), f)

    def bot_start(self):
        @self.bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            # Authentication
            if str(message.from_user.id) not in self.db.get_user_list():
                token = secrets.token_hex(12)
                print("Token for authentication in Telegram (live during one hour): " + token)
                cur_date_and_hour = datetime.datetime.now()
                cur_date_and_hour.hours = cur_date_and_hour.hours + 1
                self.tokens[token] = cur_date_and_hour
                if message.text.strip().lower() not in self.tokens:
                    self.bot.send_message(message.from_user.id, "Пожалуйста, пришли мне токен для авторизации!")
                elif self.tokens[message.text.strip().lower()] < datetime.datetime.now():
                    self.bot.send_message(message.from_user.id, "Время жизни этого токена истекло (1 час)! "
                                                                "Он будет удален.")
                    self.tokens.pop(message.text.strip().lower())
                else:
                    self.tokens.pop(message.text.strip().lower())
                    self.bot.send_message(message.from_user.id, "Вы успешно авторизировались! Токен удален.",
                                          reply_markup=self.markup)
                    self.db.insert_user(str(message.from_user.id))
            else:
                text = [x.strip() for x in message.text.split(" ", 1)]
                text[0] = text[0].lower()
                # next_scan, scandelta, reportdelta

                # Constants
                if text[0] in self.conf_bools:
                    self.config[text[0]] = not self.config[text[0]]
                    self.db.set_file_conf(telegram.my_json_to_savol(self.config.copy()))
                    self.bot.send_message(message.chat.id, 'Параметр {} успешно изменен!'.format(text[0]))

                elif text[0].lower() in self.config and re.fullmatch(r"((\d+ (час\S{,2}|дня|дней|день))|"
                                                                   r"\d\d\d\d\.\d\d\.\d\d \d\d:\d\d)", text[1]):
                    if text[0] in ["checkdate"]: #next_scan
                        new_date = self.parse_date_and_time(text[1])
                        now = datetime.datetime.now()
                        now.fromtimestamp(now.timestamp() + 180)
                        if new_date < now:
                            self.bot.send_message(message.from_user.id,
                                                  "Указана дата предшествующая или соответствующая текущей." +
                                                  (
                                                      " Для старта сканирования прямо сейчас нажми: \"Начать сканирование\"" if
                                                      text[0] == "next_scan" else ""))
                        else:
                            self.config[text[0]] = self.parse_date_and_time(text[1])
                            self.db.set_file_conf(telegram.my_json_to_savol(self.config.copy()))
                            self.bot.reply_to(message, "Параметр {} изменен!".format(text[0]))
                    else:
                        new_delta = datetime.timedelta(seconds=int(text[1].split(" ", 1)[0]) * \
                                                               (60 if "мин" in text[1] else (
                                                                   3600 if "час" in text[1] else 86400)))
                        if text[0] == "scandelta" and new_delta < self.one_hour:
                            self.bot.send_message(message.from_user.id, "Период scandelta не может быть менее часа!")
                        elif text[0] == "reportdelta" and new_delta < self.five_minutes:
                            self.bot.send_message(message.from_user.id,
                                                  "Период reportdelta не может быть менее пяти минут!")

                        else:
                            self.bot.reply_to(message, "Параметр {} изменен!".format(text[0]))
                            self.config[text[0]] = new_delta
                            self.db.set_file_conf(telegram.my_json_to_savol(self.config.copy()))
                elif text[0] == "checkcenter":
                    self.config["checkcenter"] = text[1]
                    self.db.set_file_conf(telegram.my_json_to_savol(self.config.copy()))
                    self.bot.send_message(message.from_user.id,
                                          "Параметр checkcenter успешно изменен!")
                elif text[0].lower() == "port":
                    port_range = text[1].split("-")
                    if len(port_range) != 2 or not port_range[0].isdigit() or not port_range[1].isdigit():
                        self.bot.send_message(message.chat.id, "Диапазон портов указан неверно!")
                    else:
                        self.config[text[0]] = text[1]
                        self.db.set_file_conf(telegram.my_json_to_savol(self.config.copy()))
                        self.bot.reply_to(message, "Диапазон портов изменен!")


                # sending menu
                else:
                    if True:#self.config["is_alive"]:
                        self.bot.send_message(message.from_user.id, "Смотри, что я умею: ",
                                              reply_markup=self.abilities)
                        # bot.send_message(message.from_user.id, "1", reply_markup=markup)
                    else:
                        self.bot.send_message(message.from_user.id, "Смотри, что я умею: ",
                                              reply_markup=self.abilities_poweron)
                        # bot.send_message(message.from_user.id, "1", reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            call.data = call.data.lower()
            if call.data == "help":
                self.bot.send_message(call.message.chat.id,
                                      'Чтобы вызвать главное меню, отправь любое сообщение или нажми на кнопку'
                                      '"Главное меню".'
                                      'Чтобы изменить любую из настроек (кроме next_scan), просто напиши этот параметр, '
                                      'а затем через пробел значение, которое хочешь ему присвоить!',
                                      reply_markup=self.markup)
                self.bot.send_message(call.message.chat.id,
                                      "Интервал указывается в следующем виде: N [дней|часов|минут]. Дата "
                                      "указывается в форме ГГГГ.ММ.ДД ЧЧ:ММ. IP-адрес, домен сайта, либо маска/диапазон, "
                                      "указываются по одному в строке файла (файл отправляется нажатием "
                                      "кнопки \"Отправить файл\") Дефисы в доменах сайтов экранируются обратным"
                                      " слэшем, например: some\\-site.com. Порты указываются через диапазон. Для"
                                      "изменения значений типа истина/ложь достаточно просто указать этот "
                                      "параметр или нажать на соответствующую кнопку.")
            elif call.data == "config":
                self.bot.send_message(call.message.chat.id, 'Держи свои настройки!', reply_markup=self.markup)
                s = ""
                for par in self.config:
                    if par in ["scandelta"]: #reportdelta
                        s += "*" + par + "*" + " --> " + str(self.config[par]).replace("day", "день").replace("days",
                                                                                            "дней") + " - " + \
                             self.explainconfig[par] + "\n"
                    elif par in ["checkdate"]: # next_scan
                        s += "*" + par + "*" + " --> " + self.export_to_date_and_time(self.config[par]) + " - " + \
                             self.explainconfig[
                                 par] + "\n"
                    else:
                        s += "*" + par + "*" + " --> " + str(self.config[par]) + " - " + self.explainconfig[par] + "\n"
                self.bot.send_message(call.message.chat.id, s, parse_mode='Markdown', reply_markup=self.markup_config)
            elif call.data == "scan":
                threading.Thread(target=self.scan.scan).start()
                self.bot.send_message(call.message.chat.id, 'Сканирование началось!')
            elif call.data == "get":
                self.bot.send_message(call.message.chat.id, 'Лови файл!')
                with open("iplist.csv", "rb") as misc:
                    f = misc.read()
                self.bot.send_document(call.message.chat.id, f)
            elif call.data == "add":
                self.bot.send_message(call.message.chat.id, 'Кидай мне файл!')
                self.bot.register_next_step_handler(call.message, get_ip_list_file)
            elif call.data == "del":
                f = open("iplist.csv", "w")
                f.write("google.com")
                f.close()
                self.bot.send_message(call.message.chat.id, 'Список ip-адресов удален!')
            elif call.data == "new":
                self.bot.send_message(call.message.chat.id,
                                      'Перешли мне сообщение от этого пользователя, либо скажи мне его ID!')
                self.bot.register_next_step_handler(call.message, get_new_user)
            elif call.data == "stop":
                self.bot.send_message(call.message.chat.id, 'Выключаю рассылку!')
                self.config["is_alive"] = False
            elif call.data == "start":
                self.bot.send_message(call.message.chat.id, 'Включаю рассылку!')
                self.config["is_alive"] = True
            elif call.data.lower() in [x.lower() for x in self.conf_bools]:
                self.config[call.data] = not self.config[call.data]
                self.db.set_file_conf(telegram.my_json_to_savol(self.config.copy()))
                self.bot.send_message(call.message.chat.id, 'Параметр {} успешно изменен!'.format(call.data))

        @self.bot.message_handler(content_types=['text'])
        def get_new_user(message):
            try:
                new_user = str(message.forward_from.id)
            except:
                if message.text.isdigit() and len(message.text) >= 10:
                    new_user = str(message.text)
                else:
                    new_user = None
            if new_user == None:
                self.bot.send_message(message.chat.id, 'Я не получил ID!')
            else:
                self.db.insert_user(new_user)
                self.bot.send_message(message.chat.id, 'Зарегестрирован новый пользователь с ID = ' + new_user)

        @self.bot.message_handler(content_types=['document'])
        def get_ip_list_file(message):
            try:
                isdoc = message.document
            except:
                isdoc = None
            if isdoc:
                try:
                    file_info = self.bot.get_file(message.document.file_id)
                    downloaded_file = self.bot.download_file(file_info.file_path)
                    with open("iplist.csv", 'wb') as new_file:
                        new_file.write(downloaded_file)
                    self.bot.reply_to(message, "Поймал!")
                except Exception as e:
                    self.bot.reply_to(message, str(e))
            else:
                self.bot.reply_to(message, "Я не получил никакого файла :(")

        self.bot.polling(non_stop=True, interval=0)

    def bot_stop(self):
        self.bot.stop_polling()


if __name__ == "__main__":
    tel = telegram()
    tel.bot_start()
    #tel.broadcast_string("qwe")
