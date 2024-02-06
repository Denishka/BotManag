import asyncio
from contextlib import suppress

from aiogram import Dispatcher, Bot
from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from config_reader import config
from database_manager import init_database
from filters.changing_regions import RegionFilter
from handlers import questions_for_get_links, questions_for_added_links, questions_for_remove_users, response_at_start, \
    questions_for_added_users
from handlers.questions_for_added_users import forwarded_users
from keyboards.for_questions import get_keyboard_fab

AUTHORIZED_USERS = [319186657]  # id HR

async def update_region_text_fab(message: types.Message, new_regions: list, regions):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"В какие регионы вы хотите добавить пользователя с именем {forwarded_users[319186657]['username']} и ID {forwarded_users[319186657]['user_id']} ? Выбранные регионы:  {', '.join(new_regions)}",
            reply_markup=get_keyboard_fab(regions)
        )
async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    dp.include_router(response_at_start.router)
    dp.include_router(questions_for_remove_users.router)
    dp.include_router(questions_for_added_links.router)
    dp.include_router(questions_for_get_links.router)
    dp.include_router(questions_for_added_users.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    init_database()
    asyncio.run(main())


