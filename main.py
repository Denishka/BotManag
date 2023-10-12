import asyncio

import psycopg2
from aiogram import types, Dispatcher, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

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
        # Добавление информации о новом участнике в базу данных
        cursor.execute("""
                    INSERT INTO users (user_id, username, full_name) VALUES (%s, %s, %s)
                """, (user.id, user.username, user.full_name))

        # Сохранение изменений
        conn.commit()
        await bot.send_message(update.chat.id, f'Привет, {user.full_name}, как дела? Ваш ID: {user.id}')

# @dp.message(F.animation)
# async def echo_gif(message: types.Message):
#     await message.reply_animation(message.animation.file_id)

# @dp.message(F.text)
# async def photo_msg(message: Message):
#     await message.answer("Это точно какое-то изображение!")
# @dp.message(F.text == 'hello')
# async def user_joined_chat(message: types.Message):
#     print('Users changed')

@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text='/help')
# @dp.message(lambda message: message.text.startswith('/ban'))
# async def start(message: types.Message):
#     user_id = int(message.text.split(" ")[1])
#     for chat_id_tuple in chat_ids:
#         chat_id = int(chat_id_tuple[0])
#         await bot.ban_chat_member(chat_id, user_id)


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
@dp.message(Command(commands='start'))
async def start_command(message: types.Message):
    # Получение информации о всех пользователях из базы данных
    cursor.execute("SELECT username FROM users")
    usernames = cursor.fetchall()

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=f"{usernames}",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы отправить цветы",
        reply_markup=builder.as_markup()
    )

@dp.callback_query()
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str("цветы отправлены"))


# @dp.message(content_types=['new_chat_members'])
# async def new_member(message: types.Message):
#     for new_user in message.new_chat_members:
#         user_id = new_user.id
#         username = new_user.username
#         first_name = new_user.first_name
#         last_name = new_user.last_name
#
#         cursor.execute(f"INSERT INTO users (user_id, username, first_name, last_name) VALUES ({user_id}, '{username}', '{first_name}', '{last_name}')")
#         conn.commit()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
