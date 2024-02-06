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
from handlers import questions_for_get_links,questions_for_added_links, questions_for_remove_users, response_at_start
from main import forwarded_users

router=Router()
@router.message()
async def forward_message(message: types.Message):
    if message.forward_from:
        user_id = message.forward_from.id
        username = message.forward_from.username
        forwarded_users[message.chat.id] = {'user_id': user_id, 'username': username}
        # Получаем список регионов из базы данных
        regions = get_all_regions()
        keyboard = get_keyboard_fab(regions)

        await message.answer(
            f"В какие регионы вы хотите добавить пользователя с именем {username} и ID {user_id} ? Выбранные регионы: ",
            reply_markup=keyboard
        )
    else:
        return