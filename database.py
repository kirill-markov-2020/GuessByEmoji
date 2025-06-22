
import sqlite3

database_path = 'bot_database.db'
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    content BLOB,
    emoji TEXT,
    answer TEXT,
    FOREIGN KEY (category_id) REFERENCES Categories (id)
)
''')

categories = ['Фильмы', 'Музыка', 'Мемы']
for category in categories:
    cursor.execute('INSERT INTO Categories (name) VALUES (?)', (category,))

conn.commit()
conn.close()

database_path