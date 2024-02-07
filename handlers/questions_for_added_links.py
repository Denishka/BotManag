from contextlib import suppress
from contextlib import suppress

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest

from database_manager import get_all_regions, add_links_to_database
from filters.changing_regions import RegionFilter
from handlers.questions_for_added_users import selected_regions
from keyboards.for_questions import get_keyboard_fab_2

region = []

region_filter = RegionFilter()
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
