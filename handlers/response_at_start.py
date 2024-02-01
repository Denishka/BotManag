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

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # if message.chat.type != 'private':
    #     return
    # if message.from_user.id not in AUTHORIZED_USERS:
    #     await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    # else:
    kb = [
        [
            types.KeyboardButton(text="Удалить пользователя"),
            types.KeyboardButton(text="Получить ссылки"),
            types.KeyboardButton(text="Добавить ссылки"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="выберите одно из действий"
    )
    await message.reply("Выберите действие", reply_markup=keyboard)