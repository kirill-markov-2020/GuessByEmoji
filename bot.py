import telebot
import sqlite3
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from gigachat_integration import GigaChatHelper

bot = telebot.TeleBot("7881735799:AAEfnq7_dET_fugTXRp0k9vRpOW1mpxJvBY")

try:
    GIGA_HELPER = GigaChatHelper(credentials="NWIyZDQ1MjUtNDhiYi00YmRkLWEyOWMtZTg1Yjk4MjgxYjJjOjlhNjdkZTI5LWY5MWUtNGIyZS1hMWYwLWQ5Mjk4OWY4NTE3Nw==")
except Exception as e:
    print(f"Ошибка при инициализации GigaChat: {e}")
    GIGA_HELPER = None

user_emoji_history = {}
user_correct_answers = {}

def create_hint_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_hint = KeyboardButton('Подсказка')
    button_exit = KeyboardButton('Выйти')
    keyboard.add(button_hint, button_exit)
    return keyboard

def create_category_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_films = KeyboardButton('Фильмы')
    button_music = KeyboardButton('Музыка')
    button_memes = KeyboardButton('Мемы')
    keyboard.add(button_films, button_music, button_memes)
    return keyboard

def get_random_emoji_and_content(chat_id, category_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    used_emojis = user_emoji_history.get(chat_id, {}).get(category_id, set())
    cursor.execute('SELECT id, emoji, content, answer FROM Content WHERE category_id = ?', (category_id,))
    results = cursor.fetchall()

    available_results = [result for result in results if result[0] not in used_emojis]

    conn.close()

    if available_results:
        result = random.choice(available_results)
        return result
    else:
        return None

def get_total_emojis_in_category(category_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Content WHERE category_id = ?', (category_id,))
    total_emojis = cursor.fetchone()[0]
    conn.close()
    return total_emojis

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=create_category_keyboard())

@bot.message_handler(func=lambda message: message.text in ['Фильмы', 'Музыка', 'Мемы'])
def handle_category(message):
    categories = {'Фильмы': 1, 'Музыка': 2, 'Мемы': 3}
    category_id = categories[message.text]

    if message.chat.id not in user_emoji_history:
        user_emoji_history[message.chat.id] = {}
    user_emoji_history[message.chat.id][category_id] = set()

    if message.chat.id not in user_correct_answers:
        user_correct_answers[message.chat.id] = {}
    user_correct_answers[message.chat.id][category_id] = 0

    emoji_data = get_random_emoji_and_content(message.chat.id, category_id)

    if emoji_data:
        emoji_id, emoji, content, answer = emoji_data
        user_emoji_history[message.chat.id][category_id].add(emoji_id)

        bot.send_message(message.chat.id, f"Угадайте, что это: {emoji}", reply_markup=create_hint_keyboard())
        bot.register_next_step_handler(message, check_answer, content, answer, category_id)
    else:
        bot.send_message(message.chat.id, "Нет доступного контента в этой категории.")


def check_answer(message, content, correct_answer, category_id):
    if message.text == 'Подсказка':
        # Отправляем подсказку и сразу даем следующее задание
        bot.send_message(message.chat.id, f"Подсказка: {correct_answer}")

        next_emoji_data = get_random_emoji_and_content(message.chat.id, category_id)

        if next_emoji_data:
            emoji_id, emoji, next_content, next_answer = next_emoji_data
            user_emoji_history[message.chat.id][category_id].add(emoji_id)
            bot.send_message(message.chat.id,
                             f"Угадайте, что это: {emoji}",
                             reply_markup=create_hint_keyboard())
            bot.register_next_step_handler(message, check_answer, next_content, next_answer, category_id)
        else:
            # Если эмодзи закончились
            total_emojis = get_total_emojis_in_category(category_id)
            correct_guesses = user_correct_answers[message.chat.id][category_id]
            bot.send_message(message.chat.id,
                             f"Все эмодзи в этой категории кончились. Вы угадали {correct_guesses} из {total_emojis} эмодзи.",
                             reply_markup=create_category_keyboard())

    elif message.text == 'Выйти':
        # Возвращаемся к выбору категории
        bot.send_message(message.chat.id,
                         "Выберите категорию:",
                         reply_markup=create_category_keyboard())
    else:
        # Проверяем ответ пользователя
        user_answer = message.text.strip()

        # 1. Сначала проверяем точное совпадение (регистронезависимо)
        exact_match = user_answer.lower() == correct_answer.lower()

        # 2. Если нет точного совпадения, проверяем через GigaChat
        semantic_match = False
        if not exact_match and GIGA_HELPER:
            try:
                semantic_match = GIGA_HELPER.compare_answers(user_answer, correct_answer)
            except Exception as e:
                print(f"Ошибка при проверке ответа через GigaChat: {e}")
                semantic_match = False

        if exact_match or semantic_match:
            # Отправляем соответствующий медиа-контент
            if category_id == 1:  # Фильмы
                bot.send_video(message.chat.id, content)
            elif category_id == 2:  # Музыка
                bot.send_audio(message.chat.id, content, title="Audio")
            elif category_id == 3:  # Мемы
                bot.send_photo(message.chat.id, content)

            # Увеличиваем счетчик правильных ответов
            user_correct_answers[message.chat.id][category_id] += 1

            # Даем следующее задание
            next_emoji_data = get_random_emoji_and_content(message.chat.id, category_id)

            if next_emoji_data:
                emoji_id, emoji, next_content, next_answer = next_emoji_data
                user_emoji_history[message.chat.id][category_id].add(emoji_id)
                bot.send_message(message.chat.id,
                                 f"Правильно! 🎉 Следующее задание: {emoji}",
                                 reply_markup=create_hint_keyboard())
                bot.register_next_step_handler(message, check_answer, next_content, next_answer, category_id)
            else:
                # Если эмодзи закончились
                total_emojis = get_total_emojis_in_category(category_id)
                correct_guesses = user_correct_answers[message.chat.id][category_id]
                bot.send_message(message.chat.id,
                                 f"Все эмодзи в этой категории кончились. Вы угадали {correct_guesses} из {total_emojis} эмодзи.",
                                 reply_markup=create_category_keyboard())
        else:
            # Ответ неверный
            bot.send_message(message.chat.id,
                             "Неправильно! Попробуйте снова или запросите подсказку.",
                             reply_markup=create_hint_keyboard())
            bot.register_next_step_handler(message, check_answer, content, correct_answer, category_id)
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
