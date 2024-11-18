from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import Message
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


class UserState(StatesGroup):
    # Создайте класс UserState наследованный от StatesGroup.
    # Внутри этого класса опишите 3 объекта класса State: age, growth, weight (возраст, рост, вес).
    # Эта группа(класс) будет использоваться в цепочке вызовов message_handler'ов.
    age = State()
    growth = State()
    weight = State()


bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start_message(message: Message):
    """ обработчик команды start """
    # печатает строку в консоли 'Привет! Я бот помогающий твоему здоровью.' .
    # Запускается только когда написана команда '/start' в чате с ботом.
    await message.answer('Привет! Я бот помогающий твоему здоровью.')
    await message.answer('Для начала работы введите Calories')


@dp.message_handler(text='Calories')
async def set_age(message: Message):
    # Эта функция должна выводить в Telegram-бот сообщение 'Введите свой возраст:'.)
    await message.answer('Введите свой возраст:')
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
2024/01/20 00:00|Домашнее задание по теме "Машина состояний".
Цель: получить навык работы с состояниями в телеграм-боте.

Задача "Цепочка вопросов":
Необходимо сделать цепочку обработки состояний для нахождения нормы калорий для человека.
Группа состояний:
Импортируйте классы State и StatesGroup из aiogram.dispatcher.filters.state.
Создайте класс UserState наследованный от StatesGroup.
Внутри этого класса опишите 3 объекта класса State: age, growth, weight (возраст, рост, вес).
Эта группа(класс) будет использоваться в цепочке вызовов message_handler'ов. Напишите следующие функции для обработки состояний:
Функцию set_age(message):
Оберните её в message_handler, который реагирует на текстовое сообщение 'Calories'.
Эта функция должна выводить в Telegram-бот сообщение 'Введите свой возраст:'.
После ожидать ввода возраста в атрибут UserState.age при помощи метода set.
Функцию set_growth(message, state):
Оберните её в message_handler, который реагирует на переданное состояние UserState.age.
Эта функция должна обновлять данные в состоянии age на message.text (написанное пользователем сообщение). Используйте метод update_data.
Далее должна выводить в Telegram-бот сообщение 'Введите свой рост:'.
После ожидать ввода роста в атрибут UserState.growth при помощи метода set.
Функцию set_weight(message, state):
Оберните её в message_handler, который реагирует на переданное состояние UserState.growth.
Эта функция должна обновлять данные в состоянии growth на message.text (написанное пользователем сообщение). Используйте метод update_data.
Далее должна выводить в Telegram-бот сообщение 'Введите свой вес:'.
После ожидать ввода роста в атрибут UserState.weight при помощи метода set.
Функцию send_calories(message, state):
Оберните её в message_handler, который реагирует на переданное состояние UserState.weight.
Эта функция должна обновлять данные в состоянии weight на message.text (написанное пользователем сообщение). Используйте метод update_data.
Далее в функции запомните в переменную data все ранее введённые состояния при помощи state.get_data().
Используйте упрощённую формулу Миффлина - Сан Жеора для подсчёта нормы калорий (для женщин или мужчин - на ваше усмотрение). Данные для формулы берите из ранее объявленной переменной data по ключам age, growth и weight соответственно.
Результат вычисления по формуле отправьте ответом пользователю в Telegram-бот.
Финишируйте машину состояний методом finish().
!В течение написания этих функций помните, что они асинхронны и все функции и методы должны запускаться с оператором await.

Пример результата выполнения программы:


Примечания:
При отправке вашего кода на GitHub не забудьте убрать ключ для подключения к вашему боту!
Файл module_13_4.py загрузите на ваш GitHub репозиторий. В решении пришлите ссылку на него.
"""
