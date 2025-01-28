import asyncio
import random
import string
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


from config import (
    ADMINS, START_MSG, IS_VERIFY, VERIFY_EXPIRE, SHORTLINK_URL, SHORTLINK_API, TUT_VID
)
from helper_func import get_verify_status, update_verify_status, get_shortlink, get_exp_time
from database import add_user, present_user

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#Add This Code In Start COMMAND And Everywhere Else Where You Want Shortner 
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text

    # Check if the user is in the ADMINS list
    if user_id in ADMINS:
        await message.reply(f"Welcome, Admin {message.from_user.first_name}!\nYou have full access to the bot.")
        return  # No need for verification

    # Check if the message contains a verification token
    if len(text.split()) > 1 and text.split()[1].startswith("verify_"):
        token = text.split()[1].split("_", 1)[1]  # Extract the token after "verify_"
        
        verify_status = await get_verify_status(user_id)
        if verify_status['verify_token'] == token:
            await update_verify_status(user_id, is_verified=True, verified_time=time.time())
            await message.reply("Verification successful! You can now use the bot.")
        else:
            await message.reply("Invalid or expired token. Please try again.")
        return

    # Continue with the normal /start logic if no token
    if not await present_user(user_id):
        await add_user(user_id)

    # Fetch verification status
    verify_status = await get_verify_status(user_id)

    # Check if the verification token has expired
    if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
        await update_verify_status(user_id, is_verified=False)

    # If the user is verified, allow access
    if verify_status['is_verified']:
        await message.reply(START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            id=message.from_user.id
        ))
    # If the user is not verified, send the verification link
    else:
        if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(user_id, verify_token=token)

            # Get bot's username using get_me()
            bot_info = await client.get_me()
            bot_username = bot_info.username

            short_url = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{bot_username}?start=verify_{token}')
            btn = [
                [InlineKeyboardButton("Verify Here", url=short_url)],
                [InlineKeyboardButton('How to use the bot', url=TUT_VID)]
            ]
            await message.reply(f"Please verify yourself to use the bot.\nToken will expire in {get_exp_time(VERIFY_EXPIRE)}.", reply_markup=InlineKeyboardMarkup(btn))

# Verification handler
#Must  Add This Code In Start COMMAND
async def verify_command(client: Client, message: Message):
    user_id = message.from_user.id
    token = message.text.split("_", 1)[1]  # Extract the token part after "verify_"
    
    verify_status = await get_verify_status(user_id)
    if verify_status['verify_token'] == token:
        await update_verify_status(user_id, is_verified=True, verified_time=time.time())
        await message.reply("Verification successful! You can now use the bot.")
    else:
        await message.reply("Invalid or expired token. Please try again.")

