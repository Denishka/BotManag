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
from handlers.response_at_start import cmd_start
from keyboards.for_questions import get_keyboard_fab_2, get_keyboard_fab
from main import bot, delete_user_from_chats

router = Router()
AUTHORIZED_USERS = [319186657]  # id HR

class Form(StatesGroup):
    confirm = State()
    username = State()
@router.message(F.text.lower() == "удалить пользователя")
async def with_puree(message: types.Message, state: FSMContext):
    if message.chat.type != ChatType.PRIVATE:
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    else:
        await state.set_state(Form.username)
        await message.reply("Напишите username пользователя, которого хотите удалить:")

@router.message(Form.username)
async def process_username(message: types.Message, state: FSMContext):
    if message.from_user.id not in AUTHORIZED_USERS:
        await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    else:
        username = message.text
        user = get_user_by_username_from_database(username)
        if user:
            await state.update_data(name=message.text)
            await state.set_state(Form.confirm)
            await message.answer(
                "Вы действительно хотите удалить пользователя?",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Да"),
                            KeyboardButton(text="Нет"),
                        ]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ),
            )
        else:
            await message.reply(f"Пользователь {username} не найден")
            await state.clear()

@router.message(Form.confirm, F.text.casefold() == "да")
async def process_like_write_bots(message: types.Message, state: FSMContext):
    dict_inf = await state.get_data()
    username = dict_inf["name"]
    user = get_user_by_username_from_database(username)
    await delete_user_from_chats(user, username, message)
    await message.reply("Пользователь удален!")
    await cmd_start(message)
    await state.clear()