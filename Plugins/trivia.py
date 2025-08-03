import json
import random
from datetime import datetime, timedelta
from Frontier import bot, users_collection
from Frontier.Helpers.trivia_que import questions
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Store user trivia attempts in a local array
user_trivia_cooldown = {}
COOLDOWN_TIME = 600  # 10 minutes in seconds
MAX_TRIVIA_PER_DAY = 10

# Trivia command
@bot.on_message(filters.command("trivia"))
async def trivia_command(client, message):
    user_id = message.from_user.id

    # Check if the user has to wait before attempting the next trivia
    trivia_last_attempt_time = user_trivia_cooldown.get(user_id, datetime.min)
    trivia_cooldown_time = trivia_last_attempt_time + timedelta(seconds=COOLDOWN_TIME)
    # if datetime.now() < trivia_cooldown_time:
    #     remaining_time = (trivia_cooldown_time - datetime.now()).seconds // 60
    #     return await message.reply_text(f"You need to wait {remaining_time} minutes before playing again.")

    user_data = users_collection.find_one({"user_id": user_id})
    trivia_count = int(user_data.get("trivia_attempted", 0))

    # if trivia_count >= MAX_TRIVIA_PER_DAY:
    #     return await message.reply_text("You have reached your daily trivia limit.")

    try:
        # Get a random trivia question
        trivia_question = random.choice(questions)
        question_text = trivia_question["question"]
        options = trivia_question["options"]
        correct_answer = trivia_question["correct_answer"]
        question_data = question_text.replace(" ","-")

        # Generate a unique identifier for the question
        question_id = str(hash(question_text))

        # Generate inline keyboard with options
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(option, callback_data=f"trivia_{question_data}_{correct_answer}_{option}")]
                for option in options
            ]
        )

        user_trivia_cooldown[user_id] = datetime.now()
        users_collection.update_one({"user_id": user_id}, {"$set": {"trivia_attempted": trivia_count + 1}})

        # Send the trivia question to the user
        await message.reply_text(f"**Question:**\n{question_text}", reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"Try again:\n{e}")


# Callback query handler for trivia answers
@bot.on_callback_query(filters.regex(r"trivia_"))
async def trivia_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")
    question_text = data[1].replace("-", " ")
    correct_answer = data[2]
    selected_option = data[-1]

    # Check if the selected option is correct
    coins_to_award = 100
    if selected_option.lower() == correct_answer.lower():
        # Award some coins for a correct answer
        message_text = f"✅ Correct! You got {coins_to_award} coins."
    else:
        message_text = "❌ Incorrect. Better luck next time!"

    # Edit the trivia question message with the result
    await callback_query.edit_message_text(f"**Question:**\n{question_text}\n\n{message_text}")
