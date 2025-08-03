from pyrogram import  filters,enums
from pyrogram.types import  InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
from Frontier import bot,users_collection,DEVS


@bot.on_message(filters.command("add_coins") & filters.user(DEVS))
async def add_coins(client, message):
    if len(message.command) != 3 or not message.command[1].isdigit() or not message.command[2].isdigit():
        return await message.reply_text("Invalid command. Usage: /add_coins <amount> <user_id>")

    amount = int(message.command[1])
    user_id = int(message.command[2])

    # Fetch user data
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        return await message.reply_text("User not found.")

    # Confirm action via callback button
    confirmation_message = await bot.send_message(
        chat_id=message.chat.id,
        text=f"Are you sure you want to add {amount} coins to {user_id}?",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirm", callback_data=f"confirm_{amount}_{user_id}"),
                                            InlineKeyboardButton("Reject", callback_data="reject")]])
    )
    await asyncio.sleep(5)  # Adjust this delay as needed

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=confirmation_message.message_id,
        text=f"Add {amount} coins to {user_id}? This message is no longer active.",
    )

@bot.on_callback_query(filters.regex(r"^confirm_(\d+)_(\d+)$") & filters.user(DEVS))
async def confirm_add_coins(client, callback_query):
    amount, user_id = map(int, callback_query.data.split("_")[1:])
    
    # Update user's coins
    users_collection.update_one({"user_id": user_id}, {"$inc": {"coins": amount}})
    
    await callback_query.answer("Coins added successfully.")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"{amount} coins added to user ID: {user_id}. This message is no longer active.",
    )

@bot.on_callback_query(filters.regex(r"^reject$") & filters.user(DEVS))
async def reject_add_coins(client, callback_query):
    await callback_query.answer("Action rejected.")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="Action rejected. This message is no longer active.",
    )