from Frontier import users_collection

# Function to get a user's name
async def get_user_name(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return user.get("name", "there")
    return "there"


# Function to add coins to a user's account
async def add_coins(user_id, coins_to_add):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        current_coins = user.get("coins", 0)
        updated_coins = current_coins + coins_to_add
        users_collection.update_one({"user_id": user_id}, {"$set": {"coins": updated_coins}})
        return updated_coins
    return None

# Function to remove coins from a user's account
async def remove_coins(user_id, coins_to_remove):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        current_coins = user.get("coins", 0)
        if current_coins >= coins_to_remove:
            updated_coins = current_coins - coins_to_remove
            users_collection.update_one({"user_id": user_id}, {"$set": {"coins": updated_coins}})
            return updated_coins
        return "Insufficient coins"
    return None

# Function to get a user's total coins
async def get_user_coins(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return user.get("coins", 0)
    return None