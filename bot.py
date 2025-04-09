import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot("8088476279:AAGygNftDFbJGDQ3sBPw3ZzBxzHcsEPNAb8")
def create_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_films = KeyboardButton('Фильмы')
    button_music = KeyboardButton('Музыка')
    button_memes = KeyboardButton('Мемы')
    keyboard.add(button_films, button_music, button_memes)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Фильмы')
def send_film(message):
    bot.send_message(message.chat.id, "Крутой фильм", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Музыка')
def send_music(message):
    bot.send_message(message.chat.id, "Крутая музыка", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Мемы')
def send_meme(message):
    bot.send_message(message.chat.id, "Крутой мем", reply_markup=create_keyboard())

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()