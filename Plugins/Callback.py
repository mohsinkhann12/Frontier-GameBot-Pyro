from pyrogram import filters, enums 
from Frontier import bot,users_collection,guilds_collection
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
import random
import string

@bot.on_callback_query(filters.regex(r"^confirm_guild_"))
async def confirm_guild_callback(client, callback_query):
    user_id = callback_query.from_user.id
    guild_name = callback_query.data.split("_", 2)[2]
    
    # Generate a unique guild ID
    guild_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Create a new guild document
    new_guild = {
        "guild_id": guild_id,
        "guild_name": guild_name,
        "guild_owner_id": user_id,
        "guild_members": [user_id],
        "pending_users": [],
        "guild_level": 1,
        "guild_inventory": {}
    }

    try:
        # Insert the new guild document into the guilds collection
        guilds_collection.insert_one(new_guild)
        # Update user collection with guild information
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"guild": guild_name}}
        )
        await callback_query.answer("Guild created successfully!")
        await callback_query.edit_message_text("Guild created successfully!")
    except Exception as err:
        await callback_query.edit_message_text(f"Guild created failed\n{err}")

@bot.on_callback_query(filters.regex(r"^cancel_guild$"))
async def cancel_guild_callback(client, callback_query):
    await callback_query.answer("Guild creation cancelled.")
    await callback_query.edit_message_text("Guild creation cancelled.")

