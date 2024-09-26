import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import DISCORD_TOKEN
from commands.stock_commands import stock, watchlist_add, watchlist_show, set_alert
from commands.news_commands import daily_news, test_news
from utils.database import init_db

# Enable necessary intents
intents = discord.Intents.default()
intents.message_content = True

# Set up bot with command prefix and intents
bot = commands.Bot(command_prefix='$', intents=intents)

# Initialize database
init_db()

# Register commands
bot.add_command(stock)
bot.add_command(watchlist_add)
bot.add_command(watchlist_show)
bot.add_command(set_alert)
bot.add_command(test_news)

# Scheduler for periodic tasks
scheduler = AsyncIOScheduler()

# Scheduler for news updates at specific times
@scheduler.scheduled_job('cron', hour=17)  # 5 PM
async def news_at_5pm():
    await daily_news()

@scheduler.scheduled_job('cron', hour=18)  # 6 PM
async def news_at_6pm():
    await daily_news()

@scheduler.scheduled_job('cron', hour=20)  # 8 PM
async def news_at_8pm():
    await daily_news()

@scheduler.scheduled_job('cron', hour=22)  # 10 PM
async def news_at_10pm():
    await daily_news()


# Start the scheduler
scheduler.start()

# Run the bot
bot.run(DISCORD_TOKEN)




