"""
Trading Strategy Analyzer
Автор: [твоё имя]
Описание: Алгоритмическая торговая стратегия на основе RSI, MACD и скользящих средних
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TradingStrategy:
    """Торговая стратегия с теханализом и бэктестингом"""

    def __init__(self, ticker: str, period: str = "2y", stop_loss: float = 0.05, take_profit: float = 0.15):
        self.ticker = ticker
        self.period = period
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.data = None
        self.trades = []
        self.portfolio = []

    def load_data(self):
        """Загрузка исторических данных"""
        print(f"Загружаю данные для {self.ticker}...")
        self.data = yf.Ticker(self.ticker).history(period=self.period)
        print(f"Загружено {len(self.data)} дней")
        return self

    def calculate_indicators(self):
        """Расчёт технических индикаторов"""
        close = self.data["Close"]

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        self.data["RSI"] = 100 - (100 / (1 + gain / loss))

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        self.data["MACD"] = ema12 - ema26
        self.data["MACD_Signal"] = self.data["MACD"].ewm(span=9).mean()

        # Скользящая средняя
        self.data["MA7"] = close.rolling(7).mean()

        # Сигналы
        self.data["Bull"] = (
            (self.data["MACD"] > self.data["MACD_Signal"]) &
            (self.data["RSI"] < 70) &
            (close > self.data["MA7"])
        ).astype(int)

        self.data["Bear"] = (
            (self.data["MACD"] < self.data["MACD_Signal"]) &
            (self.data["RSI"] > 30) &
            (close < self.data["MA7"])
        ).astype(int)

        return self

    def run_backtest(self, capital: float = 10000):
        """Бэктестинг стратегии"""
        self.initial_capital = capital
        self.trades = []
        self.portfolio = []
        position = 0
        entry_price = 0

        for i in range(1, len(self.data)):
            row = self.data.iloc[i]
            price = row["Close"]
            reason = None

            if position > 0:
                change = (price - entry_price) / entry_price
                if change <= -self.stop_loss:
                    reason = "STOP-LOSS"
                elif change >= self.take_profit:
                    reason = "TAKE-PROFIT"
                elif row["Bear"] == 1:
                    reason = "СИГНАЛ"

                if reason:
                    capital = position * price
                    self.trades.append({
                        "date": self.data.index[i],
                        "type": "SELL",
                        "price": price,
                        "profit": round(change * 100, 2),
                        "reason": reason
                    })
                    position = 0

            if row["Bull"] == 1 and position == 0:
                position = capital / price
                entry_price = price
                self.trades.append({
                    "date": self.data.index[i],
                    "type": "BUY",
                    "price": price,
                    "reason": "СИГНАЛ"
                })

            self.portfolio.append({
                "date": self.data.index[i],
                "value": position * price if position > 0 else capital
            })

        self.final_capital = capital if position == 0 else position * self.data["Close"].iloc[-1]
        return self

    def get_stats(self) -> dict:
        """Статистика стратегии"""
        sells = [t for t in self.trades if t["type"] == "SELL"]
        wins = [t for t in sells if t["profit"] > 0]
        total_return = ((self.final_capital - self.initial_capital) / self.initial_capital) * 100
        winrate = len(wins) / len(sells) * 100 if sells else 0
        avg_profit = np.mean([t["profit"] for t in sells]) if sells else 0
        best = max(sells, key=lambda x: x["profit"]) if sells else None
        worst = min(sells, key=lambda x: x["profit"]) if sells else None

        return {
            "ticker": self.ticker,
            "total_return": round(total_return, 2),
            "final_capital": round(self.final_capital, 2),
            "winrate": round(winrate, 1),
            "trades": len(sells),
            "avg_profit": round(avg_profit, 2),
            "best_trade": best,
            "worst_trade": worst
        }

    def print_report(self):
        """Вывод отчёта"""
        s = self.get_stats()
        print("\n" + "=" * 50)
        print(f"  ОТЧЁТ — {s['ticker']} ({self.period})")
        print("=" * 50)
        print(f"  Стартовый капитал:  $10,000.00")
        print(f"  Итоговый капитал:   ${s['final_capital']:,.2f}")
        print(f"  Доходность:         {s['total_return']}%")
        print(f"  Винрейт:            {s['winrate']}%")
        print(f"  Сделок:             {s['trades']}")
        print(f"  Средняя прибыль:    {s['avg_profit']}%")
        print(f"  Стоп-лосс:          {self.stop_loss*100:.0f}%")
        print(f"  Тейк-профит:        {self.take_profit*100:.0f}%")
        if s["best_trade"]:
            print(f"  Лучшая сделка:      +{s['best_trade']['profit']}% [{s['best_trade']['reason']}]")
        if s["worst_trade"]:
            print(f"  Худшая сделка:      {s['worst_trade']['profit']}% [{s['worst_trade']['reason']}]")
        print("=" * 50)
        return self

    def plot(self):
        """Визуализация"""
        portfolio_df = pd.DataFrame(self.portfolio).set_index("date")
        trades_df = pd.DataFrame(self.trades)
        close = self.data["Close"]

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 10),
                                             gridspec_kw={"height_ratios": [3, 1, 1]})
        fig.patch.set_facecolor("#0d0d0d")
        fig.suptitle(f"{self.ticker} — Trading Strategy", color="white", fontsize=14)

        # Цена
        ax1.plot(close.index, close, color="white", linewidth=1.5, label="Цена")
        ax1.plot(close.index, self.data["MA7"], color="orange", linewidth=1, linestyle="--", label="MA7")
        buys = trades_df[trades_df["type"] == "BUY"]
        sells_df = trades_df[trades_df["type"] == "SELL"]
        ax1.scatter(buys["date"], buys["price"], color="#00ff88", marker="^", s=100, zorder=5, label="Покупка")
        ax1.scatter(sells_df[sells_df["reason"] == "СИГНАЛ"]["date"],
                    sells_df[sells_df["reason"] == "СИГНАЛ"]["price"],
                    color="#ff4444", marker="v", s=100, zorder=5, label="Продажа")
        ax1.scatter(sells_df[sells_df["reason"] == "STOP-LOSS"]["date"],
                    sells_df[sells_df["reason"] == "STOP-LOSS"]["price"],
                    color="#ff8800", marker="x", s=150, zorder=5, label="Стоп-лосс")
        ax1.scatter(sells_df[sells_df["reason"] == "TAKE-PROFIT"]["date"],
                    sells_df[sells_df["reason"] == "TAKE-PROFIT"]["price"],
                    color="#00aaff", marker="*", s=150, zorder=5, label="Тейк-профит")
        ax1.set_facecolor("#0d0d0d")
        ax1.tick_params(colors="white")
        ax1.legend(fontsize=8)
        ax1.grid(alpha=0.2)

        # RSI
        ax2.plot(self.data.index, self.data["RSI"], color="#00ff88", linewidth=1.5)
        ax2.axhline(70, color="red", linestyle="--", alpha=0.7)
        ax2.axhline(30, color="blue", linestyle="--", alpha=0.7)
        ax2.fill_between(self.data.index, self.data["RSI"], 70,
                         where=self.data["RSI"] >= 70, alpha=0.2, color="red")
        ax2.fill_between(self.data.index, self.data["RSI"], 30,
                         where=self.data["RSI"] <= 30, alpha=0.2, color="blue")
        ax2.set_facecolor("#0d0d0d")
        ax2.tick_params(colors="white")
        ax2.set_title("RSI", color="white", fontsize=10)
        ax2.grid(alpha=0.2)

        # Портфель
        ax3.plot(portfolio_df.index, portfolio_df["value"], color="#00ff88", linewidth=1.5)
        ax3.axhline(self.initial_capital, color="white", linestyle="--", alpha=0.5)
        ax3.fill_between(portfolio_df.index, portfolio_df["value"], self.initial_capital,
                         where=portfolio_df["value"] >= self.initial_capital, alpha=0.2, color="#00ff88")
        ax3.fill_between(portfolio_df.index, portfolio_df["value"], self.initial_capital,
                         where=portfolio_df["value"] < self.initial_capital, alpha=0.2, color="#ff4444")
        ax3.set_facecolor("#0d0d0d")
        ax3.tick_params(colors="white")
        ax3.set_title("Капитал", color="white", fontsize=10)
        ax3.grid(alpha=0.2)

        plt.tight_layout()
        plt.show()
        return self


# Запуск
if __name__ == "__main__":
    # Одна строка — полный анализ
    strategy = TradingStrategy("AAPL", period="2y", stop_loss=0.05, take_profit=0.15)
    strategy.load_data().calculate_indicators().run_backtest().print_report().plot()

    # Легко сменить акцию — просто измени тикер
    # TradingStrategy("TSLA").load_data().calculate_indicators().run_backtest().print_report().plot()
    # TradingStrategy("BTC-USD").load_data().calculate_indicators().run_backtest().print_report().plot()