#-----------------------------------------------------------------------------------------------------------------------
# database common

import sqlite3
from sqlite3 import Connection as Db


def open_db(database_name: str) -> Db:
    db = sqlite3.connect(database_name)
    return db


def close_db(db: Db):
    db.commit()
    db.close()


def create_table(db: Db, table: str, keys: str):
    """
    :param db:      соединение с базой данных
    :param table:   имя таблицы
    :param keys:    строка ключей через запятую
    """
    cursor = db.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table} ({keys})')


def insert_to_db(db: Db, table: str, keys: str, params: tuple):
    cursor = db.cursor()
    cmd = f'INSERT INTO {table} ({keys}) VALUES ({",".join("?"*len(keys.split()))})'
    cursor.execute(cmd, params)


def delete_from_db(db: Db, table: str, cond: str = 'TRUE', params: tuple = ()):
    cursor = db.cursor()
    cmd = f'DELETE FROM {table} WHERE {cond}'
    cursor.execute(cmd, params)


def db_fetch_records(db: Db, table: str, cond: str = 'TRUE', params: tuple = ()) -> list:
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM {table} WHERE {cond}', params)
    return cursor.fetchall()


#-----------------------------------------------------------------------------------------------------------------------
db_id               = 'INTEGER PRIMARY KEY'
db_text             = 'TEXT'
db_text_not_null    = 'TEXT NOT NULL'
db_int              = 'INTEGER'
db_int_not_null     = 'INTEGER NOT NULL'


#-----------------------------------------------------------------------------------------------------------------------
TableKey = tuple[str, str]
TableKeys = tuple[TableKey, ...]


#-----------------------------------------------------------------------------------------------------------------------
# products

products_table = 'Products'
Product = list[str, str, int, str]
products_keys = (
    ('id',          db_id),             # первичный ключ
    ('title',       db_text_not_null),  # название продукта
    ('description', db_text),           # описание
    ('price',       db_int_not_null),   # цена
    ('image',       db_text),           # картинка
)


def create_products_table(db: Db, table: str, keys: TableKeys):
    keys = ', '.join([f'{key_name} {key_type}' for key_name, key_type in keys])
    create_table(db, table, keys)


#-----------------------------------------------------------------------------------------------------------------------
# users

users_table = 'Users'
User = list[str, str, int, int]
users_keys = (
    ('id',          db_id),             # первичный ключ
    ('username',    db_text_not_null),
    ('email',       db_text_not_null),
    ('age',         db_int_not_null),
    ('balance',     db_int_not_null),
)


def create_users_table(db: Db, table: str, keys: TableKeys):
    keys = ', '.join([f'{key_name} {key_type}' for key_name, key_type in keys])
    create_table(db, table, keys)


#-----------------------------------------------------------------------------------------------------------------------
# global db
database_filename = 'database.db'
global_db: Db


def get_all_products() -> list[Product]:
    """
    :return: все записи из таблицы Products, полученные при помощи SQL запроса.
    """
    products = [product[1:] for product in db_fetch_records(global_db, products_table)]   # skip id
    return products


def fill_products_table(count: int):
    key_names = ', '.join([key_name for key_name, _ in products_keys][1:])
    for i in range(1, count+1):
        insert_to_db(global_db, products_table, key_names, (
            f"Продукт{i}",
            f"описание {i}",
            100 * i,
            f'img{i}.jpg'
        ))


def add_user(username: str, email: str, age: int):
    """
    добавлять в таблицу Users вашей БД запись с переданными данными
    :param username:    имя пользователя
    :param email:       почту
    :param age:         возраст
    :return:
    """
    key_names = ', '.join([key_name for key_name, _ in users_keys][1:])
    # Для добавления записей в таблице используйте SQL запрос.
    # Баланс у новых пользователей всегда равен 1000.
    insert_to_db(global_db, users_table, key_names, (username, email, age, 1000))


def fill_users_table(count: int):
    for i in range(1, count+1):
        add_user(f'User{i}', f'user{i}@gmail.com', 20+i)


def initiate_db():
    """
    создаёт:
        - таблицу Products, если она ещё не создана при помощи SQL запроса.
        - таблицу Users, если она ещё не создана при помощи SQL запроса.
    """
    global global_db
    global_db = open_db(database_filename)

    create_products_table(global_db, products_table, products_keys)
    create_users_table(global_db, users_table, users_keys)


def clear_db():
    delete_from_db(global_db, products_table)
    delete_from_db(global_db, users_table)


def fill_db():
    fill_products_table(6)
    fill_users_table(10)


def commit_and_close_db():
    close_db(global_db)


def is_included(username: str):
    """
    :param username:    имя пользователя
    :return:            True, если такой пользователь есть в таблице Users в противном случае False
    """
    # Для получения записей используйте SQL запрос.
    global global_db
    records = db_fetch_records(global_db, users_table, 'user == ?', (username,))
    return len(records)


#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    initiate_db()
    clear_db()
    fill_db()
    commit_and_close_db()

