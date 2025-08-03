from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import random
import pytz
import schedule
import time

from Frontier import  users_collection, bot,DEVS,GROUP_ID

# Constants
MIN_BET_PERCENTAGE = 5
DAILY_BET_LIMIT = 20

def get_user_info(user_id):
    return users_collection.find_one({"user_id": user_id})

def update_user_info(user_id, data):
    users_collection.update_one({"user_id": user_id}, {"$set": data}, upsert=True)

@bot.on_message(filters.command("bet"))
async def bet_command(client, message):
    user_id = message.from_user.id
    current_time = datetime.datetime.now()
    user_info = get_user_info(user_id)

    # Check if user reached the daily play limit
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data:
        return await message.reply_text("You are not registered. Please register to play.")

    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Invalid bet amount. \nUsage: /bet <amount>")

    bet_amount = int(message.command[1])
    if bet_amount <= 0:
        return await message.reply_text("Please bet a positive amount.")

    initial_coins = user_info.get("initial_coins", 0)
    current_coins = user_info.get("coins", 0)
    last_bet_time = user_info.get("last_bet_time")
    daily_bet_count = user_info.get("daily_bet_count", 0)

    if bet_amount > current_coins:
        return await message.reply_text(f"You don't have enough coins to place this bet.\nYour Bal: {current_coins}")

    min_bet_required = round((current_coins*MIN_BET_PERCENTAGE)/100)
    if bet_amount < min_bet_required:
        return await message.reply_text(f"You Must have to bet atleast 5% of your coins  ({min_bet_required} coins).")

    if last_bet_time and (current_time - last_bet_time).seconds < 60:
        return await message.reply_text("You have to wait 1 minute between bets.")

    if daily_bet_count >= DAILY_BET_LIMIT:
        return await message.reply_text("You have reached your daily betting limit.")

    bet_outcome = random.choice(["win", "lose"])
    rand_win =  [1.5,2,2.5,3]
    random_win_number   =  random.choice(rand_win)
    if bet_outcome == "win":
        win_amt = bet_amount * random_win_number
        win_amount = round(win_amt,2)
        current_coins += win_amount
        response_text = f"You won! You've gained {win_amount} coins."
    else:
        rand_loss = [0.2,0.4,0.6,0.8]
        random_loss_number = random.choice(rand_loss)
        lose_amount = round(bet_amount * random_loss_number,2)
        current_coins -= lose_amount
        response_text = f"Unfortunately, you lost! You've lost {lose_amount} coins."

    update_user_info(user_id, {
        "coins": current_coins,
        "last_bet_time": current_time,
        "daily_bet_count": daily_bet_count + 1
    })

    await message.reply_text(response_text)