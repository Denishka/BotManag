import asyncio

import psycopg2
from aiogram import types, Dispatcher, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
token = "6348779855:AAH7RgMVxgJs_U-Ys2bXd87kyaImAQK5GCE"

# bot = telegram.Bot(token)
bot = Bot(token)
router = Router()
dp = Dispatcher()
chat_ids = 0
conn = ""
cursor = ""
try:
    # localhost; 5432; postgres
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='127.0.0.1')
    cursor = conn.cursor()
    cursor.execute('Select chat_id from chat_list')
    chat_ids = cursor.fetchall()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            username TEXT,
            full_name TEXT
        )
    """)
    # Сохранение изменений
    conn.commit()
    print(chat_ids)
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')

@dp.chat_member()
async def new_chat_member(update: types.ChatMemberUpdated):
    if update.new_chat_member.status == 'member':
        user = update.new_chat_member.user
        # Проверка, существует ли пользователь в базе данных
        cursor.execute("""
                    SELECT * FROM users WHERE user_id = %s
                """, (user.id,))
        result = cursor.fetchone()
        # Если пользователь не существует, добавить его в базу данных
        if not result:
            cursor.execute("""
                        INSERT INTO users (user_id, username, full_name) VALUES (%s, %s, %s)
                    """, (user.id, user.username, user.full_name))
            conn.commit()
        await bot.send_message(update.chat.id, f'Привет, {user.full_name}, как дела? Ваш ID: {user.id}')

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Удалить пользователя"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="выберите одно из действий"
    )
    await message.reply("Выберите действие", reply_markup=keyboard)


@dp.message(F.text.lower() == "удалить пользователя")
async def with_puree(message: types.Message, state: FSMContext):
    await state.set_state(Form.username)
    await message.reply("Напишите username пользователя которого хотите удалить:")


class Form(StatesGroup):
    username = State()  # определение состояния
@dp.message(Form.username)  # обработчик будет вызван только когда состояние установлено в Form.username
async def process_username(message: types.Message, state: FSMContext):
    username = message.text
    # Проверка, существует ли пользователь в базе данных
    cursor.execute("""
                SELECT * FROM users WHERE username = %s
            """, (username,))
    result = cursor.fetchone()
    # Если пользователь существует, удалить его из чата
    if result:
        user_id = result[1]  # предполагается, что user_id хранится в первом столбце результата
        for chat_id_tuple in chat_ids:
            chat_id = int(chat_id_tuple[0])
            await bot.ban_chat_member(chat_id, user_id)
        await message.reply(f"Пользователь {username} был удален")
    else:
        await message.reply(f"Пользователь {username} не найден")
    await state.clear()  # завершение состояния
# @dp.message(lambda message: message.text.startswith('/ban'))
# async def start(message: types.Message):
#     user_id = int(message.text.split(" ")[1])
#     for chat_id_tuple in chat_ids:
#         chat_id = int(chat_id_tuple[0])
#         await bot.ban_chat_member(chat_id, user_id)

class Form(StatesGroup):
    username = State()

@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Нажми меня, чтобы отправить цветы Марине",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы отправить цветы",
        reply_markup=builder.as_markup()
    )

@dp.callback_query()
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str("цветы отправлены"))



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
