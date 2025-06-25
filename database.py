import sqlite3

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'movies.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year TEXT,
            poster TEXT,
            embed_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_all_movies():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")
    rows = cursor.fetchall()
    conn.close()
    movies = []
    for row in rows:
        movies.append({
            "id": row[0],
            "title": row[1],
            "year": row[2],
            "poster": row[3],
            "embed_url": row[4]
        })
    return movies

def save_movie(title, year, poster, embed_url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movies (title, year, poster, embed_url) VALUES (?, ?, ?, ?)",
                   (title, year, poster, embed_url))
    conn.commit()
    conn.close()

# Add to end of database.py just for now:
if __name__ == "__main__":
    init_db()
