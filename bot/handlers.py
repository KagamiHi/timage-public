from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from bot.application import dp
from bot.constants import WELCOME_TEXT, DONATION_MESSAGE
from users.models import User


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await User.aget_or_create_from_tlg(message.chat.id)

    keyboard = [[KeyboardButton(text="/donate")]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False
    )
    await message.answer(
        text=WELCOME_TEXT, reply_markup=reply_markup, parse_mode=ParseMode.HTML
    )


@dp.message(Command("donate"))
async def donate(message: Message) -> None:
    await message.answer(DONATION_MESSAGE, parse_mode=ParseMode.HTML)
