from aiogram import Bot
from aiogram import Bot
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from database_manager import get_invite_links_for_user

router=Router()


@router.message(F.text.lower() == "получить ссылки")
async def with_puree(message: types.Message, state: FSMContext,bot: Bot):
    result = get_invite_links_for_user(message.from_user.id)
    if result:
        result_text = "\n".join(result)
        await bot.send_message(message.from_user.id, result_text)
    else:
        await bot.send_message(message.from_user.id, "Извините, ссылок для вас не найдено.")
