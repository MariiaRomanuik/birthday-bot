from datetime import timedelta, date

from aiogram.dispatcher.filters import Text
from aiogram.types import Message

import keyboards
from controller import bot
from database import get_persons_by_user, StatusType, get_current_status_type, save, UserStatus, \
    delete_current_status


@bot.message_handler(Text(equals=["Подивитися дні народження"]))
async def show_data(message: Message):
    save(UserStatus(user_id=message.chat.id, status_type=StatusType.ShowBirthdays.value))
    await message.answer("Вибери варіант нижче", reply_markup=keyboards.get_date_keyboard())


@bot.message_handler(Text(equals=["Сьогодні", "Тиждень", "Місяць", "По категоріях", "Весь рік"]))
async def get_data(message: Message):
    today = date.today()
    persons = get_persons_by_user(message.chat.id)  # тут ми отримали всіх моїх персон
    result_message = ""

    if message.text == "Сьогодні":
        for person in persons:
            if person.birthday.replace(year=today.year) == today:
                result_message += f"\n{person.name} {count_age(person)}\n"

        if result_message:
            await message.answer("Дні народження сьогодні:\n" + result_message + "\nЙди писати привітання!")
        else:
            await message.answer("Ех, сьогодні ні в кого немає дня народження...")
    elif message.text == "Тиждень":
        for person in sorted(persons, key=lambda psn: (psn.birthday.month, psn.birthday.day)):
            if today <= person.birthday.replace(year=today.year) < (today + timedelta(weeks=1)):
                result_message += f"\n{person.name} {person.birthday.day}-го числа {count_age(person)}\n"
        if result_message:
            await message.answer("Дні народження цього тижня:\n" + result_message + "\nПриготуй подаруночок!")
        else:
            await message.answer("Ех, цього тижня немає ні в кого дня народження...")
    elif message.text == "Місяць":
        from_date = today.replace(day=1)
        if today.month == 12:
            to_date = today.replace(day=1, month=1, year=today.year + 1)
        else:
            to_date = today.replace(day=1, month=today.month + 1)
        for person in sorted(persons, key=lambda psn: (psn.birthday.month, psn.birthday.day)):
            if from_date <= person.birthday.replace(year=today.year) < to_date:
                result_message += f"\n{person.name} {person.birthday.day}-го числа {count_age(person)}\n"
        if result_message:
            await message.answer(f"\nДні народження цього місяця:\n" + result_message + "\nПриготуй подаруночок!")
        else:
            await message.answer("Ех, цього місяця немає ні в кого дня народження...")
    elif message.text == "Весь рік":
        months = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
                  "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"]
        grouped_persons = {}

        for person in persons:
            if person.birthday.month not in grouped_persons:
                grouped_persons[person.birthday.month] = []
            grouped_persons[person.birthday.month].append(person)

        for to_date in grouped_persons:
            result_message += f"\n{months[to_date - 1]}\n"
            for person in sorted(grouped_persons[to_date], key=lambda psn: (psn.birthday.month, psn.birthday.day)):
                result_message += f"{person.name} {person.birthday.day}-го числа {count_age(person)}\n"
        if result_message:
            await message.answer(f"Дні народження за рік:\n" + result_message)
        else:
            await message.answer("Немає нічого...")

    elif message.text == "По категоріях":
        grouped_persons = {}

        for person in persons:
            if person.category.type not in grouped_persons:
                grouped_persons[person.category.type] = []
            grouped_persons[person.category.type].append(person)

        for category in grouped_persons:
            result_message += f"\n{category}\n"
            for person in sorted(grouped_persons[category], key=lambda psn: (psn.birthday.month, psn.birthday.day)):
                result_message += f"{person.name} {person.birthday.day:02d}.{person.birthday.month:02d} " \
                                  f"{count_age(person)}\n"
        if result_message:
            await message.answer(f"Дні народження по категоріях:\n" + result_message)
        else:
            await message.answer("Немає нічого...")


def count_age(person):
    year = person.birthday.year
    if year > 1:
        age = date.today().year - year
        last_digit = age % 10
        if 10 < age < 20 or last_digit in [0, 5, 6, 7, 8, 9]:
            return f"({age} років)"
        if last_digit == 1:
            return f"({age} рік)"
        if last_digit in [2, 3, 4]:
            return f"({age} роки)"
    return ""


def format_birthdays(persons):
    result = ""
    for person in persons:
        category_type = ""
        if person.category is not None:
            category_type = person.category.type
        if person.birthday is not None:
            # тут формат дати 01.01 with zero where we need
            result += f"{person.name}  -  {person.birthday.day:02d}.{person.birthday.month:02d}  -  {category_type}\n"
    return result


@bot.message_handler(Text(equals=["Вибрати дату"]))
async def choose_data(message: Message):
    await message.answer("Введи дату у форматі " + date.today().strftime("%d.%m"),
                         reply_markup=keyboards.cancel_keyboard())


@bot.message_handler(lambda message: get_current_status_type(message.chat.id) == StatusType.ShowBirthdays.value)
async def shows_birthdays(message: Message):
    persons = get_persons_by_user(message.chat.id)
    # status = get_current_status_type(message.chat.id)
    result_message = ""
    birthday = message.text.split(".")
    # status.status_type = StatusType.ShowBirthdaysByDate.value
    StatusType.ShowBirthdays.value = StatusType.ShowBirthdaysByDate.value

    try:
        input_day = int(birthday[0])
        input_month = int(birthday[1])
        date(year=int(birthday[2]) if len(birthday) > 2 else 1, month=int(birthday[1]),
             day=int(birthday[0]))

        for person in persons:
            if person.birthday.day == input_day and person.birthday.month == input_month:
                result_message += f"{person.name} {count_age(person)}\n"
                delete_current_status(message.chat.id)

        if result_message:
            await message.answer("Дні народження " f"{message.text}:\n" + result_message + "Готуй привітання!",
                                 reply_markup=keyboards.get_menu_keyboard())
        else:
            await message.answer("Немає людини з днем народження у вибрану дату!\nВведи іншу дату",
                                 reply_markup=keyboards.cancel_keyboard())
    except (IndexError, ValueError):
        await message.answer("Запиши, будь ласка, в правильному форматі дату!")
