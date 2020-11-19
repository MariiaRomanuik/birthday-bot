from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Подивитися дні народження"),
                KeyboardButton(text="Додати особу"),
            ],
            [
                KeyboardButton(text="Редагувати особу"),
                KeyboardButton(text="Змінити своє ім'я")
            ],
        ],
        resize_keyboard=True
    )


def get_date_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сьогодні"),
                KeyboardButton(text="Тиждень"),
            ],
            [
                KeyboardButton(text="Місяць"),
                KeyboardButton(text="Весь рік"),

            ],
            [
                KeyboardButton(text="Вибрати дату"),
                KeyboardButton(text="По категоріях")
            ],
            [
                KeyboardButton(text="Відмінити")
            ],
        ],
        resize_keyboard=True
    )


def get_persons_keyboard(persons):
    return ReplyKeyboardMarkup(
        keyboard=[[person.name] for person in persons] + [["Відмінити"]],
        resize_keyboard=True
    )


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Відмінити")
            ]
        ],
        resize_keyboard=True
    )


def get_edit_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Ім'я"),
                KeyboardButton(text="День народження")
            ],
            [
                KeyboardButton(text="Категорія"),
                KeyboardButton(text="Відмінити")
            ]
        ],
        resize_keyboard=True
    )
