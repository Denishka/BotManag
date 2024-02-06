from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_factories import RegionCallbackFactory

router = Router()


def get_keyboard_fab(regions):
    builder = InlineKeyboardBuilder()
    for region in regions:
        builder.button(
            text=region[1], callback_data=RegionCallbackFactory(action="select", region=region[0])
        )
    builder.button(
        text="Подтвердить", callback_data=RegionCallbackFactory(action="finish")
    )
    # Выравниваем кнопки по 3 в ряд
    builder.adjust(2)
    return builder.as_markup()


def get_keyboard_fab_2(regions):
    builder = InlineKeyboardBuilder()
    for region in regions:
        builder.button(
            text=region[1], callback_data=RegionCallbackFactory(action="select_one_region", region=region[0])
        )
    builder.button(
        text="Подтвердить", callback_data=RegionCallbackFactory(action="finish2")
    )
    # Выравниваем кнопки по 3 в ряд
    builder.adjust(2)
    return builder.as_markup()



