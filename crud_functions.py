

def initiate_db():
    # initiate_db, которая создаёт таблицу Products, если она ещё не создана при помощи SQL запроса. Эта таблица должна содержать следующие поля:
    # id - целое число, первичный ключ
    # title(название продукта) - текст (не пустой)
    # description(описание) - текст
    # price(цена) - целое число (не пустой)
    ...


def get_all_products():
    # get_all_products, которая возвращает все записи из таблицы Products, полученные при помощи SQL запроса.
    products = [(f"Продукт{i}", f"описание {i}", 100*i, f'img{i}.jpg') for i in range(1, 5)]
    return products

