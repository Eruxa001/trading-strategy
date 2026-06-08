import yfinance as yf

data = yf.download("TSLA", start="2026-04-08", end="2026-06-08")
Current_price = yf.Ticker("TSLA").info['currentPrice']
Maximum_price = data["High"].max().values[0]
Minimum_price = data["Low"].min().values[0]
Change_percentage = (Current_price - Minimum_price) / Minimum_price * 100

print(f"Текущая цена: {Current_price}")
print(f"Максимальная цена за период: {Maximum_price}")
print(f"Минимальная цена за период: {Minimum_price}")
print(f"Изменение в процентах: {Change_percentage:.2f}%")