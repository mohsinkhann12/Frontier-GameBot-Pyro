import datetime
from pyrogram import filters

from Frontier import bot,users_collection

# Constants
RESET_HOUR = 6  # Reset daily claim status at 6 AM

@bot.on_message(filters.command("daily"))
async def daily_command(client, message):
    user_id = message.from_user.id
    current_time = datetime.datetime.now()
    user_info = users_collection.find_one({"user_id": user_id})

    if not user_info:
        return await message.reply_text("You are not registered. Please register to claim your daily reward.")

    last_claim_time = user_info.get("last_daily_claim")

    if last_claim_time and (current_time - last_claim_time).days < 1:
        return await message.reply_text("You've already claimed your daily reward today.")

    # Give coins for daily claim
    coins_reward = 100  # Change this value to the desired reward amount
    users_collection.update_one({"user_id": user_id}, {"$set": {"coins": user_info.get("coins", 0) + coins_reward, "last_daily_claim": current_time}})
    await message.reply_text(f"You've claimed your daily reward of {coins_reward} coins.")

