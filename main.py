from random import randint

from aiogram import types, Dispatcher, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import telegram
import psycopg2
from aiogram import F
from aiogram.filters import Command


token = "6348779855:AAH7RgMVxgJs_U-Ys2bXd87kyaImAQK5GCE"

#bot = telegram.Bot(token)
bot = Bot(token)

dp = Dispatcher()
chat_ids = 0
try:
    # localhost; 5432; postgres
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='127.0.0.1')
    cursor = conn.cursor()
    cursor.execute('Select chat_id from chat_list')
    chat_ids = cursor.fetchall()
    print(chat_ids)
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')


@dp.message(lambda message: message.text.startswith('/ban'))
async def start(message: types.Message):
    user_id = int(message.text.split(" ")[1])
    for chat_id_tuple in chat_ids:
        chat_id = int(chat_id_tuple[0])
        await bot.ban_chat_member(chat_id, user_id)

@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(7, 8)))

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

