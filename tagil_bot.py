import telebot
from telebot import types

# parse_mode='HTML' позволяет использовать <b>, <i>, <code>, <a href=""> во всех сообщениях
bot = telebot.TeleBot('8266635215:AAHYpAj1GheTN-ux7VFNvEH39Jn5eGtQfXY', parse_mode='HTML')

@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message):
    bot.send_message(message.chat.id, "Бот запущен!")

if __name__ == '__main__':
    # skip_pending=True игнорирует сообщения, написанные пока бот был выключен
    bot.infinity_polling(skip_pending=True)