from contextlib import suppress

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest

from database_manager import get_all_regions, get_region_name_by_id, add_user_to_regions
from filters.changing_regions import RegionFilter
from handlers.callback_factories import RegionCallbackFactory
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


@router.callback_query(RegionCallbackFactory.filter(F.action == "select"))
async def callbacks_region_select(
        callback: types.CallbackQuery,
        callback_data: RegionCallbackFactory
):
    user_info = forwarded_users.get(callback.from_user.id, {})
    # Если регион еще не выбран, инициализируем список
    if 'regions' not in user_info:
        user_info['regions'] = []
    # Добавляем выбранный регион в список
    user_info['regions'].append(callback_data.region)
    forwarded_users[callback.from_user.id] = user_info
    region_names = [get_region_name_by_id(region) for region in user_info['regions']]
    regions = get_all_regions()
    await update_region_text_fab(callback.message, region_names, regions)
    await callback.answer()


async def update_region_text_fab(message: types.Message, new_regions: list, regions):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"В какие регионы вы хотите добавить пользователя с именем {forwarded_users[319186657]['username']} и ID {forwarded_users[319186657]['user_id']} ? Выбранные регионы:  {', '.join(new_regions)}",
            reply_markup=get_keyboard_fab(regions)
        )


@router.callback_query(RegionCallbackFactory.filter(F.action == "finish"))
async def callbacks_region_finish(
        callback: types.CallbackQuery,
        callback_data: RegionCallbackFactory
):
    # Используем user_id, username и выбранные регионы из временного хранилища
    user_info = forwarded_users.get(callback.message.chat.id)
    if user_info is not None and 'regions' in user_info:
        await add_user_to_regions(user_info['user_id'], user_info['username'], user_info['regions'])
        region_names = [get_region_name_by_id(region) for region in user_info['regions']]
        await callback.message.edit_text(
            f"Выбор регионов завершен. Выбранные регионы: {', '.join(region_names)}")
    else:
        await callback.message.edit_text("Выбор регионов завершен.")
    await callback.answer()
