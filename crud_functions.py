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
database_filename = 'database.db'

products_table = 'Products'
product_keys = 'title, description, price, image'
Product = list[str, str, int, str]

users_table = 'Users'


def initiate_db():
    """
    создаёт таблицу Products, если она ещё не создана при помощи SQL запроса.
    """
    db = open_db(database_filename)

    keys = ', '.join((
        'id INTEGER PRIMARY KEY',   # целое число, первичный ключ
        'title TEXT NOT NULL',      # название продукта - текст (не пустой)
        'description TEXT',         # описание - текст
        'price INTEGER NOT NULL',   # цена - целое число (не пустой)
        'image TEXT'                # картинка
        ))

    create_table(db, products_table, keys)

    delete_from_db(db, products_table)

    for i in range(1, 5):
        insert_to_db(db, products_table, product_keys, (
            f"Продукт{i}",
            f"описание {i}",
            100 * i,
            f'img{i}.jpg'
        ))

    close_db(db)


def get_all_products() -> list[Product]:
    """
    :return: все записи из таблицы Products, полученные при помощи SQL запроса.
    """
    db = open_db(database_filename)
    products = [product[1:] for product in fetch_records(db, products_table)]   # skip id
    close_db(db)
    return products


#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    initiate_db()
