from aiogram import Bot
from aiogram import Router, types

from database_manager import get_invite_links_for_user

router = Router()


@router.callback_query(lambda c: c.data == 'get_links')
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    links = get_invite_links_for_user(user_id)
    text = "\n".join(links)
    await bot.send_message(callback_query.from_user.id, text)
