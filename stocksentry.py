import requests

ALPHA_VANTAGE_API_KEY = 'your_alpha_vantage_api_key'
BASE_URL = 'https://www.alphavantage.co/query'
NEWS_API_KEY = 'your_news_api_key'


def get_stock_price(symbol):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    # Parse and return the latest stock price
    return data['Time Series (1min)']

def get_market_news():
    url = f'https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return articles[:5]  # Return top 5 articles
