import asyncio

import aiogram.enums.chat_type
import psycopg2
from aiogram import Dispatcher, Bot
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config_reader import config
from aiogram.types.chat import Chat
from aiogram.enums.chat_type import ChatType

bot = Bot(token=config.bot_token.get_secret_value())

router = Router()
dp = Dispatcher()


def get_connection_to_database():
    return psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='127.0.0.1')


def init_database():
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT
            )
        """)
    conn.commit()


def get_chat_ids():
    try:
        # localhost; 5432; postgres
        conn = get_connection_to_database()
        cursor = conn.cursor()
        cursor.execute('Select chat_id from chat_list')
        return cursor.fetchall()
    except:
        print('Can`t establish connection to database')
        # Обработка, в случае если база данных недоступна


def insert_user_to_database(user):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
                INSERT INTO users (user_id, username, full_name) VALUES (%s, %s, %s)
            """, (user.id, user.username, user.full_name))
    conn.commit()


def get_user_by_id_from_database(user):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
                SELECT * FROM users WHERE user_id = %s
            """, (user.id,))
    return cursor.fetchone()


@dp.chat_member()
async def new_chat_member(update: types.ChatMemberUpdated):
    if update.new_chat_member.status == 'member':
        user = update.new_chat_member.user
        users = get_user_by_id_from_database(user)
        if not users:
            insert_user_to_database(user)
        await bot.send_message(update.chat.id, f'Привет, {user.full_name}, как дела? Ваш ID: {user.id}')


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type != ChatType.PRIVATE:
        return
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


def get_user_by_username_from_database(username):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT * FROM users WHERE username = %s
                """, (username,))
    return cursor.fetchone()


async def delete_user_from_chats(user, message):
    user_id = user[1]
    chat_ids = get_chat_ids()
    username = message.text
    for chat_id_tuple in chat_ids:
        chat_id = int(chat_id_tuple[0])
        await bot.ban_chat_member(chat_id, user_id)
    await message.reply(f"Пользователь {username} был удален")


@dp.message(Form.username)
async def process_username(message: types.Message, state: FSMContext):
    username = message.text
    user = get_user_by_username_from_database(username)
    if user:
        await delete_user_from_chats(user, message)
    else:
        await message.reply(f"Пользователь {username} не найден")
    await state.clear()


class Form(StatesGroup):
    username = State()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
