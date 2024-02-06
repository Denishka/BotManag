from aiogram import types
from aiogram.filters import Filter

from database_manager import get_all_regions


class RegionFilter(Filter):
    async def check(self, message: types.Message):
        return message.text.lower() in get_all_regions()

    async def __call__(self, message: types.Message):
        return await self.check(message)