@bot.on_callback_query(filters.regex(r"^accept_"))
async def accept_join_request(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")

    if len(data) != 3:
        await callback_query.answer("Invalid action.")
        return

    guild_id = data[1]
    target_user_id = int(data[2])

    # Check if the callback is initiated by the guild owner
    guild_data = guilds_collection.find_one({"guild_id": guild_id, "guild_owner_id": user_id})
    if not guild_data:
        await callback_query.answer("You are not authorized to interact with this guild's requests.")
        return

    # Remove the user from pending requests and add to guild members
    guilds_collection.update_one(
        {"guild_id": guild_id},
        {"$pull": {"pending_users": target_user_id}, "$push": {"guild_members": target_user_id}}
    )

    # Update the guild status of the user in the user collection
    users_collection.update_one(
        {"user_id": target_user_id},
        {"$set": {"guild": guild_id}}
    )

    # Notify the user about the approval
    user_message = f"Your request to join guild {guild_id} has been approved!"
    await bot.send_message(target_user_id, user_message)

    await callback_query.answer("Request approved.")
    await callback_query.edit_message_text("Request approved.")

@bot.on_callback_query(filters.regex(r"^reject_"))
async def reject_join_request(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")

    if len(data) != 3:
        await callback_query.answer("Invalid action.")
        return

    guild_id = data[1]
    target_user_id = int(data[2])

    # Check if the callback is initiated by the guild owner
    guild_data = guilds_collection.find_one({"guild_id": guild_id, "guild_owner_id": user_id})
    if not guild_data:
        await callback_query.answer("You are not authorized to interact with this guild's requests.")
        return

    # Remove the user from pending requests
    guilds_collection.update_one(
        {"guild_id": guild_id},
        {"$pull": {"pending_users": target_user_id}}
    )

    # Notify the user about the rejection
    user_message = f"Your request to join guild {guild_id} has been rejected."
    await bot.send_message(target_user_id, user_message)

    await callback_query.answer("Request rejected.")
    await callback_query.edit_message_text("Request rejected.")

# Callback queries for guild actions
@bot.on_callback_query(filters.regex(r"confirm_leave_"))
async def confirm_leave_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")
    guild_name = data[2]
    leave_user_id = int(data[3])

    if user_id != leave_user_id:
        return await callback_query.answer("This action is not for you.")

    # Logic for leaving guild
    guilds_collection.update_one(
        {"guild_name": guild_name},
        {"$pull": {"guild_members": leave_user_id}}
    )

    users_collection.update_one(
        {"user_id": leave_user_id},
        {"$unset": {"guild": ""}}
    )

    await callback_query.edit_message_text("You have left the guild successfully.")

@bot.on_callback_query(filters.regex(r"cancel_leave_"))
async def cancel_leave_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")
    guild_name = data[2]

    if str(user_id) != data[3]:
        return await callback_query.answer("This action is not for you.")

    await callback_query.edit_message_text("Operation cancelled.")

# Callback to confirm guild ownership transfer
@bot.on_callback_query(filters.regex(r"transfer_confirm_"))
async def transfer_confirm_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")

    if len(data) != 4:
        return await callback_query.answer("Invalid data format.")

    guild_name = data[1]
    new_owner_id = data[2]

    try:
        guild_data = guilds_collection.find_one({"guild_name": guild_name})

        if guild_data is None:
            print(f"Guild information not found for guild: {guild_name}")
            raise ValueError("Guild information not found.")

        old_owner_id = guild_data.get("guild_owner_id")

        if user_id != old_owner_id:
            return await callback_query.answer("This action is not for you.")

        try:
            new_owner_id = int(new_owner_id)
        except ValueError:
            return await callback_query.answer("Invalid user ID.")

        # Transfer ownership logic
        guilds_collection.update_one(
            {"guild_name": guild_name},
            {"$set": {"guild_owner_id": new_owner_id}}
        )

        # Update messages and inform new owner
        await callback_query.edit_message_text(f"Ownership transferred successfully to user ID: {new_owner_id}.")

        new_owner_message = f"You are now the owner of the guild {guild_name}."
        await client.send_message(new_owner_id, new_owner_message)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        await callback_query.answer(error_message, show_alert=True)
        # Log the error for further investigation
        print(error_message)

# Callback to confirm guild deletion
@bot.on_callback_query(filters.regex(r"delete_guild_"))
async def delete_guild_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")

    if len(data) != 3:
        return await callback_query.answer("Invalid data format.")

    guild_name = data[1]

    try:
        guild_data = guilds_collection.find_one({"guild_name": guild_name})

        if guild_data is None or guild_data.get("guild_owner_id") is None:
            raise ValueError("Guild information not found.")

        # Check if the user is the owner of the guild
        if user_id != guild_data.get("guild_owner_id"):
            return await callback_query.answer("This action is not for you.")

        confirmation_keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Yes", callback_data=f"confirm_delete_guild_{guild_name}")],
                [InlineKeyboardButton("No", callback_data=f"cancel_delete_guild_{guild_name}")]
            ]
        )
        confirmation_text = f"Do you really want to delete the guild {guild_name}?"
        await callback_query.edit_message_text(confirmation_text, reply_markup=confirmation_keyboard)

    except ValueError as ve:
        error_message = f"An error occurred: {str(ve)}"
        await callback_query.answer(error_message, show_alert=True)
        # Log the error for further investigation
        print(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        await callback_query.answer(error_message, show_alert=True)
        # Log the error for further investigation
        print(error_message)

# Callback to confirm guild deletion
@bot.on_callback_query(filters.regex(r"confirm_delete_guild_"))
async def confirm_delete_guild_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")

    if len(data) != 3:
        return await callback_query.answer("Invalid data format.")

    guild_name = data[1]

    try:
        guild_data = guilds_collection.find_one({"guild_name": guild_name})

        if guild_data is None:
            print(f"Guild information not found for guild: {guild_name}")
            raise ValueError("Guild information not found.")

        # Check if the user is the owner of the guild
        if user_id != guild_data.get("guild_owner_id"):
            return await callback_query.answer("This action is not for you.")

        # Delete the guild from the guild collection
        guilds_collection.delete_one({"guild_name": guild_name})

        # Reset guild status for all members
        guild_members = guild_data.get("guild_members", [])
        for member_id in guild_members:
            users_collection.update_one(
                {"user_id": member_id},
                {"$unset": {"guild": ""}}
            )

        # Edit the message to confirm guild deletion
        await callback_query.edit_message_text(f"The guild {guild_name} has been deleted.")

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        await callback_query.answer(error_message, show_alert=True)
        # Log the error for further investigation
        print(error_message)

# Callback to cancel guild deletion
@bot.on_callback_query(filters.regex(r"cancel_delete_guild_"))
async def cancel_delete_guild_callback(client, callback_query):
    await callback_query.edit_message_text("Guild deletion cancelled.")

