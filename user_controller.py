from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message

import keyboards
from birthday_controller import bot
from database import User, StatusType, save, get_user_by_chat_id, UserStatus, get_current_status_type, \
    delete_current_status


@bot.message_handler(Command("start"))
async def start_conversation(message: Message):
    user = get_user_by_chat_id(message.chat.id)
    if user is None:
        await message.answer(f"Привіт! Як я можу до тебе звертатися?")
        save(User(chat_id=message.chat.id))
        save(UserStatus(user_id=message.chat.id, status_type=StatusType.UpdateUserName.value))
    else:
        await message.answer(f"{user.name}, вибери варіант нижче:", reply_markup=keyboards.get_menu_keyboard())


@bot.message_handler(Text(equals=["Змінити своє ім'я"]))
async def change_name(message: Message):
    save(UserStatus(user_id=message.chat.id, status_type=StatusType.UpdateUserName.value))
    await message.answer(f"Введи нове ім'я", reply_markup=keyboards.cancel_keyboard())


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.UpdateUserName.value)
async def update_user_name(message: Message):
    user = get_user_by_chat_id(message.chat.id)
    user.name = message.text
    save(user)
    delete_current_status(user.chat_id)
    await message.answer(f"Класне ім'я {user.name}, запам'ятаю!", reply_markup=keyboards.get_menu_keyboard())
