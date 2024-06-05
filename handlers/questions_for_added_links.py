from contextlib import suppress
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from database_manager import get_all_regions, add_links_to_database, add_user_to_regions, get_region_name_by_id
from filters.changing_regions import RegionFilter
from handlers.callback_factories import RegionCallbackFactory
from handlers.questions_for_added_users import selected_regions, forwarded_users
from keyboards.for_questions import get_keyboard_fab
from aiogram.filters.state import State, StatesGroup

region = []

region_filter = RegionFilter()
router = Router()


class LinkStates(StatesGroup):
    waiting_for_description = State()


@router.message(F.text.lower() == "добавить ссылки")
async def with_puree(message: types.Message):
    regions = get_all_regions()
    keyboard = get_keyboard_fab(regions, action="select_one_region", finish_action="finish2")
    await message.answer(
        f"В какие регионы вы хотите добавить ссылки-приглашения? Выбранный регион: ",
        reply_markup=keyboard
    )


@router.message(F.text.lower().startswith("https://t.me/"))
async def links_received(message: types.Message, state: FSMContext):
    link = message.text.strip()
    region_id = selected_regions.get(message.chat.id)
    if region_id is not None:
        await state.update_data(link=link, region_id=region_id)
        await state.set_state(LinkStates.waiting_for_description)
        await message.answer("Пожалуйста, введите описание для этой ссылки:")
    else:
        await message.answer("Не удалось найти выбранный регион. Пожалуйста, выберите регион снова.")


@router.message(LinkStates.waiting_for_description)
async def link_description_received(message: types.Message, state: FSMContext):
    description = message.text.strip()
    user_data = await state.get_data()
    link = user_data['link']
    region_id = user_data['region_id']

    add_links_to_database(link, description, region_id)

    await message.answer("Ссылка и описание успешно добавлены в базу данных.")
    await state.clear()


@router.callback_query(RegionCallbackFactory.filter(F.action == "select_one_region"))
async def callbacks_region_select(
        callback: types.CallbackQuery,
        callback_data: RegionCallbackFactory
):
    user_info = forwarded_users.get(callback.from_user.id, {})
    user_info['region'] = callback_data.region
    forwarded_users[callback.from_user.id] = user_info
    region_name = get_region_name_by_id(user_info['region'])
    regions = get_all_regions()
    await update_region_text(callback.message, region_name, regions)
    await callback.answer()


async def update_region_text(message: types.Message, new_region: str, regions):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"В какие регионы вы хотите добавить ссылки-приглашения? Выбранный регион: {new_region}",
            reply_markup=get_keyboard_fab(regions, action="select_one_region", finish_action="finish2")

        )


@router.callback_query(RegionCallbackFactory.filter(F.action == "finish2"))
async def callbacks_region_finish(
        callback: types.CallbackQuery,
):
    user_info = forwarded_users.get(callback.message.chat.id)
    if user_info is not None and 'regions' in user_info:
        await add_user_to_regions(user_info['user_id'], user_info['username'], user_info['regions'])
        region_names = [get_region_name_by_id(region) for region in user_info['regions']]
        await callback.message.edit_text(
            f"Выбор регионов завершен. Выбранные регионы: {', '.join(region_names)}. Теперь отправьте ссылки в чат.")
        selected_regions[callback.message.chat.id] = user_info['region']
    else:
        await callback.message.edit_text("Выбор регионов завершен, отправьте ссылки для добавления")
        selected_regions[callback.message.chat.id] = user_info['region']
    await callback.answer()
