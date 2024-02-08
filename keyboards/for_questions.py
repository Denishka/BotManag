from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.callback_factories import RegionCallbackFactory


def get_keyboard_fab(regions):
    builder = InlineKeyboardBuilder()
    for region in regions:
        builder.button(
            text=region[1], callback_data=RegionCallbackFactory(action="select", region=region[0])
        )
    builder.button(
        text="Подтвердить", callback_data=RegionCallbackFactory(action="finish")
    )
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
    builder.adjust(2)
    return builder.as_markup()
