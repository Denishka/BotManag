import asyncio

import psycopg2
from aiogram import Dispatcher, Bot
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

token = "6348779855:AAH7RgMVxgJs_U-Ys2bXd87kyaImAQK5GCE"

bot = Bot(token)
router = Router()
dp = Dispatcher()
chat_ids = 0
conn = ""
cursor = ""
try:
    # localhost; 5432; postgres
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
    conn.commit()
    print(chat_ids)
except:
    print('Can`t establish connection to database')


@dp.chat_member()
async def new_chat_member(update: types.ChatMemberUpdated):
    if update.new_chat_member.status == 'member':
        user = update.new_chat_member.user
        cursor.execute("""
                    SELECT * FROM users WHERE user_id = %s
                """, (user.id,))
        result = cursor.fetchone()
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
    username = State()


@dp.message(Form.username)
async def process_username(message: types.Message, state: FSMContext):
    username = message.text
    cursor.execute("""
                SELECT * FROM users WHERE username = %s
            """, (username,))
    result = cursor.fetchone()
    if result:
        user_id = result[1]
        for chat_id_tuple in chat_ids:
            chat_id = int(chat_id_tuple[0])
            await bot.ban_chat_member(chat_id, user_id)
        await message.reply(f"Пользователь {username} был удален")
    else:
        await message.reply(f"Пользователь {username} не найден")
    await state.clear()  # завершение состояния


class Form(StatesGroup):
    username = State()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
