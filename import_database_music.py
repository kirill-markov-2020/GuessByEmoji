import sqlite3
import os


conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

music_file_path = 'music/lolita-na-titanike.mp3'

with open(music_file_path, 'rb') as file:
    music_data = file.read()

emoji = "🤫🧊🚢"
answer = "На титанике"

cursor.execute('''
INSERT INTO Content (category_id, content, emoji, answer)
VALUES (?, ?, ?, ?)
''', (2, music_data, emoji, answer))

conn.commit()
conn.close()
