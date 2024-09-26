import discord
from discord.ext import commands
from utils.database import get_db_connection
from utils.charts import generate_stock_chart
from utils.helpers import send_message_in_chunks
import yfinance as yf
import discord
from discord import File

# Command to get the stock price
@commands.command()
async def stock(ctx, symbol: str):
    price = get_stock_price(symbol)
    if price:
        await ctx.send(f"The current price of {symbol.upper()} is ${price}")
    else:
        await ctx.send(f"Could not retrieve stock data for {symbol.upper()}.")

# Command to add a stock to the user's watchlist
@commands.command()
async def watchlist_add(ctx, symbol: str):
    user_id = str(ctx.author.id)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO watchlists (user_id, symbol) VALUES (?, ?)', (user_id, symbol.upper()))
    conn.commit()
    conn.close()
    await ctx.send(f"{symbol.upper()} has been added to your watchlist.")

# Command to view the user's watchlist with more details and interactive charts
@commands.command()
async def watchlist_show(ctx):
    user_id = str(ctx.author.id)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT symbol FROM watchlists WHERE user_id = ?', (user_id,))
    watchlist = c.fetchall()
    conn.close()

    if not watchlist:
        await ctx.send("Your watchlist is empty.")
        return

    for symbol in watchlist:
        stock = yf.Ticker(symbol[0])
        stock_info = stock.history(period='1d')

        # Ensure there are enough data points to calculate the percentage change
        if len(stock_info) > 1:
            price = stock_info['Close'][0]
            previous_close = stock_info['Close'][-2]
            percent_change = ((price - previous_close) / previous_close) * 100
        else:
            price = stock_info['Close'][0]
            percent_change = 0  # Set percent change to 0 if there's no previous data point

        volume = stock_info['Volume'][0] if 'Volume' in stock_info.columns else 'N/A'

        # Send formatted stock details
        stock_details = (f"**{symbol[0].upper()}**\n"
                         f"Price: ${price:.2f}\n"
                         f"Change: {percent_change:.2f}%\n"
                         f"Volume: {volume}")
        await ctx.send(stock_details)

        # Generate the stock chart (1 month by default)
        chart_image = generate_stock_chart(symbol[0], '1mo')
        message = await ctx.send(file=File(chart_image, f"{symbol[0]}_1mo.png"))

        # Add reaction emojis for timeframes
        timeframes = {
            '📅': '1d',  # 1 day
            '🗓️': '1wk',  # 1 week
            '📆': '1mo',  # 1 month
            '📈': '1y',   # 1 year
        }
        for emoji in timeframes:
            await message.add_reaction(emoji)

        # Reaction listener for switching timeframes
        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in timeframes

        while True:
            try:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)
                selected_timeframe = timeframes[str(reaction.emoji)]

                # Generate new chart based on selected timeframe
                new_chart_image = generate_stock_chart(symbol[0], selected_timeframe)

                # Send the updated chart
                await message.delete()  # Delete the old message and chart
                new_message = await ctx.send(file=File(new_chart_image, f"{symbol[0]}_{selected_timeframe}.png"))

                # Re-add the reaction emojis to the new message
                for emoji in timeframes:
                    await new_message.add_reaction(emoji)

                message = new_message  # Update the message object to the new one

            except Exception as e:
                print(f"Error in reaction handling: {e}")
                break


# Command to set a price alert
@commands.command()
async def set_alert(ctx, symbol: str, price: float, direction: str):
    user_id = str(ctx.author.id)
    if direction.lower() not in ['above', 'below']:
        await ctx.send("Please specify direction as either 'above' or 'below'.")
        return

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO alerts (user_id, symbol, target_price, direction) VALUES (?, ?, ?, ?)', 
              (user_id, symbol.upper(), price, direction.lower()))
    conn.commit()
    conn.close()
    await ctx.send(f"Alert set for {symbol.upper()} to notify you when the price goes {direction} ${price}.")

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        latest_price = stock.history(period="1d")['Close'][0]
        return round(latest_price, 2)
    except Exception as e:
        print(f"Error fetching data from Yahoo Finance: {e}")
        return None
