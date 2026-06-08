import os
import yfinance as yf
import asyncio
from dotenv import load_dotenv
from telegram import Bot
import schedule
import time

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(close):
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd, signal

def analyze(ticker: str) -> str:
    data = yf.Ticker(ticker).history(period="3mo")
    close = data["Close"]
    rsi = calculate_rsi(close).iloc[-1]
    macd, signal = calculate_macd(close)
    ma7 = close.rolling(7).mean().iloc[-1]
    price = close.iloc[-1]
    macd_now = macd.iloc[-1]
    signal_now = signal.iloc[-1]
    bullish = sum([macd_now > signal_now, rsi < 70, price > ma7])
    bearish = sum([macd_now < signal_now, rsi > 30, price < ma7])
    if bullish == 3:
        action = "🟢 ПОКУПАТЬ"
    elif bearish == 3:
        action = "🔴 ПРОДАВАТЬ"
    else:
        action = "🟡 ЖДАТЬ"
    return f"""
📊 *{ticker} — Анализ*
💵 Цена: ${price:.2f}
📈 RSI: {rsi:.1f}
📉 MACD: {macd_now:.3f}
〰️ Signal: {signal_now:.3f}
*Итог: {action}*
"""

async def send_signal(tickers: list):
    bot = Bot(token=TOKEN)
    for ticker in tickers:
        message = analyze(ticker)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        print(f"Отправил сигнал для {ticker}")

def run():
    asyncio.run(send_signal(TICKERS))

TICKERS = ["AAPL", "TSLA", "GOOGL", "BTC-USD"]

# Сразу отправить при запуске
run()

# Потом каждый час
schedule.every(1).hours.do(run)

print("Бот запущен — проверяю каждый час...")
while True:
    schedule.run_pending()
    time.sleep(60)