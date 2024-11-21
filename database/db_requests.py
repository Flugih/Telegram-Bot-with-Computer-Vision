import sqlite3

connection = sqlite3.connect("database/database.db")
cursor = connection.cursor()


def create_table():
    # cursor.execute(
    #     f"""INSERT INTO stats (user_chat_id) VALUES (1)"""
    # )
    # connection.commit()
    #
    cursor.execute('''CREATE TABLE stats (
                            id INTEGER PRIMARY KEY NOT NULL,
                            user_chat_id integer,
                            text_translate integer,
                            chatgpt_search integer,
                            images_sent integer,
                            day_of_purchase integer,
                            user_status text
                                                )
                            ''')
    connection.commit()

    cursor.execute(
        """SELECT * FROM stats"""
    )
    yes = cursor.fetchone()
    print(yes)
    pass


async def add_user(chat_id):
    cursor.execute(
        f"""SELECT id FROM stats WHERE user_chat_id = {chat_id}"""
    )
    rows = cursor.fetchall()
    if not rows:
        if chat_id == 6694745423:
            cursor.execute(
                f"""INSERT INTO stats (user_status, user_chat_id, text_translate, chatgpt_search, images_sent) VALUES ('Admin', {chat_id}, 0, 0, 0)"""
            )
        else:
            cursor.execute(
                f"""INSERT INTO stats (user_status, user_chat_id, text_translate, chatgpt_search, images_sent) VALUES ('Beta-Test', {chat_id}, 0, 0, 0)"""
            )
    connection.commit()


async def add_requests(type_of_request, chat_id):
    cursor.execute(
        f"""SELECT {type_of_request} FROM stats WHERE user_chat_id = {chat_id}"""
    )
    number_of_requests = cursor.fetchone()[0] + 1

    cursor.execute(
        f"""UPDATE stats SET {type_of_request} = {number_of_requests} WHERE user_chat_id = {chat_id}"""
    )
    connection.commit()


async def get_last_id():
    cursor.execute(
        """SELECT id FROM stats ORDER BY ID DESC LIMIT 1"""
    )
    return cursor.fetchone()[0]


async def get_requests(user_id, user_chat_id, type_of_request):
    if user_chat_id is None:
        cursor.execute(
            f"""SELECT {type_of_request} FROM stats WHERE id = {user_id}"""
        )
        return cursor.fetchone()[0]
    elif user_id is None:
        cursor.execute(
            f"""SELECT {type_of_request} FROM stats WHERE user_chat_id = {user_chat_id}"""
        )
        return cursor.fetchone()[0]


async def get_day_of_purchase(user_chat_id):
    cursor.execute(
        f"""SELECT day_of_purchase FROM stats WHERE user_chat_id = {user_chat_id}"""
    )
    return cursor.fetchone()[0]


async def end_of_sub(user_chat_id):
    cursor.execute(
        f"""UPDATE stats SET user_status = 'Default' WHERE user_chat_id = {user_chat_id}"""
    )
    cursor.execute(
        f"""UPDATE stats SET day_of_purchase = null WHERE user_chat_id = {user_chat_id}"""
    )
    connection.commit()


async def get_status(user_chat_id):
    cursor.execute(
        f"""SELECT user_status FROM stats WHERE user_chat_id = {user_chat_id}"""
    )
    return cursor.fetchone()[0]
