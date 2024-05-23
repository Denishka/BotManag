import asyncio

from aiogram import Dispatcher, Bot
from config_reader import config
from database_manager import init_database, add_start_regions
from handlers import questions_for_get_links, questions_for_added_links, questions_for_remove_users, response_at_start, \
    questions_for_added_users

AUTHORIZED_USERS = [319186657]  # id HR


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
    add_start_regions()
    asyncio.run(main())
