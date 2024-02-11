from aiogram import Router, types
from aiogram.filters import Command

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
