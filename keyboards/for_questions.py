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
from main import RegionCallbackFactory


def get_keyboard_fab(regions):
    builder = InlineKeyboardBuilder()
    for region in regions:
        builder.button(
            text=region[1], callback_data=RegionCallbackFactory(action="select", region=region[0])
        )
    builder.button(
        text="Подтвердить", callback_data=RegionCallbackFactory(action="finish")
    )
    # Выравниваем кнопки по 3 в ряд
    builder.adjust(2)
    return builder.as_markup()


def get_keyboard_fab_2(regions):
    builder = InlineKeyboardBuilder()
    for region in regions:
        builder.button(
            text=region[1], callback_data=RegionCallbackFactory(action="select_one_region", region=region[0])
        )
    builder.button(
        text="Подтвердить", callback_data=RegionCallbackFactory(action="finish2")
    )
    # Выравниваем кнопки по 3 в ряд
    builder.adjust(2)
    return builder.as_markup()
