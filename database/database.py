import sqlite3
from datetime import datetime
import pytz

conn = sqlite3.connect('database/openai_telegram.db')
cursor = conn.cursor()


def is_user_exists(telegram_id):
    cursor.execute("select exists(select 1 from users where telegram_id = ?)", (telegram_id,))
    [exists] = cursor.fetchone()  # fetch and unpack the only row our query returns
    if exists:
        return True
    else:
        return False


def add_user(name: str, username: str, telegram_id: int):
    values = [
        (name, username, telegram_id, datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"), 1, "false"),
    ]
    sqlite_insert_query = """
                            INSERT INTO users(name, username, telegram_id, register_date, number_of_requests, paid)
                            VALUES (?,?,?,?,?,?);
                            """
    cursor.executemany(sqlite_insert_query, values)
    conn.commit()


def increment_number_of_requests(telegram_id: int):
    sqlite_query = """
                    UPDATE users
                    SET number_of_requests = number_of_requests + 1
                    WHERE telegram_id = ?;
                    """
    with conn:
        cursor.execute(sqlite_query, (telegram_id,))


def get_all_users():
    sqlite_query = """SELECT * FROM users;"""
    cursor.execute(sqlite_query)
    data = cursor.fetchall()
    result = []
    for user in data:
        result.append({
            "telegram_id": user[0],
            "name": user[1],
            "username": user[2],
            "register_date": user[3],
            "number_of_requests": user[4],
            "paid": user[5],
        })
    return result
