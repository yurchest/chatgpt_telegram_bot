from database import *

if __name__ == "__main__":
    sqlite_query = """
                    UPDATE users
                    SET number_of_requests = 1
                    WHERE username = "yurchest";
                    """
    with conn:
        cursor.execute(sqlite_query)