import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot import api

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('aiogram')

load_dotenv()

API_TOKEN = os.getenv("Telegram_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
