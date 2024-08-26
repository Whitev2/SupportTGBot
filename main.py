import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery


API_TOKEN = '7516642839:AAGdJf-My3DAvOt9Ab_mcoKDou6w-ERpWIg'
SUPPORT_CHAT_ID = '-4552814838'

logging.basicConfig(level=logging.INFO)

# Initializing the bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Class for handling callback data
class ConfirmPaymentCallback(CallbackData, prefix="confirm"):
    user_id: int
    message_id: int  # Adding field to store message_id


# Handling the /start command
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Hello! Please send a photo with payment confirmation.")


# Handling the receipt of a photo from the user
@dp.message(lambda message: message.photo)
async def handle_payment_photo(message: Message):
    # Sending the photo to the support group with an inline "Confirm" button
    photo = message.photo[-1]  # Take the photo in maximum quality

    keyboard = InlineKeyboardBuilder()
    callback_data = ConfirmPaymentCallback(user_id=message.from_user.id, message_id=message.message_id)
    keyboard.button(text="Confirm", callback_data=callback_data.pack())

    await bot.send_photo(SUPPORT_CHAT_ID, photo.file_id,
                         caption=f"User @{message.from_user.username} sent a payment confirmation.",
                         reply_markup=keyboard.as_markup())

    await message.answer("The photo has been sent for review. Please wait for confirmation.")


# Handling the pressing of the "Confirm" button
@dp.callback_query(ConfirmPaymentCallback.filter())
async def confirm_payment(callback_query: CallbackQuery, callback_data: ConfirmPaymentCallback):
    # Extracting user_id and message_id from callback_data
    user_id = callback_data.user_id
    message_id = callback_data.message_id

    # Sending confirmation message to the user
    try:
        # Replying to the user's photo message
        await bot.send_message(chat_id=user_id, text="Your transaction has been confirmed!", reply_to_message_id=message_id)

        # Removing the button after confirmation
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=None  # Removing buttons
        )

        await callback_query.answer("Transaction confirmed.", show_alert=True)
    except Exception as e:
        logging.error(f"Error sending confirmation to the user: {e}")
        await callback_query.answer("Error: Failed to send confirmation to the user.", show_alert=True)


async def main():
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
