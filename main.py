from aiogram import executor

if __name__ == "__main__":
    from person_controller import bot

    executor.start_polling(bot)
