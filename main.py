import asyncio
from contextlib import suppress
from typing import Optional
from aiogram import Dispatcher, Bot
from aiogram import F, Router, types
from aiogram import exceptions
from aiogram.enums.chat_type import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, Filter
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
from database_manager import init_database, get_connection_to_database, get_all_regions, get_chat_ids, \
    delete_user_from_database, add_user_to_regions, insert_user_to_database, get_user_by_username_from_database, \
    get_user_by_id_from_database, add_links_to_database
from keyboards.for_questions import get_keyboard_fab_2, get_keyboard_fab
from handlers import questions_for_get_links,questions_for_added_links, questions_for_remove_users, response_at_start, questions_for_added_users



AUTHORIZED_USERS = [319186657]  # id HR

forwarded_users = {}

async def update_region_text_fab(message: types.Message, new_regions: list, regions):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"В какие регионы вы хотите добавить пользователя с именем {forwarded_users[319186657]['username']} и ID {forwarded_users[319186657]['user_id']} ? Выбранные регионы:  {', '.join(new_regions)}",
            reply_markup=get_keyboard_fab(regions)
        )

# Временное хранилище для выбранных регионов
selected_regions = {}


region = []

region_filter = RegionFilter()


async def delete_user_from_chats(user, username, message,bot: Bot):
    user_id = user[1]
    chat_ids = get_chat_ids()
    for chat_id_tuple in chat_ids:
        chat_id = int(chat_id_tuple[0])
        try:
            await bot.ban_chat_member(chat_id, user_id)
        except exceptions.TelegramBadRequest:
            continue
    delete_user_from_database(user_id)
    await message.answer(f"Пользователь {username} был удален")
async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    dp.include_router(response_at_start)
    dp.include_router(questions_for_remove_users)
    dp.include_router(questions_for_added_links)
    dp.include_router(questions_for_get_links)
    dp.include_router(questions_for_added_users)

    await dp.start_polling(bot)


if __name__ == '__main__':
    init_database()
    asyncio.run(main())


