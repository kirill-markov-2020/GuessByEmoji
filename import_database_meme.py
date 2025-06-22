import sqlite3
import os

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

photo_file_path = 'meme/sova.png'

with open(photo_file_path, 'rb') as file:
    photo_data = file.read()

emoji = "👵🦉🎥"
answer = "А я думала сова"

cursor.execute('''
INSERT INTO Content (category_id, content, emoji, answer)
VALUES (?, ?, ?, ?)
''', (3, photo_data, emoji, answer))

conn.commit()
conn.close()
