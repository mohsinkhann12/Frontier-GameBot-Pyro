from pyrogram import Client, filters,enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import string
from typing import List, Tuple

from Frontier import bot, users_collection, guilds_collection
guild_creation_data = {}

@bot.on_message(filters.command("new_guild"))
async def create_guild_command(client, message):
    user_id = message.from_user.id
    
    # Check if the user is already in a guild
    user_data = users_collection.find_one({"user_id": user_id})
    if user_data and user_data.get("guild"):
        return await message.reply_text("You are already a member of a guild.")
    
    creation_cost = 500  # Set the guild creation cost
    
    # Check if the user has enough coins to create a guild
    if user_data and user_data.get("coins", 0) >= creation_cost:
        guild_name = message.text.split(" ", 1)[1].strip()  # Extract the guild name from the command
        
        confirmation_text = (
            f"Create a guild '{guild_name}' for {creation_cost} coins?"
            "\nThis action is irreversible."
        )

        confirmation_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Confirm", callback_data=f"confirm_guild_{guild_name}"),
                    InlineKeyboardButton("Cancel", callback_data="cancel_guild")
                ]
            ]
        )

        # Send confirmation message with inline keyboard
        sent_message = await message.reply_text(
            confirmation_text,
            reply_markup=confirmation_keyboard
        )

    else:
        return await message.reply_text("Insufficient coins or you are already in a guild.")


@bot.on_message(filters.command("my_guild"))
async def my_guild_info(client, message):
    user_id = message.from_user.id

    # Check if the user is part of any guild
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data or "guild" not in user_data:
        return await message.reply_text("You are not part of any guild.")

    guild_name = user_data["guild"]

    # Retrievfrom e guild information the guilds collection
    guild_info = guilds_collection.find_one({"guild_name": guild_name})
    if not guild_info:
        return await message.reply_text("Guild information not found.")

    owner_id = guild_info.get("guild_owner_id")
    members = guild_info.get("guild_members", [])
    inventory = guild_info.get("guild_inventory", {})
    guild_level = guild_info.get("guild_level", 1)
    guild_id = guild_info.get("guild_id", 1)
    guild_type = guild_info.get("guild_type", "open")
    guild_coins = guild_info.get("guild_inventory", {}).get("coins", 0)


    owner_info = await bot.get_users(owner_id)
    owner_username = owner_info.username if owner_info.username else owner_info.first_name
    owner_link = f'<a href="tg://user?id={owner_id}">{owner_username}</a>'

    members_info = []
    for member_id in members:
        member = await bot.get_users(member_id)
        member_name = member.username if member.username else member.first_name
        member_link = f'<a href="tg://user?id={member_id}">{member_name}</a>'
        members_info.append(member_name)

    members_list = "\n".join(f"- {member} " for member in members_info)

    info_message = (
        "Your Guild Info:\n\n"
        f"<b>Guild Name:</b> <b>{guild_name}</b>\n"
        f"<b>Guild ID:</b> <code>{guild_id}</code>\n"
        f"<b>Owner:</b> <b>{owner_link}</b>\n"
        f"<b>Members:</b>\n<b>{member_link}</b>\n"
        f"<b>Guild Level:</b> {guild_level}\n"
        f"<b>Guild Type:</b> {guild_type}\n"
        f"<b>Guild Coins:</b> {guild_coins}\n"
    )

    await message.reply_text(info_message, parse_mode=enums.ParseMode.HTML)


# ==================================================================================
@bot.on_message(filters.command("change_guild_type"))
async def change_guild_type(client, message):
    user_id = message.from_user.id

    # Check if the user is the guild owner
    guild_data = guilds_collection.find_one({"guild_owner_id": user_id})
    if not guild_data:
        return await message.reply_text("Only the guild owner can change the guild type.")

    command_parts = message.text.split(" ")
    if len(command_parts) != 2:
        return await message.reply_text("Invalid command usage. Use: /change_guild_type <open/approval/closed>")

    new_guild_type = command_parts[1]

    if new_guild_type not in ["open", "approval", "closed"]:
        return await message.reply_text("Invalid guild type. Available types: open, approval, closed")

    # Update the guild type
    guilds_collection.update_one(
        {"guild_owner_id": user_id},
        {"$set": {"guild_type": new_guild_type}}
    )

    await message.reply_text(f"Guild type updated to {new_guild_type}.")


@bot.on_message(filters.command("join_guild"))
async def join_guild(client, message):
    user_id = message.from_user.id
    command_parts = message.text.split(" ")

    if len(command_parts) != 2:
        return await message.reply_text("Invalid usage. Use: /join_guild <guild_id>")

    guild_id = command_parts[1]

    # Check if the guild exists
    guild_data = guilds_collection.find_one({"guild_id": guild_id})
    if not guild_data:
        return await message.reply_text("Guild not found.")

    guild_type = guild_data.get("guild_type")
    guild_name = guild_data.get("guild_name")

    if guild_type == "open":
        # Add the user directly to the guild members
        guilds_collection.update_one(
            {"guild_id": guild_id},
            {"$push": {"guild_members": user_id}}
        )
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"guild": guild_name}}
        )
        await message.reply_text("You joined the guild successfully!")

    elif guild_type == "approval":
        # Notify the guild owner about the join request with buttons to approve or reject
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Accept", callback_data=f"accept_{guild_id}_{user_id}"),
                    InlineKeyboardButton("Reject", callback_data=f"reject_{guild_id}_{user_id}")
                ]
            ]
        )

        owner_id = guild_data.get("guild_owner_id")
        owner_message = f"User {user_id} wants to join your guild {guild_id}. Approve or reject?"
        await bot.send_message(owner_id, owner_message, reply_markup=keyboard)
        await message.reply_text("Join request sent to the guild owner.")

        # Add the user ID to pending requests
        guilds_collection.update_one(
            {"guild_id": guild_id},
            {"$push": {"pending_users": user_id}}
        )

    elif guild_type == "closed":
        return await message.reply_text("This guild is closed for new members.")

