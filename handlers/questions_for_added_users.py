from aiogram import Router, types

from database_manager import get_all_regions
from filters.changing_regions import RegionFilter
from keyboards.for_questions import get_keyboard_fab


forwarded_users = {}
router = Router()

selected_regions = {}




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
