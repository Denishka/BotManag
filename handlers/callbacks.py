from aiogram import Bot
from aiogram import Bot
from aiogram import F, Router, types

from callback_factories import RegionCallbackFactory
from database_manager import get_all_regions, add_user_to_regions, get_region_name_by_id, get_invite_links_for_user
from handlers.questions_for_added_links import update_region_text_fab_2
from main import forwarded_users, selected_regions, update_region_text_fab

router = Router()


@router.callback_query(lambda c: c.data == 'get_links')
async def process_callback(callback_query: types.CallbackQuery,bot: Bot):
    user_id = callback_query.from_user.id
    links = get_invite_links_for_user(user_id)
    text = "\n".join(links)
    await bot.send_message(callback_query.from_user.id, text)

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

@router.callback_query(RegionCallbackFactory.filter(F.action == "select_one_region"))
async def callbacks_region_select(
        callback: types.CallbackQuery,
        callback_data: RegionCallbackFactory
):
    user_info = forwarded_users.get(callback.from_user.id, {})
    # Устанавливаем выбранный регион
    user_info['region'] = callback_data.region
    forwarded_users[callback.from_user.id] = user_info
    region_name = get_region_name_by_id(user_info['region'])
    regions = get_all_regions()
    await update_region_text_fab_2(callback.message, region_name, regions)
    await callback.answer()

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

@router.callback_query(RegionCallbackFactory.filter(F.action == "finish2"))
async def callbacks_region_finish2(
        callback: types.CallbackQuery,
        callback_data: RegionCallbackFactory
):
    # Используем user_id, username и выбранные регионы из временного хранилища
    user_info = forwarded_users.get(callback.message.chat.id)
    if user_info is not None and 'regions' in user_info:
        await add_user_to_regions(user_info['user_id'], user_info['username'], user_info['regions'])
        region_names = [get_region_name_by_id(region) for region in user_info['regions']]
        await callback.message.edit_text(
            f"Выбор регионов завершен. Выбранные регионы: {', '.join(region_names)}. Теперь отправьте ссылки в чат.")
        # Сохраняем выбранные регионы во временное хранилище
        selected_regions[callback.message.chat.id] = user_info['region']
    else:
        await callback.message.edit_text("Выбор регионов завершен, отправьте ссылки для добавления")
        selected_regions[callback.message.chat.id] = user_info['region']
    await callback.answer()