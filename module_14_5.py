#from email import message_from_binary_file

from aiogram import Bot, Dispatcher, executor
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage, BaseStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
#import asyncio

from string import ascii_letters

from crud_functions import initiate_db, get_all_products, close_db, is_included, add_user
products: list


try:
    from credentials import token
except ImportError:
    print("Error: You must use your own Telegram Bot API token to use this program")
    print("Place token in credentials.py")
    exit(1)


def calc_calories(gender: str, age: float, growth: float, weight: float):
    """
    формула Миффлина - Сан Жеора для подсчёта нормы калорий для женщин или мужчин
    :param gender: пол, 'M' или 'F'
    :param age: вес в кг
    :param growth: рост в см
    :param weight: возраст в г
    :return: норма калорий
    """
    # (10 х вес в кг) + (6, 25 х рост в см) – (5 х возраст в г) + 5(M) или -161(F).
    return (10.0 * weight) + (6.25 * growth) - (5.0 * age) + 5.0 if gender == 'M' else -161.0


bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


#-----------------------------------------------------------------------------------------------------------------------
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message: Message):
    """ обработчик команды start """
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(
        KeyboardButton(text="Информация"),
        KeyboardButton(text="Рассчитать"),
        KeyboardButton(text="Купить"),
        # Кнопки главного меню дополните кнопкой "Регистрация".
        KeyboardButton(text="Регистрация")
    )
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Купить')
async def get_buying_list(message: Message):
    for name, description, price, img in products:
        text = f'Название: {name} | Описание: {description} | Цена: {price}'
        try:
            with open(img, 'rb') as file:
                await message.answer_photo(file, text)  # с картинкой, если есть
        except IOError:
            await message.answer(text)                  # или без картинки

    kb = InlineKeyboardMarkup()
    kb.add(*[InlineKeyboardButton(text=name, callback_data=f"product_buying {name}") for name, _, _, _ in products])
    await message.answer('Выберите продукт для покупки:', reply_markup=kb)


@dp.callback_query_handler(lambda t: t.data and t.data.startswith('product_buying '))
async def send_confirm_message(call: CallbackQuery):
    product_name = call.data.replace('product_buying ', '')
    await call.message.answer(f"Вы успешно приобрели {product_name}!")


@dp.message_handler(text='Рассчитать')
async def main_menu(message: Message):
    kb = InlineKeyboardMarkup()
    info_button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
    calc_button = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
    kb.row(info_button, calc_button)
    await message.answer('Выберите опцию:', reply_markup=kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: CallbackQuery):
    await call.message.answer('''\
формула Миффлина - Сан Жеора для подсчёта нормы калорий
для женщин:
(10 х вес в кг) + (6, 25 х рост в см) – (5 х возраст в г) -161
для мужчин:
(10 х вес в кг) + (6, 25 х рост в см) – (5 х возраст в г) + 5\
''')


@dp.callback_query_handler(text='calories')
async def set_age(call: CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state = UserState.age)
async def set_growth(message: Message, state: BaseStorage):
    try:
        age = float(message.text)
        assert age > 0
    except (ValueError, AssertionError):
        await message.answer('Возраст должен быть положительным числом!')
        return

    await state.update_data(age=age)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state = UserState.growth)
async def set_weight(message: Message, state: BaseStorage):
    try:
        growth = float(message.text)
        assert growth > 0
    except (ValueError, AssertionError):
        await message.answer('Рост должен быть положительным числом!')
        return

    await state.update_data(growth=growth)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state = UserState.weight)
async def send_calories(message: Message, state: BaseStorage):
    try:
        weight = float(message.text)
        assert weight > 0
    except (ValueError, AssertionError):
        await message.answer('Вес должен быть положительным числом!')
        return

    await state.update_data(weight=weight)
    data = await state.get_data()
    age, growth, weight = (data[k] for k in ['age', 'growth', 'weight'])
    calories = calc_calories('M', age, growth, weight)
    await message.answer(f'Ваша норма калорий: {calories}')
    await state.finish()


#-----------------------------------------------------------------------------------------------------------------------
# Создайте цепочку изменений состояний RegistrationState.
# Напишите новый класс состояний RegistrationState
class RegistrationState(StatesGroup):
    # с следующими объектами класса State: username, email, age, balance(по умолчанию 1000).
    username = State()
    email = State()
    age = State()
    balance = State('1000')


@dp.message_handler(text='Регистрация')
async def sign_up(message: Message):
    # Эта функция должна выводить в Telegram-бот сообщение "Введите имя пользователя (только латинский алфавит):".
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    # После ожидать ввода имени в атрибут RegistrationState.username при помощи метода set.
    await RegistrationState.username.set()


@dp.message_handler(state = RegistrationState.username)
async def set_username(message: Message, state: BaseStorage):
    username = message.text

    if not all(map(lambda c: c in ascii_letters, username)):
        await message.answer("только латинский алфавит")
        return

    if is_included(username):
        # Если пользователь с таким message.text есть в таблице,
        # то выводить "Пользователь существует, введите другое имя"
        await message.answer("Пользователь существует, введите другое имя")
        # и запрашивать новое состояние для RegistrationState.username.
        return

    # Если пользователя message.text ещё нет в таблице,
    # то должны обновляться данные в состоянии username на message.text.
    await state.update_data(username=username)
    # Далее выводится сообщение "Введите свой email:"
    await message.answer("Введите свой email:")
    # и принимается новое состояние RegistrationState.email.
    await RegistrationState.email.set()


