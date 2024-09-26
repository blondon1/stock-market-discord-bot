import discord
from discord.ext import commands
from utils.translation import translate_to_spanish
from utils.helpers import send_message_in_chunks
from config import CHANNEL_ID, NEWS_API_KEY
import requests

@commands.command()
async def test_news(ctx):
    await daily_news(ctx.channel)
    await ctx.send("Noticias de el día.")

# Function to fetch and send daily news
async def daily_news(channel=None):
    if channel is None:
        channel = bot.get_channel(CHANNEL_ID)

    news = get_market_news()
    if news:
        news_summary = "\n".join([
            f"**{translate_to_spanish(article.get('title', 'No Title'))}** - {translate_to_spanish(article.get('source', {}).get('name', 'Unknown Source'))}\n{article['url']}"
            for article in news
        ])
        await send_message_in_chunks(channel, f"**Noticias del Mercado Diario:**\n{news_summary}")
    else:
        await channel.send("No hay noticias disponibles hoy.")

def get_market_news():
    url = f'https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=10&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return articles[:20]
