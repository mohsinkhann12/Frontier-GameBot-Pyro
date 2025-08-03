from pyrogram import filters
import datetime
from Frontier import bot,users_collection
from Frontier.Helpers.vars import INTEREST_RATE


# Constants


@bot.on_message(filters.command("deposit"))
async def deposit_command(client, message):
    user_id = message.from_user.id
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Invalid deposit amount. Usage: /deposit <amount>")

    deposit_amount = int(message.command[1])
    if deposit_amount <= 0:
        return await message.reply_text("Please deposit a positive amount.")

    user_info = users_collection.find_one({"user_id": user_id})
    if not user_info:
        return await message.reply_text("You are not registered. Please register to use the bank.")

    current_coins = user_info.get("coins", 0)
    if deposit_amount > current_coins:
        return await message.reply_text("You don't have enough coins to deposit this amount.")

    bank_balance = user_info.get("bank_balance", 0)
    bank_balance += deposit_amount
    current_coins -= deposit_amount

    users_collection.update_one({"user_id": user_id}, {"$set": {"coins": current_coins, "bank_balance": bank_balance}})
    await message.reply_text(f"You've deposited {deposit_amount} coins into the bank.")

@bot.on_message(filters.command("withdraw"))
async def withdraw_command(client, message):
    user_id = message.from_user.id
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Invalid withdraw amount. Usage: /withdraw <amount>")

    withdraw_amount = int(message.command[1])
    if withdraw_amount <= 0:
        return await message.reply_text("Please withdraw a positive amount.")

    user_info = users_collection.find_one({"user_id": user_id})
    if not user_info:
        return await message.reply_text("You are not registered. Please register to use the bank.")

    bank_balance = user_info.get("bank_balance", 0)
    if withdraw_amount > bank_balance:
        return await message.reply_text("You don't have enough balance in the bank to withdraw this amount.")

    current_coins = user_info.get("coins", 0)
    current_coins += withdraw_amount
    bank_balance -= withdraw_amount

    users_collection.update_one({"user_id": user_id}, {"$set": {"coins": current_coins, "bank_balance": bank_balance}})
    await message.reply_text(f"You've withdrawn {withdraw_amount} coins from the bank.")

@bot.on_message(filters.command("checkbank"))
async def check_bank(client, message):
    user_id = message.from_user.id
    user_info = users_collection.find_one({"user_id": user_id})
    if not user_info:
        return await message.reply_text("You are not registered. Please register to use the bank.")

    bank_balance = user_info.get("bank_balance", 0)
    last_interest_date = user_info.get("last_interest_date")
    interest_earned = 0

    if last_interest_date:
        days_passed = (datetime.datetime.now() - last_interest_date).days
        interest_earned = bank_balance * INTEREST_RATE * days_passed

    await message.reply_text(f"Bank Balance: {bank_balance}\nInterest Earned: {interest_earned} coins")
