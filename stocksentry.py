import discord
from discord.ext import commands
import sqlite3
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Discord bot token (replace with your bot's token)
DISCORD_TOKEN = 'your_discord_bot_token'

# Alpha Vantage and NewsAPI keys
ALPHA_VANTAGE_API_KEY = 'your_alpha_vantage_api_key'
NEWS_API_KEY = 'your_news_api_key'

# Set up bot with a command prefix
bot = commands.Bot(command_prefix='/')

# SQLite setup to store user watchlists
conn = sqlite3.connect('watchlists.db')
c = conn.cursor()

# Create the watchlist table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS watchlists (
        user_id TEXT,
        symbol TEXT
    )
''')
conn.commit()

# Helper function to get the stock price from Alpha Vantage
def get_stock_price(symbol):
    BASE_URL = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    try:
        latest_time = list(data['Time Series (1min)'].keys())[0]
        latest_price = data['Time Series (1min)'][latest_time]['4. close']
        return latest_price
    except KeyError:
        return None

# Helper function to get market news from NewsAPI
def get_market_news():
    url = f'https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return articles[:5]  # Return top 5 articles

# Command to get the stock price
@bot.command()
async def stock(ctx, symbol: str):
    price = get_stock_price(symbol)
    if price:
        await ctx.send(f"The current price of {symbol.upper()} is ${price}")
    else:
        await ctx.send(f"Could not retrieve stock data for {symbol.upper()}.")

# Command to add a stock to the user's watchlist
@bot.command()
async def watchlist_add(ctx, symbol: str):
    user_id = str(ctx.author.id)
    c.execute('INSERT INTO watchlists (user_id, symbol) VALUES (?, ?)', (user_id, symbol.upper()))
    conn.commit()
    await ctx.send(f"{symbol.upper()} has been added to your watchlist.")

# Command to view the user's watchlist
@bot.command()
async def watchlist_show(ctx):
    user_id = str(ctx.author.id)
    c.execute('SELECT symbol FROM watchlists WHERE user_id = ?', (user_id,))
    watchlist = c.fetchall()
    
    if watchlist:
        watchlist_symbols = ', '.join([item[0] for item in watchlist])
        await ctx.send(f"Your watchlist: {watchlist_symbols}")
    else:
        await ctx.send("Your watchlist is empty.")

# Set up the scheduler for daily updates
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=8)  # Runs daily at 8 AM
async def daily_news():
    channel = bot.get_channel(your_channel_id)  # Replace with your Discord channel ID
    news = get_market_news()
    
    if news:
        news_summary = "\n".join([f"**{article['title']}** - {article['source']['name']}\n{article['url']}" for article in news])
        await channel.send(f"**Daily Market News:**\n{news_summary}")
    else:
        await channel.send("No news available today.")

scheduler.start()

# Run the bot
bot.run(DISCORD_TOKEN)

