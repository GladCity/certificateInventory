import telebot

bot = telebot.TeleBot('5894305427:AAE03pvAh-6u9p3nftQzYHlyx5E2Ra9GekM')



keyboard = telebot.types.InlineKeyboardMarkup()  # наша клавиатура
key_yes = telebot.types.InlineKeyboardButton(text='Хочу пиццу', callback_data='pizza')  # кнопка «Да»
keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
key_no = telebot.types.InlineKeyboardButton(text='Хочу суши', callback_data='sushi')
keyboard.add(key_no)
i = True

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global i
    if i:
        bot.send_message(message.from_user.id, "I get message: " + message.text)
    else:
        bot.send_message(message.from_user.id, text="Что выберешь?", reply_markup=keyboard)
    i = not i
    #bot.register_next_step_handler(message, callback_worker)




@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "pizza":
        bot.send_message(call.message.chat.id, 'Ты хочешь пиццу!')
    elif call.data == "sushi":
        bot.send_message(call.message.chat.id, 'Ты хочешь суши!')
    #bot.register_next_step_handler(call, get_text_messages)


bot.polling(none_stop=True, interval=0)
