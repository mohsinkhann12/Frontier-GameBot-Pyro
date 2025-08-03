from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Frontier import users_collection, bot,logging,GROUP_ID

async def ResetData():
    
        try:
            users_collection.update_many({}, {"$set": {"daily_bet_count": 0}})
            users_collection.update_many({}, {"$set": {"last_daily_claim": ""}})
            users_collection.update_many({}, {"$set": {"dart_count": "0"}})
            users_collection.update_many({}, {"$set": {"dice_rolled": "0"}})
            print("Function Executed")
            await bot.send_message(GROUP_ID, "Data Reset Sucessfully")
            
        except Exception as e:
            try:
                await bot.send_message(GROUP_ID, "Data Reset Sucessfully")
                print(f"Error Occured\n{e}")
            except:
                 print(f"Error Occured\n{e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(ResetData, trigger="cron", hour=6, minute=00)
scheduler.start()
