from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage, BaseStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
#import asyncio


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


class UserState(StatesGroup):
    # Создайте класс UserState наследованный от StatesGroup.
    # Внутри этого класса опишите 3 объекта класса State: age, growth, weight (возраст, рост, вес).
    # Эта группа(класс) будет использоваться в цепочке вызовов message_handler'ов.
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message: Message):
    """ обработчик команды start """
    # печатает строку в консоли 'Привет! Я бот помогающий твоему здоровью.' .
    # Запускается только когда написана команда '/start' в чате с ботом.
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    info_button = KeyboardButton(text="Информация")
    calc_button = KeyboardButton(text="Рассчитать")
    kb.row(info_button, calc_button)
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


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
    # Эта функция должна выводить в Telegram-бот сообщение 'Введите свой возраст:'.)
    await call.message.answer('Введите свой возраст:')#, reply_markup=)
    await call.answer()
    # После ожидать ввода возраста в атрибут UserState.age при помощи метода set.
    await UserState.age.set()


@dp.message_handler(state = UserState.age)
async def set_growth(message: Message, state: BaseStorage):
    try:
        age = float(message.text)
        assert age > 0
    except (ValueError, AssertionError):
        await message.answer('Возраст должен быть положительным числом!')
        return

    # Эта функция должна обновлять данные в состоянии age на message.text
    await state.update_data(age=age)
    # Далее должна выводить в Telegram-бот сообщение 'Введите свой рост:'.
    await message.answer('Введите свой рост:')
    # После ожидать ввода роста в атрибут UserState.growth при помощи метода set.
    await UserState.growth.set()


@dp.message_handler(state = UserState.growth)
async def set_weight(message: Message, state: BaseStorage):
    try:
        growth = float(message.text)
        assert growth > 0
    except (ValueError, AssertionError):
        await message.answer('Рост должен быть положительным числом!')
        return

    # Эта функция должна обновлять данные в состоянии growth на message.text
    await state.update_data(growth=growth)
    # Далее должна выводить в Telegram-бот сообщение 'Введите свой вес:'.
    await message.answer('Введите свой вес:')
    # После ожидать ввода роста в атрибут UserState.weight при помощи метода set.
    await UserState.weight.set()


@dp.message_handler(state = UserState.weight)
async def send_calories(message: Message, state: BaseStorage):
    try:
        weight = float(message.text)
        assert weight > 0
    except (ValueError, AssertionError):
        await message.answer('Вес должен быть положительным числом!')
        return

    # Эта функция должна обновлять данные в состоянии weight на message.text
    await state.update_data(weight=weight)
    # Далее в функции запомните в переменную data все ранее введённые состояния
    data = await state.get_data()
    age, growth, weight = (data[k] for k in ['age', 'growth', 'weight'])
    # Используйте упрощённую формулу Миффлина - Сан Жеора для подсчёта нормы калорий
    calories = calc_calories('M', age, growth, weight)
    # Результат вычисления по формуле отправьте ответом пользователю в Telegram-бот.
    await message.answer(f'Ваша норма калорий: {calories}')
    # Финишируйте машину состояний методом finish().
    await state.finish()


@dp.message_handler()
async def all_messages(message: Message):
    """ обработчик остальных сообщений """
    # печатает строку в консоли 'Введите команду /start, чтобы начать общение.'.
    # Запускается при любом обращении не описанном ранее.
    await message.answer('Введите команду /start, чтобы начать общение.')


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()


"""
2024/01/22 00:00|Домашнее задание по теме "Инлайн клавиатуры".
Цель: научится создавать Inline клавиатуры и кнопки на них в Telegram-bot.

Задача "Ещё больше выбора":
Необходимо дополнить код предыдущей задачи, чтобы при нажатии на кнопку 'Рассчитать' присылалась Inline-клавиатруа.
Создайте клавиатуру InlineKeyboardMarkup с 2 кнопками InlineKeyboardButton:
С текстом 'Рассчитать норму калорий' и callback_data='calories'
С текстом 'Формулы расчёта' и callback_data='formulas'
Создайте новую функцию main_menu(message), которая:
Будет обёрнута в декоратор message_handler, срабатывающий при передаче текста 'Рассчитать'.
Сама функция будет присылать ранее созданное Inline меню и текст 'Выберите опцию:'
Создайте новую функцию get_formulas(call), которая:
Будет обёрнута в декоратор callback_query_handler, который будет реагировать на текст 'formulas'.
Будет присылать сообщение с формулой Миффлина-Сан Жеора.
Измените функцию set_age и декоратор для неё:
Декоратор смените на callback_query_handler, который будет реагировать на текст 'calories'.
Теперь функция принимает не message, а call. Доступ к сообщению будет следующим - call.message.
По итогу получится следующий алгоритм:
Вводится команда /start
На эту команду присылается обычное меню: 'Рассчитать' и 'Информация'.
В ответ на кнопку 'Рассчитать' присылается Inline меню: 'Рассчитать норму калорий' и 'Формулы расчёта'
По Inline кнопке 'Формулы расчёта' присылается сообщение с формулой.
По Inline кнопке 'Рассчитать норму калорий' начинает работать машина состояний по цепочке.

Пример результата выполнения программы:

Примечания:
При отправке вашего кода на GitHub не забудьте убрать ключ для подключения к вашему боту!
Файл module_13_6.py загрузите на ваш GitHub репозиторий. В решении пришлите ссылку на него.
"""
