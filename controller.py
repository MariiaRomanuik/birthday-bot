from aiogram.dispatcher.filters import Text
from aiogram.types import Message

import keyboards
from config import bot
from database import get_user_by_chat_id, delete_current_status, get_current_status, delete_person_by_id, StatusType


@bot.message_handler(Text(equals=["Відмінити"]))
async def cmd_start(message: Message):
    user = get_user_by_chat_id(message.chat.id)
    status = get_current_status(message.chat.id)
    if status is not None and status.status_type in [StatusType.CreatePersonName.value,
                                                     StatusType.CreatePersonBirthday.value,
                                                     StatusType.CreatePersonCategory.value]:
        delete_person_by_id(status.person_id)
    delete_current_status(message.chat.id)

    await message.answer(f"{user.name}, вибери варіант нижче:", reply_markup=keyboards.get_menu_keyboard())
