import pyrogram

from Frontier import bot,GROUP_ID

async def run_clients():
    await bot.start()
    await pyrogram.idle()

if __name__ == "__main__":
    bot.loop.run_until_complete(run_clients())