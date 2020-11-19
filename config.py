import logging
import os

from aiogram import Bot, Dispatcher

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format=u'[%(asctime)s]  %(message)s',
    level=logging.INFO
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

bot = Dispatcher(Bot(BOT_TOKEN))
