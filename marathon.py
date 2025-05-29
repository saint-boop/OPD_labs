import asyncio
import csv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
import re
import os

load_dotenv()

# === Настройки ===
TOKEN = '7717717757:AAHgBRTNy9G_TUtKtEqDIq49Dmd3JHKik9s'
CSV_FILE = "registrations.csv"

# === Бот и диспетчер ===
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# === Состояния ===
class Form(StatesGroup):
    name = State()

# === Клавиатура с типами забега ===
def get_run_type_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 км", callback_data="run_5")],
        [InlineKeyboardButton(text="10 км", callback_data="run_10")],
        [InlineKeyboardButton(text="21 км", callback_data="run_21")]
    ])
    return kb

# === Проверка ФИО ===
def is_valid_name(name: str):
    return bool(re.fullmatch(r"[А-Яа-яA-Za-zЁё]+(?:\s+[А-Яа-яA-Za-zЁё]+)+", name.strip()))

# === Старт ===
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Введите ваше <b>ФИО</b>:")

# === Ввод ФИО ===
@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    if not is_valid_name(full_name):
        await message.answer("⚠ Пожалуйста, введите корректное ФИО (например, Иванов Иван).")
        return

    await state.update_data(name=full_name)
    await message.answer("Выберите <b>тип забега</b>:", reply_markup=get_run_type_keyboard())

# === Обработка выбора забега ===
@dp.callback_query(lambda c: c.data.startswith("run_"))
async def process_run_type(callback: CallbackQuery, state: FSMContext):
    run_type_map = {
        "run_5": "5 км",
        "run_10": "10 км",
        "run_21": "21 км"
    }

    run_type = run_type_map.get(callback.data, "Неизвестно")
    data = await state.get_data()
    name = data.get("name", "Неизвестно")

    # Сохраняем в CSV
    save_to_csv(name, run_type)

    await callback.message.edit_text(
        f"✅ Регистрация завершена!\n\n<b>ФИО:</b> {name}\n<b>Тип забега:</b> {run_type}"
    )
    await state.clear()

# === Сохранение в CSV ===
def save_to_csv(name, run_type):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["ФИО", "Тип забега"])
        writer.writerow([name, run_type])

# === Запуск ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