@dp.message_handler(state = RegistrationState.email)
async def set_email(message: Message, state: BaseStorage):
    # Эта функция должна обновляться данные в состоянии RegistrationState.email на message.text.
    await state.update_data(email=message.text)
    # Далее выводить сообщение "Введите свой возраст:":
    await message.answer("Введите свой возраст:")
    # После ожидать ввода возраста в атрибут RegistrationState.age.
    await RegistrationState.age.set()


@dp.message_handler(state = RegistrationState.age)
async def set_age(message: Message, state: BaseStorage):
    try:
        age = float(message.text)
        assert age > 0
    except (ValueError, AssertionError):
        await message.answer('Возраст должен быть положительным числом!')
        return

    # Эта функция должна обновляться данные в состоянии RegistrationState.age на message.text.
    await state.update_data(age=age)
    # Далее брать все данные (username, email и age) из состояния
    data = await state.get_data()
    username, email, age = (data[k] for k in ['username', 'email', 'age'])
    # и записывать в таблицу Users при помощи ранее написанной crud-функции add_user.
    add_user(username, email, age)
    # В конце завершать приём состояний при помощи метода finish().
    await state.finish()


#-----------------------------------------------------------------------------------------------------------------------
@dp.message_handler()
async def all_messages(message: Message):
    """
    обработчик остальных сообщений
    Запускается при любом обращении не описанном ранее.
    """
    await message.answer('Введите команду /start, чтобы начать общение.')


def main():
    initiate_db()
    try:
        global products
        products = get_all_products()
        executor.start_polling(dp, skip_updates=True)
    finally:
        close_db()


if __name__ == '__main__':
    main()


"""
2024/02/02 00:00|Домашнее задание по теме "Написание примитивной ORM"
Если вы решали старую версию задачи, проверка будет производиться по ней.
Ссылка на старую версию тут.
Цель: написать простейшие CRUD функции для взаимодействия с базой данных.

Задача "Регистрация покупателей":
Подготовка:
Для решения этой задачи вам понадобится код из предыдущей задачи. Дополните его, следуя пунктам задачи ниже.

Дополните файл crud_functions.py, написав и дополнив в нём следующие функции:
initiate_db дополните созданием таблицы Users, если она ещё не создана при помощи SQL запроса. Эта таблица должна содержать следующие поля:
id - целое число, первичный ключ
username - текст (не пустой)
email - текст (не пустой)
age - целое число (не пустой)
balance - целое число (не пустой)
add_user(username, email, age), которая принимает: имя пользователя, почту и возраст. Данная функция должна добавлять в таблицу Users вашей БД запись с переданными данными. Баланс у новых пользователей всегда равен 1000. Для добавления записей в таблице используйте SQL запрос.
is_included(username) принимает имя пользователя и возвращает True, если такой пользователь есть в таблице Users, в противном случае False. Для получения записей используйте SQL запрос.

Изменения в Telegram-бот:
Кнопки главного меню дополните кнопкой "Регистрация".
Напишите новый класс состояний RegistrationState с следующими объектами класса State: username, email, age, balance(по умолчанию 1000).
Создайте цепочку изменений состояний RegistrationState.
Фукнции цепочки состояний RegistrationState:
sing_up(message):
Оберните её в message_handler, который реагирует на текстовое сообщение 'Регистрация'.
Эта функция должна выводить в Telegram-бот сообщение "Введите имя пользователя (только латинский алфавит):".
После ожидать ввода имени в атрибут RegistrationState.username при помощи метода set.
set_username(message, state):
Оберните её в message_handler, который реагирует на состояние RegistrationState.username.
Если пользователя message.text ещё нет в таблице, то должны обновляться данные в состоянии username на message.text. Далее выводится сообщение "Введите свой email:" и принимается новое состояние RegistrationState.email.
Если пользователь с таким message.text есть в таблице, то выводить "Пользователь существует, введите другое имя" и запрашивать новое состояние для RegistrationState.username.
set_email(message, state):
Оберните её в message_handler, который реагирует на состояние RegistrationState.email.
Эта функция должна обновляться данные в состоянии RegistrationState.email на message.text.
Далее выводить сообщение "Введите свой возраст:":
После ожидать ввода возраста в атрибут RegistrationState.age.
set_age(message, state):
Оберните её в message_handler, который реагирует на состояние RegistrationState.age.
Эта функция должна обновляться данные в состоянии RegistrationState.age на message.text.
Далее брать все данные (username, email и age) из состояния и записывать в таблицу Users при помощи ранее написанной crud-функции add_user.
В конце завершать приём состояний при помощи метода finish().
Перед запуском бота пополните вашу таблицу Products 4 или более записями для последующего вывода в чате Telegram-бота.

Пример результата выполнения программы:
Машина состояний и таблица Users в Telegram-bot:


Результат в таблице Users:


Файлы module_14_5.py, crud_functions.py, а также файл с базой данных и таблицей Users загрузите на ваш GitHub репозиторий. В решении пришлите ссылку на него.
"""
