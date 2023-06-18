import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import pandas as pd

# Настройки бота
TOKEN = "6044510900:AAGkFWv6On-GGViDKMXVGYM6ylYIIl88KIY"

# Настройки логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Загрузка данных из датасета
dataset = pd.read_csv('Cars5_modified.csv', sep=';', encoding='utf-8')

# Состояния для поиска
class SearchState(StatesGroup):
    BRAND = State()
    MODEL = State()
    YEAR = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttonsrch = ["Начать поиск"]
    keyboard.add(*buttonsrch)
    await message.answer("Привет! Я бот по поиску необходимых вам автомобилей на сайте 'auto.ru'. "
                         "Для продолжения нажмите кнопку 'Начать поиск'",
                         reply_markup=keyboard)

# Обработчик нажатия кнопки 'Начать поиск'
@dp.message_handler(text='Начать поиск')
async def search_start(message: types.Message):
    await message.reply("Напишите искомую марку автомобиля:")
    await SearchState.BRAND.set()

# Обработчик марки автомобиля
@dp.message_handler(state=SearchState.BRAND)
async def search_brand(message: types.Message, state: FSMContext):
    brand = message.text
    await message.reply("Напишите искомую модель автомобиля:")
    await SearchState.MODEL.set()
    await state.update_data(brand=brand)

# Обработчик модели автомобиля
@dp.message_handler(state=SearchState.MODEL)
async def search_model(message: types.Message, state: FSMContext):
    model = message.text
    await message.reply("Напишите требуемый год выпуска автомобиля:")
    await SearchState.YEAR.set()
    await state.update_data(model=model)

# Обработчик года выпуска автомобиля
@dp.message_handler(state=SearchState.YEAR)
async def search_year(message: types.Message, state: FSMContext):
    year = message.text

    # Получение сохраненных данных (марка и модель)
    data = await state.get_data()
    brand = data['brand']
    model = data['model']

    # Выполнение поиска по заданным параметрам
    results = dataset.loc[(dataset['Brand'] == brand) & (dataset['Model'] == model) & (dataset['Year'] == int(year))]

    # Вывод результатов пользователю
    if len(results) > 0:
        # Вывод результатов
        response = "Результаты поиска:\n\n"
        for index, row in results.iterrows():
            price = row['Price']
            link = row['Link']
            city = row['City']
            response += f"Цена: {price}\n"
            response += f"Город: {city}\n"
            response += f"Ссылка: {link}\n\n"

        await message.reply(response)
    else:
        await message.reply("Ничего не найдено")

    # Завершение поиска
    await state.finish()

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp)