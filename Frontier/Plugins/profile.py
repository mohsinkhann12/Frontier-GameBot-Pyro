from pyrogram import  filters
from pyrogram.types import  InlineKeyboardButton, InlineKeyboardMarkup
from Frontier.Database.coins_db import get_user_coins
from Frontier import users_collection,bot
from Frontier.Helpers.vars import INTEREST_RATE
import os
import datetime

async def get_user_info(user, already=False):
    if not already:
        user = await bot.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    coins = await get_user_coins(user_id)
    username = user.username
    first_name = user.first_name
    mention = user.mention("Link")
    photo_id = user.photo.big_file_id if user.photo else None
    info_text = f"""
ID: {user_id}
Name: {first_name}
UserName: @{username}
Coins: {coins}
""" 
    return info_text, photo_id


@bot.on_message(filters.command("profile"))
async def info_func(client, message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]
    existing_user = users_collection.find_one({"user_id": user})
    m = await message.reply_text("Processing...")
    try:
        info_text, photo_id = await get_user_info(user)
    except Exception as e:
        print(f"Something Went Wrong {e}")
        return await m.edit("Sorry something Went Wrong Report At @The_Catch_Squad")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Support",url="https://t.me/testBot_Grabber")]
       
    ])

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Start Me in PM First", url=f"https://t.me/{bot.me.username}?start=True")]
        ]
    )

    if photo_id is None:
        return await m.edit(info_text, disable_web_page_preview=True, reply_markup=keyboard)
    elif not existing_user:
        return await m.edit(info_text, disable_web_page_preview=True, reply_markup=reply_markup)

    photo = await bot.download_media(photo_id)
    await message.reply_photo(photo, caption=info_text, reply_markup=keyboard)
    await m.delete()
    os.remove(photo)

reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Start Me in PM First", url=f"https://t.me/{bot.me.username}?start=True")]
        ]
    )

@bot.on_message(filters.command("bal"))
async def bal(client, message):
    user = message.from_user
    user_id = user.id
    user_info = users_collection.find_one({"user_id": user_id})
    existing_user = users_collection.find_one({"user_id": user_id})
    if not existing_user:
        await message.reply_text("Let's Get yourself registered first",reply_markup=reply_markup)
    else:
        coins = await get_user_coins(user_id)
        bank_balance = user_info.get("bank_balance", 0)
        last_interest_date = user_info.get("last_interest_date")
        interest_earned = 0

        if last_interest_date:
            days_passed = (datetime.datetime.now() - last_interest_date).days
            interest_earned = bank_balance * INTEREST_RATE * days_passed
        await message.reply_text(f"""
Your Balance: {coins}
In Bank: {bank_balance}
Interest Earned: {interest_earned} ({INTEREST_RATE}%)
""")
