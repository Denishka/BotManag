from aiogram import Router, types
from aiogram.filters import Command

from main import AUTHORIZED_USERS

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # if message.chat.type != 'private':
    #     return

    kb = [[types.KeyboardButton(text="Получить ссылки")]]

    if message.from_user.id in AUTHORIZED_USERS:
        kb.append([types.KeyboardButton(text="Удалить пользователя")])
        kb.append([types.KeyboardButton(text="Добавить ссылки")])

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="выберите одно из действий"
    )
    await message.reply("Выберите действие", reply_markup=keyboard)
