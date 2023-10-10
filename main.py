from aiogram import types, Dispatcher, Bot
import asyncio
import telegram
import psycopg2

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


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

