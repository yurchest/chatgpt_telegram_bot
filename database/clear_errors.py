import sqlite3

try:
    sqlite_connection = sqlite3.connect('openai_telegram.db')
    sqlite_query = """
                        DELETE FROM error_logs;
                        """

    cursor = sqlite_connection.cursor()
    print("База данных подключена к SQLite")
    cursor.execute(sqlite_query)
    sqlite_connection.commit()
    print("Успешно очищены ошибки")

    cursor.close()

except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
finally:
    if (sqlite_connection):
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")