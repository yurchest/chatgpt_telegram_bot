import sqlite3
from datetime import datetime
import pytz
from decouple import config

PATH_TO_DB = config("PATH_TO_DB")
conn = sqlite3.connect(PATH_TO_DB)
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
        (name, username, telegram_id, datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"), 1,
         "false", 5),
    ]
    sqlite_insert_query = """
                            INSERT INTO users(name, username, telegram_id, register_date, number_of_requests, paid, nums_img_generated)
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
            "paid_number": user[6],
            "paid_date": user[7]
        })
    return result


def is_user_paid(telegram_id):
    cursor.execute("SELECT paid FROM users WHERE telegram_id = ?", (telegram_id,))
    [is_paid] = cursor.fetchone()  # fetch and unpack the only row our query returns
    if is_paid == "true":
        return True
    else:
        return False


def is_user_test_period(telegram_id):
    cursor.execute("SELECT number_of_requests FROM users WHERE telegram_id = ?", (telegram_id,))
    [number_of_requests] = cursor.fetchone()  # fetch and unpack the only row our query returns
    if number_of_requests < 50:
        return True
    else:
        return False


def set_user_paid(telegram_id, paid_number):
    current_date = datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
    sqlite_query = """
                        UPDATE users
                        SET paid = "true",
                        paid_number = ?,
                        paid_date = ?
                        WHERE telegram_id = ?;
                        """
    with conn:
        cursor.execute(sqlite_query, (paid_number, current_date, telegram_id))


def add_error_to_db(error: str, telegram_id: str, filename: str, line: int, exc_type: type):
    current_date = datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
    sqlite_insert_query = """
                            INSERT INTO error_logs(date_time, filename, line, exc_type, telegram_id, error_message)
                            VALUES (?,?,?,?,?,?);
                            """
    with conn:
        cursor.execute(sqlite_insert_query, (current_date, filename, line, str(exc_type), telegram_id, error))


def get_last_30_errors() -> str:
    sqlite_query = """
                    SELECT date_time, filename, line, exc_type, telegram_id, error_message
                    FROM error_logs
                    Order By date_time DESC LIMIT 10
                    """
    with conn:
        cursor.execute(sqlite_query)
        data = cursor.fetchall()
        result_text = ""
        for error in data:
            result_text += f"{error[0]}| {error[3]}: {error[5]}\n"

    return result_text


def clear_errors():
    sqlite_query = """
                    DELETE FROM error_logs;
                    """
    with conn:
        cursor.execute(sqlite_query)


def is_user_allow_generate_img(telegram_id):
    cursor.execute("SELECT nums_img_generated FROM users WHERE telegram_id = ?", (telegram_id,))
    [nums_img_generated] = cursor.fetchone()  # fetch and unpack the only row our query returns
    if nums_img_generated > 0:
        return True
    else:
        return False


def get_nums_img_generated(telegram_id) -> int:
    cursor.execute("SELECT nums_img_generated FROM users WHERE telegram_id = ?", (telegram_id,))
    [nums_img_generated] = cursor.fetchone()  # fetch and unpack the only row our query returns
    return nums_img_generated


def add_30_nums_img_generated(telegram_id):
    sqlite_query = """
                    UPDATE users
                    SET nums_img_generated = nums_img_generated + 30
                    WHERE telegram_id = ?;
                    """
    with conn:
        cursor.execute(sqlite_query, (telegram_id,))


def decrement_nums_img_generated(telegram_id):
    sqlite_query = """
                    UPDATE users
                    SET nums_img_generated = nums_img_generated - 1
                    WHERE telegram_id = ?;
                    """
    with conn:
        cursor.execute(sqlite_query, (telegram_id,))
