from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.callback_factories import RegionCallbackFactory


def get_keyboard_fab(regions, action="select", finish_action="finish"):
    builder = InlineKeyboardBuilder()
    for region in regions:
        builder.button(
            text=region[1], callback_data=RegionCallbackFactory(action=action, region=region[0])
        )
    builder.button(
        text="Подтвердить", callback_data=RegionCallbackFactory(action=finish_action)
    )
    builder.adjust(2)
    return builder.as_markup()