# Leave Guild Command
@bot.on_message(filters.command("leave_guild"))
async def leave_guild_command(client, message):
    user_id = message.from_user.id
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data or not user_data.get("guild"):
        return await message.reply_text("You are not part of any guild.")

    guild_name = user_data.get("guild")
    guild_data = guilds_collection.find_one({"guild_name": guild_name})
    
    # Check if the user is the guild owner
    if user_id == guild_data.get("guild_owner_id"):
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Delete Guild", callback_data=f"delete_guild_{guild_name}"),
                    InlineKeyboardButton("Transfer Ownership", callback_data=f"transfer_{guild_name}")
                ]
            ]
        )
        await message.reply_text("You are the owner of this guild. Choose an action:", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Confirm", callback_data=f"confirm_leave_{guild_name}_{user_id}")],
                [InlineKeyboardButton("Cancel", callback_data=f"cancel_leave_{guild_name}_{user_id}")]
            ]
        )
        await message.reply_text(f"Confirm to leave guild {guild_name}?", reply_markup=keyboard)

# Command to initiate guild transfer
@bot.on_message(filters.command("guild_transfer"))
async def guild_transfer_command(client, message):
    user_id = message.from_user.id
    command_parts = message.text.split()
    
    if len(command_parts) != 2:
        return await message.reply_text("Invalid command usage. Use: /guild_transfer <user_id>")
    
    new_owner_id = int(command_parts[1])

    # Get guild information from the user's data
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data or not user_data.get("guild"):
        return await message.reply_text("You are not part of any guild.")

    guild_name = user_data.get("guild")
    guild_data = guilds_collection.find_one({"guild_name": guild_name})

    if user_id != guild_data.get("guild_owner_id"):
        return await message.reply_text("You are not the owner of this guild.")

    if new_owner_id not in guild_data.get("guild_members", []):
        return await message.reply_text("The provided user is not a member of this guild.")

    new_owner_info = await client.get_users(new_owner_id)
    confirmation_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Yes", callback_data=f"transfer_confirm_{guild_name}_{new_owner_id}")],
            [InlineKeyboardButton("No", callback_data=f"transfer_cancel_{guild_name}")]
        ]
    )
    confirmation_text = (
        f"You really want to transfer the guild ownership of {guild_name} to user {new_owner_info.first_name}?"
    )
    await message.reply_text(
        confirmation_text,
        reply_markup=confirmation_keyboard
    )


# Command to contribute coins to guild inventory
@bot.on_message(filters.command("contribute_coins"))
async def contribute_coins_command(client, message):
    user_id = message.from_user.id
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data or not user_data.get("guild"):
        return await message.reply_text("You are not part of any guild.")

    guild_name = user_data.get("guild")
    guild_data = guilds_collection.find_one({"guild_name": guild_name})

    try:
        # Get the contribution amount from the command arguments
        amount = int(message.command[1])

        if amount < 500:
            return await message.reply_text("Contribution amount must be at least 500 coins.")

        # Update guild inventory with contributed coins
        guilds_collection.update_one(
            {"guild_name": guild_name},
            {"$inc": {"guild_inventory.coins": amount}}
        )
        users_collection.update_one({"user_id": user_id}, {"$inc": {"coins": -amount}})

        # Inform the user about the successful contribution
        await message.reply_text(f"You have contributed {amount} coins to the guild {guild_name}'s inventory.")

    except (ValueError, IndexError):
        # Handle invalid input or missing arguments
        await message.reply_text("Invalid command usage. Use: /contribute_coins <amount>")

@bot.on_message(filters.command("withdraw_coins"))
async def withdraw_coins_command(client, message):
    user_id = message.from_user.id

    # Check if the user is part of any guild
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data or "guild" not in user_data:
        return await message.reply_text("You are not part of any guild.")

    guild_name = user_data["guild"]

    # Retrieve guild information from the guilds collection
    guild_info = guilds_collection.find_one({"guild_name": guild_name})
    if not guild_info:
        return await message.reply_text("Guild information not found.")

    owner_id = guild_info.get("guild_owner_id")

    # Check if the command is used by the guild owner
    if user_id != owner_id:
        return await message.reply_text("You are not the owner of this guild.")

    # Parse the command to get the amount to withdraw
    command_parts = message.text.split()
    if len(command_parts) != 2 or not command_parts[1].isdigit():
        return await message.reply_text("Invalid command usage. Use: /withdraw_coins <amount>")

    amount_to_withdraw = int(command_parts[1])

    # Withdraw coins logic
    guild_coins = guild_info.get("guild_inventory", {}).get("coins", 0)

    if amount_to_withdraw <= 0 or amount_to_withdraw > guild_coins:
        return await message.reply_text("Invalid amount to withdraw.")

    # Update guild inventory
    guilds_collection.update_one(
        {"guild_name": guild_name},
        {"$inc": {"guild_inventory.coins": -amount_to_withdraw}}
    )

    # Add coins to user profile
    users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"coins": amount_to_withdraw}}
    )

    await message.reply_text(f"{amount_to_withdraw} coins successfully withdrawn from the guild inventory.")