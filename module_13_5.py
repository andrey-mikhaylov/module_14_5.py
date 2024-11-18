from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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

kb = ReplyKeyboardMarkup(resize_keyboard=True)
info_button = KeyboardButton(text="Информация")
calc_button = KeyboardButton(text="Рассчитать")
kb.row(info_button, calc_button)


@dp.message_handler(commands=['start'])
async def start_message(message: Message):
    """ обработчик команды start """
    # печатает строку в консоли 'Привет! Я бот помогающий твоему здоровью.' .
    # Запускается только когда написана команда '/start' в чате с ботом.
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def set_age(message: Message):
    # Эта функция должна выводить в Telegram-бот сообщение 'Введите свой возраст:'.)
    await message.answer('Введите свой возраст:', reply_markup=types.ReplyKeyboardRemove())
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
2024/01/21 00:00|Домашнее задание по теме "Клавиатура кнопок".
Цель: научится создавать клавиатуры и кнопки на них в Telegram-bot.

Задача "Меньше текста, больше кликов":
Необходимо дополнить код предыдущей задачи, чтобы вопросы о параметрах тела для расчёта калорий выдавались по нажатию кнопки.
Измените massage_handler для функции set_age. Теперь этот хэндлер будет реагировать на текст 'Рассчитать', а не на 'Calories'.
Создайте клавиатуру ReplyKeyboardMarkup и 2 кнопки KeyboardButton на ней со следующим текстом: 'Рассчитать' и 'Информация'. Сделайте так, чтобы клавиатура подстраивалась под размеры интерфейса устройства при помощи параметра resize_keyboard.
Используйте ранее созданную клавиатуру в ответе функции start, используя параметр reply_markup.
В итоге при команде /start у вас должна присылаться клавиатура с двумя кнопками. При нажатии на кнопку с надписью 'Рассчитать' срабатывает функция set_age с которой начинается работа машины состояний для age, growth и weight.

Пример результата выполнения программы:
Клавиатура по команде /start:`

После нажатия на кнопку 'Рассчитать':


Примечания:
При отправке вашего кода на GitHub не забудьте убрать ключ для подключения к вашему боту!
Файл module_13_5.py загрузите на ваш GitHub репозиторий. В решении пришлите ссылку на него.
"""
