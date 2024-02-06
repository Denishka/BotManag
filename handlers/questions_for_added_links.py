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
from main import region_filter

router=Router()
@router.message(F.text.lower() == "добавить ссылки")
async def with_puree(message: types.Message):
    regions = get_all_regions()
    keyboard = get_keyboard_fab_2(regions)
    await message.answer(
        f"В какие регионы вы хотите добавить ссылки-приглашения? Выбранный регион: ",
        reply_markup=keyboard
    )

@router.message(region_filter)
async def region_selected(message: types.Message):
    await message.answer("Отправьте мне ссылки.")

async def update_region_text_fab_2(message: types.Message, new_region: str, regions):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"В какие регионы вы хотите добавить ссылки-приглашения? Выбранный регион: {new_region}",
            reply_markup=get_keyboard_fab_2(regions)
        )
@router.message(F.text.lower().startswith("https://t.me/"))
async def links_received(message: types.Message):
    links = message.text.split()
    # Получаем регион из временного хранилища
    region_id = selected_regions.get(message.chat.id)
    if region_id is not None:
        add_links_to_database(links, region_id)
        await message.answer("Ссылки успешно добавлены в базу данных.")
    else:
        await message.answer("Не удалось найти выбранный регион. Пожалуйста, выберите регион снова.")
