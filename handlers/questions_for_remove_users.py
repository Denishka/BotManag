from aiogram import Bot
from aiogram import F, Router, types
from aiogram import exceptions
from aiogram.enums.chat_type import ChatType
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database_manager import get_chat_ids, \
    delete_user_from_database, get_user_by_username_from_database
from handlers.response_at_start import cmd_start
from main import AUTHORIZED_USERS

router = Router()


class Form(StatesGroup):
    confirm = State()
    username = State()


@router.message(F.text.lower() == "удалить пользователя")
async def with_puree(message: types.Message, state: FSMContext, bot: Bot):
    if message.chat.type != ChatType.PRIVATE:
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    else:
        await state.set_state(Form.username)
        await message.reply("Напишите username пользователя, которого хотите удалить:")


@router.message(Form.username)
async def process_username(message: types.Message, state: FSMContext, bot: Bot):
    if message.from_user.id not in AUTHORIZED_USERS:
        await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    else:
        username = message.text
        user = get_user_by_username_from_database(username)
        if user is None:
            await message.reply(f"Пользователь {username} не найден")
            await state.clear()
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



@router.message(Form.confirm, F.text.casefold() == "да")
async def process_like_write_bots(message: types.Message, state: FSMContext, bot: Bot):
    dict_inf = await state.get_data()
    username = dict_inf["name"]
    user = get_user_by_username_from_database(username)
    await delete_user_from_chats(user, username, message, bot)
    await message.reply("Пользователь удален!")
    await cmd_start(message)
    await state.clear()


@router.message(Form.confirm, F.text.casefold() == "нет")
async def process_dont_like_write_bots(message: types.Message, state: FSMContext):
    await message.reply("Вы отказались удалять пользователя")
    await cmd_start(message)
    await state.clear()


async def delete_user_from_chats(user, username, message, bot: Bot):
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
