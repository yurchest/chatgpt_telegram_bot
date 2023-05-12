from database import *

if __name__ == "__main__":
    sqlite_query = """
                    UPDATE users
                    SET number_of_requests = 1
                    WHERE username = "yurchest";
                    """
    with conn:
        cursor.execute(sqlite_query)

    #add_user('Name', "yusername", 2281488)
    print(is_user_paid(2281488))


