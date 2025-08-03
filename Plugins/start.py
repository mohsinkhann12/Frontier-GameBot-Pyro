from pyrogram import Client, filters,enums
from Frontier import bot
from pyrogram.enums import *

from Frontier import users_collection,bot,GROUP_ID,groups_collection
from Frontier.Database.coins_db import get_user_name

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    chat_type = message.chat.type
    chat_id = message.chat.id
    chat_name = message.chat.title
    user_first_Name = message.from_user.first_name

    if message.chat.type == ChatType.PRIVATE:
        existing_user = users_collection.find_one({"user_id": user_id})
        

        if existing_user:
            user_name = await get_user_name(user_id)
            await message.reply_text(f"""Hello {user_name}! How's your day?\n\nHere are some you can use:\n\n/command1 - Description of command 1\n/command2 - Description of command 2\n\nThis bot is designed to assist you with XYZ.""")
        else:
            user_data = {
                "user_id": user_id,
                "name": message.from_user.first_name,
                "username": message.from_user.username or "",
                "coins": 100,  # Initial coins to be credited
                "guild": ""  # Initial coins to be credited
            }
            users_collection.insert_one(user_data)
            total_users = users_collection.count_documents({})
            await message.reply_text("Registration successful! 100 coins added to your account.")
            user_link = f'<a href="tg://user?id={user_id}">{user_first_Name}</a>'
            NEW_USER_TEXT= f"""
<u><b>#NEW_USER</b></u>

<b>Name:</b> {user_link}
<b>UserID:</b> <code>{user_id}</code>
<b>UserName:</b> @{message.from_user.username or ""}

<b>Now we've {total_users} users...</b>
"""
            await bot.send_message(GROUP_ID,NEW_USER_TEXT,parse_mode=enums.ParseMode.HTML)
    else:
        existing_chat = groups_collection.find_one({"chat_id": chat_id})
        if existing_chat:
            await message.reply_text("I am Alive")

        else:
            chat_data = {
                "chat_id": chat_id,
                "chat_name": chat_name
            }
            groups_collection.insert_one(chat_data)
            total_groups = groups_collection.count_documents({})
            members_count = await client.get_chat_members_count(chat_id)
            NEW_GROUP_TEXT = f"""
<u><b>#NEW_GROUP</b></u>

<b>Name:</b> {chat_name}
<b>ChatID:</b> <code>{chat_id}</code>
<b>Members:</b> {members_count}

<b>Now we've {total_groups} groups...</b>
"""
            await message.reply_text("I am Alive")
            await bot.send_message(GROUP_ID,NEW_GROUP_TEXT,parse_mode=enums.ParseMode.HTML)