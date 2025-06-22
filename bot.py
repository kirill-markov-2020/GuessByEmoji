import telebot
import sqlite3
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot("7881735799:AAEfnq7_dET_fugTXRp0k9vRpOW1mpxJvBY")

# Глобальный словарь для отслеживания использованных эмодзи
user_emoji_history = {}

def create_category_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_films = KeyboardButton('Фильмы')
    button_music = KeyboardButton('Музыка')
    button_memes = KeyboardButton('Мемы')
    keyboard.add(button_films, button_music, button_memes)
    return keyboard

def create_continue_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_continue = KeyboardButton('Продолжить')
    button_back = KeyboardButton('Вернуться к выбору категорий')
    keyboard.add(button_continue, button_back)
    return keyboard

def get_random_emoji_and_content(chat_id, category_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    # Получаем все эмодзи из выбранной категории, которые еще не использовались
    used_emojis = user_emoji_history.get(chat_id, {}).get(category_id, set())
    cursor.execute('SELECT id, emoji, content, answer FROM Content WHERE category_id = ?', (category_id,))
    results = cursor.fetchall()

    # Фильтруем результаты, чтобы исключить использованные эмодзи
    available_results = [result for result in results if result[0] not in used_emojis]

    conn.close()

    if available_results:
        # Выбираем случайный эмодзи из доступных
        result = random.choice(available_results)
        return result
    else:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=create_category_keyboard())

@bot.message_handler(func=lambda message: message.text in ['Фильмы', 'Музыка', 'Мемы'])
def handle_category(message):
    categories = {'Фильмы': 1, 'Музыка': 2, 'Мемы': 3}
    category_id = categories[message.text]

    emoji_data = get_random_emoji_and_content(message.chat.id, category_id)

    if emoji_data:
        emoji_id, emoji, content, answer = emoji_data

        # Обновляем историю использованных эмодзи
        if message.chat.id not in user_emoji_history:
            user_emoji_history[message.chat.id] = {}
        if category_id not in user_emoji_history[message.chat.id]:
            user_emoji_history[message.chat.id][category_id] = set()

        user_emoji_history[message.chat.id][category_id].add(emoji_id)

        bot.send_message(message.chat.id, f"Угадайте, что это: {emoji}")
        bot.register_next_step_handler(message, check_answer, content, answer, category_id)
    else:
        bot.send_message(message.chat.id, "Вы использовали все эмодзи в этой категории. Выберите другую категорию:", reply_markup=create_category_keyboard())

def check_answer(message, content, correct_answer, category_id):
    if message.text.lower() == correct_answer.lower():
        if category_id == 1:  # Фильмы
            bot.send_video(message.chat.id, content)
        elif category_id == 2:  # Музыка
            bot.send_audio(message.chat.id, content, title="Audio")
        elif category_id == 3:  # Мемы
            bot.send_photo(message.chat.id, content)

        bot.send_message(message.chat.id, "Правильно! Вот ваш контент.", reply_markup=create_continue_keyboard())
    else:
        bot.send_message(message.chat.id, "Неправильно! Попробуйте снова.")

@bot.message_handler(func=lambda message: message.text in ['Продолжить', 'Вернуться к выбору категорий'])
def handle_continue(message):
    if message.text == 'Продолжить':
        # Определяем последнюю использованную категорию
        last_category_id = next(reversed(user_emoji_history[message.chat.id]))
        emoji_data = get_random_emoji_and_content(message.chat.id, last_category_id)

        if emoji_data:
            emoji_id, emoji, content, answer = emoji_data
            user_emoji_history[message.chat.id][last_category_id].add(emoji_id)
            bot.send_message(message.chat.id, f"Угадайте, что это: {emoji}")
            bot.register_next_step_handler(message, check_answer, content, answer, last_category_id)
        else:
            bot.send_message(message.chat.id, "Вы использовали все эмодзи в этой категории. Выберите другую категорию:", reply_markup=create_category_keyboard())
    else:
        bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=create_category_keyboard())

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
