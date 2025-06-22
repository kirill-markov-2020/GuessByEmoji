import sqlite3
import os

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

video_file_path = 'movie/1plus1.mp4'

with open(video_file_path, 'rb') as file:
    video_data = file.read()

emoji = "💩➕👨‍🦽"
answer = "1 + 1"

cursor.execute('''
INSERT INTO Content (category_id, content, emoji, answer)
VALUES (?, ?, ?, ?)
''', (1, video_data, emoji, answer))

conn.commit()
conn.close()
