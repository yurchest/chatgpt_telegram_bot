import sqlite3

try:
    sqlite_connection = sqlite3.connect('openai_telegram.db')
    sqlite_create_table_query = '''
                                CREATE TABLE if not EXISTS error_logs (
                                date_time TEXT,
                                telegram_id TEXT,
                                error_message TEXT
                                );
                                '''

    cursor = sqlite_connection.cursor()
    print("База данных подключена к SQLite")
    cursor.execute(sqlite_create_table_query)
    sqlite_connection.commit()
    print("Таблица SQLite error_logs создана")

    cursor.close()

except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
finally:
    if (sqlite_connection):
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")
