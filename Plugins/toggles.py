from Frontier import bot,users_collection,DEVS
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton,  CallbackQuery

@bot.on_message(filters.command("reset_daily_bet")& filters.user(DEVS))
async def reset_daily_bet_count(_, message):
    confirmation_text = "Are you Sure to reset Today's bet count of all users?"
    confirmation_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes✅", callback_data="confirm_reset_daily_bet_count"),
            InlineKeyboardButton("No❌", callback_data="cancel_reset_daily_bet_count")
        ]
    ])
    await message.reply_text(confirmation_text, reply_markup=confirmation_keyboard)

@bot.on_callback_query(filters.regex("^confirm_reset_daily_bet_count$"))
async def confirm_reset_daily_bet_count(_, query: CallbackQuery):
    if query.from_user.id in DEVS:
        users_collection.update_many({}, {"$set": {"daily_bet_count": 0}})
        await query.edit_message_text("Bet count reset for all users.")
    else:
        await query.answer("You are not authorized to perform this action.")

@bot.on_callback_query(filters.regex("^cancel_reset_daily_bet_count$"))
async def cancel_reset_daily_bet_count(_, query: CallbackQuery):
    await query.edit_message_text("Canceled reseting all user's exchange limit")
