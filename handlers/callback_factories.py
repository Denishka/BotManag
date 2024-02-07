from typing import Optional

from aiogram.filters.callback_data import CallbackData


class RegionCallbackFactory(CallbackData, prefix="region"):
    action: str
    region: Optional[int] = None
