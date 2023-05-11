import sqlite3

try:
    sqlite_connection = sqlite3.connect('openai_telegram.db')
    sqlite_create_table_query = '''
                                CREATE TABLE if not EXISTS users (
                                telegram_id INTEGER PRIMARY KEY,
                                name TEXT NOT NULL,
                                username TEXT NOT NULL UNIQUE,
                                register_date TEXT NOT NULL,
                                number_of_requests INTEGER,
                                paid TEXT NOT NULL,
                                paid_number TEXT,
                                paid_date TEXT
                                );
                                '''

    cursor = sqlite_connection.cursor()
    print("База данных подключена к SQLite")
    cursor.execute(sqlite_create_table_query)
    sqlite_connection.commit()
    print("Таблица SQLite создана")

    cursor.close()

except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
finally:
    if (sqlite_connection):
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")
