from aiogram import types, Dispatcher, Bot
import asyncio

token = "6348779855:AAH7RgMVxgJs_U-Ys2bXd87kyaImAQK5GCE"

bot = Bot(token)
dp = Dispatcher()


@dp.message(lambda message: message.text.startswith('/start'))
async def start(message: types.Message):
    await message.answer('Hello , Marina!')


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

