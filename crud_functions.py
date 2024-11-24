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


def fetch_records(db: Db, table: str, cond: str = 'TRUE', params: tuple = ()) -> list:
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM {table} WHERE {cond}', params)
    return cursor.fetchall()


#-----------------------------------------------------------------------------------------------------------------------
def add_user(username: str, email: str, age: int):
    """
    добавлять в таблицу Users вашей БД запись с переданными данными
    :param username:    имя пользователя
    :param email:       почту
    :param age:         возраст
    :return:
    """
    # Баланс у новых пользователей всегда равен 1000.
    # Для добавления записей в таблице используйте SQL запрос.
    ...


def is_included(username: str):
    """
    :param username:    имя пользователя
    :return:            True, если такой пользователь есть в таблице Users в противном случае False
    """
    # Для получения записей используйте SQL запрос.
    ...


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


def fill_products_table(db: Db, table: str, keys: TableKeys, count: int):
    key_names = ', '.join([key_name for key_name, _ in keys][1:])
    for i in range(1, count+1):
        insert_to_db(db, table, key_names, (
            f"Продукт{i}",
            f"описание {i}",
            100 * i,
            f'img{i}.jpg'
        ))


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
database_filename = 'database.db'

def initiate_db():
    """
    создаёт
    - таблицу Products, если она ещё не создана при помощи SQL запроса.
    - таблицы Users, если она ещё не создана при помощи SQL запроса.
    """
    db = open_db(database_filename)

    create_products_table(db, products_table, products_keys)
    delete_from_db(db, products_table)
    fill_products_table(db, products_table, products_keys, 4)

    create_users_table(db, users_table, users_keys)
    delete_from_db(db, users_table)

    close_db(db)


def get_all_products() -> list[Product]:
    """
    :return: все записи из таблицы Products, полученные при помощи SQL запроса.
    """
    db = open_db(database_filename)
    products = [product[1:] for product in fetch_records(db, products_table)]   # skip id
    close_db(db)
    return products


if __name__ == '__main__':
    initiate_db()
