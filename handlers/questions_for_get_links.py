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
    get_user_by_id_from_database, add_links_to_database, get_invite_links_for_user
from keyboards.for_questions import get_keyboard_fab_2, get_keyboard_fab

router=Router()


@router.message(F.text.lower() == "получить ссылки")
async def with_puree(message: types.Message, state: FSMContext,bot: Bot):
    result = get_invite_links_for_user(message.from_user.id)
    if result:
        result_text = "\n".join(result)
        await bot.send_message(message.from_user.id, result_text)
    else:
        await bot.send_message(message.from_user.id, "Извините, ссылок для вас не найдено.")
