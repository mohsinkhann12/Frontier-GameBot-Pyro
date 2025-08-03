from pyrogram import Client, filters
import datetime
import asyncio

from Frontier import users_collection, bot

# Constants
COOLDOWN_TIME = 60  # Cooldown time in seconds
DAILY_LIMIT = 20  # Maximum daily plays

dart_user_cooldown = {}
# MongoDB initialization and collections
# Assuming you have initialized the MongoDB connection as users_collection


@bot.on_message(filters.command("dart"))
async def dart_game(client, message):
    user_id = message.from_user.id

    # Check if user reached the daily play limit
    user_data = users_collection.find_one({"user_id": user_id})
    dart_played = int(user_data.get("dart_count", 0))  # Convert dart_count to int

    if dart_played >= DAILY_LIMIT:
        return await message.reply_text("You have reached your daily play limit.")

    if user_id in dart_user_cooldown:
        cooldown_time = dart_user_cooldown[user_id]
        time_diff = datetime.datetime.now() - cooldown_time
        if time_diff.total_seconds() < COOLDOWN_TIME:
            remaining_time = COOLDOWN_TIME - time_diff.total_seconds()
            return await message.reply_text(
                f"You need to wait {int(remaining_time)} seconds before playing again."
            )

    # Get bet amount from command argument
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Invalid bet amount. Usage: /dart <amount>")

    dart_amount = int(message.command[1])  # Define dart_amount here
    if dart_amount <= 0:
        return await message.reply_text("Please bet a positive amount.")

    # Check if the user has enough coins
    if user_data and user_data.get("coins", 0) < dart_amount:
        return await message.reply_text("You don't have enough coins to place this bet.")

    if dart_played >= DAILY_LIMIT:
        return await message.reply_text("You've reached your daily play limit.")
    # Update the user's play count in the database
    users_collection.update_one({"user_id": user_id}, {"$set": {"dart_count": dart_played + 1}})

    # Roll the dart using send_dart method
    dart_message = await bot.send_dice(chat_id=message.chat.id, emoji="🎯")

    # Get the dart value from the message
    dart_value = dart_message.dice.value

    # Check if the dart value is even or odd
    if dart_value % 2 == 0:  # Even number, user wins
        users_collection.update_one({"user_id": user_id}, {"$inc": {"coins": dart_amount}})
        result_text = f"Your dart hits on red ring! You win {dart_amount} coins."
    else:  # Odd number, user loses
        users_collection.update_one({"user_id": user_id}, {"$inc": {"coins": -dart_amount}})
        result_text = f"Your dart hits on white ring! You lose {dart_amount} coins."

    dart_user_cooldown[user_id] = datetime.datetime.now()
    await asyncio.sleep(4)

    await message.reply_text(result_text)
