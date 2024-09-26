import matplotlib.pyplot as plt
import io
import yfinance as yf


def generate_stock_chart(symbol, period='1mo'):
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)

    # Generate chart
    plt.figure(figsize=(10, 5))
    plt.plot(hist.index, hist['Close'], label=symbol.upper())
    plt.title(f"{symbol.upper()} Stock Price ({period})")
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()

    # Save to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf