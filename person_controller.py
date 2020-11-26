from datetime import date

from aiogram.dispatcher.filters import Text
from aiogram.types import Message

import keyboards
from database import Person, Category, StatusType, save, get_category_by_type, get_current_status_type, UserStatus, \
    delete_current_status, get_current_status, get_persons_by_user, get_person_by_user_and_name
from user_controller import bot


@bot.message_handler(Text(equals=["Додати особу"]))
async def create_person(message: Message):
    new_person = Person(user_id=message.chat.id)
    save(new_person)
    save(UserStatus(user_id=message.chat.id, status_type=StatusType.CreatePersonName.value, person_id=new_person.id))
    await message.answer(f"Введи ім'я", reply_markup=keyboards.cancel_keyboard())


@bot.message_handler(Text(equals=["Редагувати особу"]))
async def edit_person(message: Message):
    save(UserStatus(user_id=message.chat.id, status_type=StatusType.EditPerson.value))
    persons = get_persons_by_user(message.chat.id)
    await message.answer("Вибери особу", reply_markup=keyboards.get_persons_keyboard(persons))


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.EditPerson.value)
async def edit_person_detailed(message: Message):
    status = get_current_status(message.chat.id)
    if status.person is None:
        person_to_edit = get_person_by_user_and_name(message.chat.id, message.text)
        if person_to_edit is not None:
            status.person = person_to_edit
            save(status)
            await message.answer("Що будемо редагувати?", reply_markup=keyboards.get_edit_keyboard())
        else:
            await message.answer("Вибери особу")
    else:
        if message.text == "Ім'я":
            status.status_type = StatusType.EditPersonName.value
            await message.answer(f"Введи нове ім'я", reply_markup=keyboards.cancel_keyboard())
        elif message.text == "День народження":
            status.status_type = StatusType.EditPersonBirthday.value
            await message.answer("Введи дату народження у форматі " + date.today().strftime("%d.%m") + " або " +
                                 date.today().strftime("%d.%m.%Y"), reply_markup=keyboards.cancel_keyboard())
        elif message.text == "Категорія":
            status.status_type = StatusType.EditPersonCategory.value
            await message.answer(f"Введи нову категорію", reply_markup=keyboards.cancel_keyboard())
        save(status)


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.CreatePersonName.value)
async def create_person_name(message):
    person_with_given_name = get_person_by_user_and_name(message.chat.id, message.text)
    if person_with_given_name is None:
        status = get_current_status(message.chat.id)
        status.person.name = message.text
        status.status_type = StatusType.CreatePersonBirthday.value
        save(status)
        await message.answer("Введи дату народження у форматі " + date.today().strftime("%d.%m") + " або " +
                             date.today().strftime("%d.%m.%Y"), reply_markup=keyboards.cancel_keyboard())
    else:
        await message.answer("Ти вже маєш особу з таким ім'ям, обери інше")


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.EditPersonName.value)
async def edit_person_name(message):
    person_with_given_name = get_person_by_user_and_name(message.chat.id, message.text)
    if person_with_given_name is None:
        status = get_current_status(message.chat.id)
        status.person.name = message.text
        save(status.person)
        delete_current_status(message.chat.id)
        await message.answer("Ім'я змінено!", reply_markup=keyboards.get_menu_keyboard())
    else:
        await message.answer("Ти вже маєш особу з таким ім'ям, обери інше")


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.CreatePersonBirthday.value)
async def create_person_birthday(message: Message):
    status = get_current_status(message.chat.id)
    # якщо користувач провильно ввів формат дати, то зберігаємо, якщо ні, просимо записати правильний формат
    birthday = message.text.split(".")
    # розділи текст на список
    # birthday = ["11", "04"] ---- birthday[0] = 11, birthday[1] = 04
    try:
        status.person.birthday = date(year=int(birthday[2]) if len(birthday) > 2 else 1, month=int(birthday[1]),
                                      day=int(birthday[0]))
        status.status_type = StatusType.CreatePersonCategory.value
        save(status)
        await message.answer("Ми розподіляємо людей по категоріях які ти для себе придумаєш, тому введи категорію:",
                             reply_markup=keyboards.cancel_keyboard())
    except (IndexError, ValueError):
        await message.answer("Запиши, будь ласка, в правильному форматі дату!")


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.EditPersonBirthday.value)
async def edit_person_birthday(message: Message):
    status = get_current_status(message.chat.id)
    # якщо користувач провильно ввів формат дати, то зберігаємо, якщо ні, просимо записати правильний формат
    birthday = message.text.split(".")
    try:
        status.person.birthday = date(year=int(birthday[2]) if len(birthday) > 2 else 1, month=int(birthday[1]),
                                      day=int(birthday[0]))
        save(status.person)
        delete_current_status(message.chat.id)
        await message.answer("Дату змінено!", reply_markup=keyboards.get_menu_keyboard())
    except (IndexError, ValueError):
        await message.answer("Запиши, будь ласка, в правильному форматі дату!")


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.CreatePersonCategory.value)
async def create_person_category(message):
    status = get_current_status(message.chat.id)
    category = get_category_by_type(message.text)
    status.person.category = category or Category(type=message.text)
    save(status.person)
    delete_current_status(message.chat.id)
    await message.answer("Особа додана!", reply_markup=keyboards.get_menu_keyboard())


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.EditPersonCategory.value)
async def edit_person_category(message):
    status = get_current_status(message.chat.id)
    category = get_category_by_type(message.text)
    status.person.category = category or Category(type=message.text)
    save(status.person)
    delete_current_status(message.chat.id)
    await message.answer("Категорію змінено!", reply_markup=keyboards.get_menu_keyboard())
