from pyrogram import filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import asyncio

from Frontier import bot,users_collection

# Initialize APScheduler for daily resets
scheduler = AsyncIOScheduler()

# Local dictionary to store user cooldowns
dice_user_cooldown = {}

# Constants
MAX_PLAY_COUNT = 20
COOLDOWN_TIME_SECONDS = 60
DAILY_RESET_HOUR = 6
MIN_BET_PERCENTAGE=5

@bot.on_message(filters.command("dice"))
async def dice_game(client, message):
    user_id = message.from_user.id

    # Check if user reached the daily play limit
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        return await message.reply_text("You are not registered. Please register to play.")
    
    # Convert 'dice_rolled' field to integer or initialize to 0 if not present
    dice_rolled_count = int(user_data.get("dice_rolled", 0))

    if dice_rolled_count >= MAX_PLAY_COUNT:
        return await message.reply_text("You have reached your daily play limit.")

    
    # Check user cooldown
    last_play_time = dice_user_cooldown.get(user_id)
    if last_play_time and (datetime.datetime.now() - last_play_time).seconds < COOLDOWN_TIME_SECONDS:
        return await message.reply_text("Please wait 1 min before playing again.")
    
    # Get bet amount from command argument
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Invalid bet amount. Usage: /dice <amount>")
    
    bet_amount = int(message.command[1])
    if bet_amount <= 0:
        return await message.reply_text("Please bet a positive amount.")
    
    current_coins = user_data.get("coins", 0)
    min_bet_required = round((current_coins * MIN_BET_PERCENTAGE) / 100)
    if bet_amount < min_bet_required:
        return await message.reply_text(f"You must bet at least 5% of your coins ({min_bet_required} coins).")

    # Check if the user has enough coins
    if user_data and user_data.get("coins", 0) < bet_amount:
        return await message.reply_text("You don't have enough coins to place this bet.")
    
    # Update the user's play count in the database
    users_collection.update_one({"user_id": user_id}, {"$set": {"dice_rolled": dice_rolled_count + 1}})

    
    # Roll the dice using send_dice method
    dice_message = await bot.send_dice(chat_id=message.chat.id, emoji="🎲")
    
    # Get the dice value from the message
    dice_value = dice_message.dice.value
    
    # Check if the dice value is even or odd
    if dice_value % 2 == 0:  # Even number, user wins
        users_collection.update_one({"user_id": user_id}, {"$inc": {"coins": bet_amount}})
        result_text = f"You rolled an even number! You win {bet_amount} coins."
    else:  # Odd number, user loses
        users_collection.update_one({"user_id": user_id}, {"$inc": {"coins": -bet_amount}})
        result_text = f"You rolled an odd number! You lose {bet_amount} coins."

    dice_user_cooldown[user_id] = datetime.datetime.now()
    await asyncio.sleep(4)

    await message.reply_text(result_text)