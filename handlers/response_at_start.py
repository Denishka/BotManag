from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from database_manager import execute_and_commit_query
from main import AUTHORIZED_USERS

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [[types.KeyboardButton(text="Получить ссылки")]]

    if message.from_user.id in AUTHORIZED_USERS:
        kb.append([types.KeyboardButton(text="Удалить пользователя")])
        kb.append([types.KeyboardButton(text="Добавить ссылку")])

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="выберите одно из действий"
    )
    await message.reply("Выберите действие", reply_markup=keyboard)


def get_chat_id(message: Message):
    chat_id = message.chat.id
    insert_chat_query = """
    INSERT INTO chat_list (chat_id)
    VALUES (%s)
    ON CONFLICT (chat_id) DO NOTHING;
    """
    execute_and_commit_query(insert_chat_query, (chat_id,))
    print("Chat ID:", chat_id)

def get_chat_id(message: Message):
    chat_id = message.chat.id
    insert_chat_query = """
    INSERT INTO chat_list (chat_id)
    VALUES (%s)
    ON CONFLICT (chat_id) DO NOTHING;
    """
    execute_and_commit_query(insert_chat_query, (chat_id,))
    print("Chat ID:", chat_id)


@router.message(lambda message: message.text == "get_chat_id")
async def get_chat_id_router(message: Message):
    get_chat_id(message)


@router.channel_post(lambda message: message.text == "get_chat_id")
async def get_channel_id(message: Message):
    get_chat_id(message)

