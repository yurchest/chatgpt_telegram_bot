import sqlite3
from decouple import config


try:
    # PATH_TO_DB = config("PATH_TO_DB")
    conn = sqlite3.connect("openai_telegram.db")
    cursor = conn.cursor()

    sqlite_query = """SELECT * FROM error_logs;"""
    cursor.execute(sqlite_query)
    data = cursor.fetchall()
    for error in data:
        print(f"{error[1]}  {error[0]} {error[2]}")

    cursor.close()

except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
finally:
    if conn:
        conn.close()
        print("Соединение с SQLite закрыто")
