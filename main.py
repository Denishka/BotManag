import asyncio
from contextlib import suppress
from typing import Optional
from aiogram import Dispatcher, Bot
from aiogram import F, Router, types
from aiogram import exceptions
from aiogram.enums.chat_type import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_reader import config
from database_manager import init_database, get_connection_to_database, get_all_regions, get_chat_ids, \
    delete_user_from_database, add_user_to_region, insert_user_to_database, get_user_by_username_from_database, \
    get_user_by_id_from_database

bot = Bot(token=config.bot_token.get_secret_value())

router = Router()
dp = Dispatcher()

AUTHORIZED_USERS = [319186657]  # id HR

forwarded_users = {}


def get_region_name_by_id(region_id):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM regions WHERE id = %s", (region_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


class RegionCallbackFactory(CallbackData, prefix="region"):
    action: str
    region: Optional[int] = None


async def update_region_text_fab(message: types.Message, new_regions: list, regions):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"В какие регионы вы хотите добавить пользователя с именем {forwarded_users[319186657]['username']} и ID {forwarded_users[319186657]['user_id']} ? Выбранные регионы:  {', '.join(new_regions)}",
            reply_markup=get_keyboard_fab(regions)
        )


@dp.callback_query(RegionCallbackFactory.filter(F.action == "select"))
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



@dp.callback_query(RegionCallbackFactory.filter(F.action == "finish"))
async def callbacks_region_finish(
        callback: types.CallbackQuery,
        callback_data: RegionCallbackFactory
):
    # Используем user_id, username и выбранные регионы из временного хранилища
    user_info = forwarded_users.get(callback.message.chat.id)
    if user_info is not None and 'regions' in user_info:
        for region in user_info['regions']:
            await add_user_to_region(user_info['user_id'], user_info['username'], region)
        region_names = [get_region_name_by_id(region) for region in user_info['regions']]
        await callback.message.edit_text(
            f"Выбор регионов завершен. Выбранные регионы: {', '.join(region_names)}")
    else:
        await callback.message.edit_text("Выбор регионов завершен.")
    await callback.answer()


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


@dp.message()
async def forward_message(message: types.Message):
    if message.forward_from:
        user_id = message.forward_from.id
        username = message.forward_from.username
        forwarded_users[message.chat.id] = {'user_id': user_id, 'username': username}
        # Получаем список регионов из базы данных
        regions = get_all_regions()
        keyboard = get_keyboard_fab(regions)

        await message.answer(
            f"В какие регионы вы хотите добавить пользователя с именем {username} и ID {user_id} ? Выбранные регионы: ",
            reply_markup=keyboard
        )


@dp.chat_member()
async def new_chat_member(update: types.ChatMemberUpdated):
    if update.new_chat_member.status == 'member':
        user = update.new_chat_member.user
        users = get_user_by_id_from_database(user)
        if not users:
            insert_user_to_database(user)
        await bot.send_message(update.chat.id, f'Привет, {user.full_name}, как дела? Ваш ID: {user.id}')


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type != 'private':
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    else:
        kb = [
            [
                types.KeyboardButton(text="Удалить пользователя"),
            ],
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="выберите одно из действий"
        )
        await message.reply("Выберите действие", reply_markup=keyboard)


@dp.message(F.text.lower() == "удалить пользователя")
async def with_puree(message: types.Message, state: FSMContext):
    if message.chat.type != ChatType.PRIVATE:
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    else:
        await state.set_state(Form.username)
        await message.reply("Напишите username пользователя, которого хотите удалить:")


async def delete_user_from_chats(user, username, message):
    user_id = user[1]
    chat_ids = get_chat_ids()
    for chat_id_tuple in chat_ids:
        chat_id = int(chat_id_tuple[0])
        try:
            await bot.ban_chat_member(chat_id, user_id)
        except exceptions.TelegramBadRequest:
            continue
    delete_user_from_database(user_id)
    await message.answer(f"Пользователь {username} был удален")


class Form(StatesGroup):
    confirm = State()
    username = State()


@dp.message(Form.username)
async def process_username(message: types.Message, state: FSMContext):
    if message.from_user.id not in AUTHORIZED_USERS:
        await bot.send_message(message.from_user.id, "Извините, у вас нет доступа к этой функции.")
    else:
        username = message.text
        user = get_user_by_username_from_database(username)
        if user:
            await state.update_data(name=message.text)
            await state.set_state(Form.confirm)
            await message.answer(
                "Вы действительно хотите удалить пользователя?",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Да"),
                            KeyboardButton(text="Нет"),
                        ]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ),
            )
        else:
            await message.reply(f"Пользователь {username} не найден")
            await state.clear()


@dp.message(Form.confirm, F.text.casefold() == "да")
async def process_like_write_bots(message: types.Message, state: FSMContext):
    dict_inf = await state.get_data()
    username = dict_inf["name"]
    user = get_user_by_username_from_database(username)
    await delete_user_from_chats(user, username, message)
    await message.reply("Пользователь удален!")
    await cmd_start(message)
    await state.clear()


@dp.message(Form.confirm, F.text.casefold() == "нет")
async def process_dont_like_write_bots(message: types.Message, state: FSMContext):
    await message.reply("Вы отказались удалять пользователя")
    await cmd_start(message)
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    init_database()
    asyncio.run(main())
