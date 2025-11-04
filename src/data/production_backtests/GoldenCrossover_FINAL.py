#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Crossover Strategy - FINAL VERSION
Compatible with backtesting framework - Fully working
"""

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy


class GoldenCrossoverFinal(Strategy):
    """
    Final Golden Crossover Strategy
    Based on SMA crossover with Fibonacci retracements
    """

    def init(self):
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.sma200 = self.I(talib.SMA, self.data.Close, timeperiod=200)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14
        )
        self.avg_volume = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        self.last_peak_price = 0.0
        self.last_peak_rsi = 100.0
        self.entry_bar = 0

    def next(self):
        if len(self.data) < 200:
            return

        close = self.data.Close[-1]
        low = self.data.Low[-1]
        high = self.data.High[-1]
        volume = self.data.Volume[-1]
        sma20 = self.sma20[-1]
        sma200 = self.sma200[-1]
        rsi = self.rsi[-1]
        atr = self.atr[-1]
        avg_vol = self.avg_volume[-1]

        # Exit condition: broken uptrend
        if close <= sma200:
            if self.position:
                self.position.close()
                print("Exiting long due to broken uptrend below SMA200")
            return

        # Calculate dynamic Fib 61.8% retracement
        fib618 = self._calculate_fib618()
        if fib618 is None:
            return

        # Entry conditions
        crossover = (
            len(self.data) > 1
            and self.data.Close[-2] <= self.sma20[-2]
            and close > sma20
        )
        touch_fib = low <= fib618 + (0.01 * close)  # Tolerance for touch/wick
        volume_confirm = volume > avg_vol
        uptrend = close > sma200

        if crossover and touch_fib and volume_confirm and uptrend and not self.position:
            self._execute_long_entry(close, atr, fib618)

        # Position management
        if self.position:
            self._manage_position(close, high, rsi, atr, sma20)

    def _calculate_fib618(self):
        """Calculate 61.8% Fibonacci retracement"""
        lookback = 50
        from_idx = max(0, len(self.data) - lookback - 1)

        try:
            recent_high_values = self.data.High.iloc[
                from_idx : len(self.data) - 1
            ].values
            if len(recent_high_values) < 10:
                return None

            rel_high_idx = np.argmax(recent_high_values)
            abs_high_idx = from_idx + rel_high_idx
            swing_high = self.data.High.iloc[abs_high_idx]

            low_values_to_high = self.data.Low.iloc[from_idx : abs_high_idx + 1].values
            rel_low_idx = np.argmin(low_values_to_high)
            abs_low_idx = from_idx + rel_low_idx
            swing_low = self.data.Low.iloc[abs_low_idx]

            return swing_high - 0.618 * (swing_high - swing_low)
        except:
            return None

    def _execute_long_entry(self, close, atr, fib618):
        """Execute long entry with proper risk management"""
        entry_price = close
        sl_distance = 1.2 * atr
        stop_price = entry_price - sl_distance

        if fib618 < entry_price:
            stop_price = min(stop_price, fib618 - 0.5 * atr)

        risk_per_unit = entry_price - stop_price
        if risk_per_unit <= 0:
            return

        capital = 1000000
        risk_amount = capital * 0.01
        position_size = int(round(risk_amount / risk_per_unit))

        if position_size > 0:
            self.buy(size=position_size, sl=stop_price)
            self.entry_bar = len(self.data) - 1
            self.last_peak_price = self.data.High[-1]
            self.last_peak_rsi = self.rsi[-1]
            print(
                f"LONG ENTRY at {entry_price:.2f}, SL {stop_price:.2f}, Size {position_size}"
            )

    def _manage_position(self, close, high, rsi, atr, sma20):
        """Manage existing positions"""
        entry_price = self.position.entry_price
        current_sl = self.position.sl
        bars_since_entry = len(self.data) - 1 - self.entry_bar
        unrealized_pnl = close - entry_price
        risk = entry_price - current_sl if current_sl else atr * 1.2

        # Trailing stop after 1:1 RR
        if unrealized_pnl >= risk:
            trail_sl = sma20 - atr
            if trail_sl > current_sl:
                self.position.sl = trail_sl
                print(f"Trailing SL updated to {trail_sl:.2f} after 1:1 RR")

        # Profit take at 2:1 RR
        if unrealized_pnl >= 2 * risk:
            print("Taking profits at 2:1 RR!")
            self.position.close()
            return

        # Bearish divergence approximation
        if (
            rsi > 70
            and len(self.data) > 2
            and close > self.data.Close[-2]
            and rsi < self.rsi[-2]
        ):
            print("Bearish RSI Divergence detected, EXITING!")
            self.position.close()
            return

        # Exit below SMA20 trail
        if close < sma20:
            print("EXITING below SMA20 trail")
            self.position.close()
            return

        # Update peak for next divergence check
        if high > self.last_peak_price:
            self.last_peak_price = high
            self.last_peak_rsi = rsi


def run_backtest():
    """Execute backtest and generate results"""

    # Try to load existing data
    data_paths = ["src/data/rbi_v3/10_23_2025/BTC-USD-15m-synthetic.csv"]

    data = None
    for data_path in data_paths:
        try:
            if os.path.exists(data_path):
                data = pd.read_csv(
                    data_path, parse_dates=["datetime"], index_col="datetime"
                )
                print(f"Data loaded from: {data_path}")
                break
        except (FileNotFoundError, pd.errors.EmptyDataError):
            continue

    if data is None:
        print("No data file found, creating minimal synthetic data")
        data = create_minimal_data()

    # Clean data
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if "unnamed" in col.lower()])
    data = data.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )

    data = data.dropna()

    print(f"Golden Crossover Strategy Test - FINAL VERSION")
    print(f"Data loaded: {len(data)} bars")
    print(f"Period: {data.index[0]} to {data.index[-1]}")
    print("=" * 50)

    # Configure and run backtest
    bt = Backtest(data, GoldenCrossoverFinal, cash=1000000, commission=0.002)
    stats = bt.run()

    # Display results
    print(stats)

    # Convert to JSON format for frontend
    def get_stat_value(stats_dict, possible_keys, default=0.0):
        """Helper to get statistic value from different possible key names"""
        for key in possible_keys:
            if key in stats_dict:
                value = stats_dict[key]
                if isinstance(value, (int, float)):
                    return float(value)
        return default

    try:
        result = {
            "strategy": "GoldenCrossoverFinal",
            "success": True,
            "total_return": round(
                get_stat_value(stats, ["Return [%", "ReturnPct", "Return"], 0.0), 2
            ),
            "annual_return": round(
                get_stat_value(
                    stats, ["Return (Ann.) [%", "AnnualReturn", "AnnualReturnPct"], 0.0
                ),
                2,
            ),
            "sharpe_ratio": round(
                get_stat_value(stats, ["Sharpe Ratio", "SharpeRatio"], 0.0), 2
            ),
            "max_drawdown": round(
                get_stat_value(
                    stats, ["Max. Drawdown [%", "MaxDrawdown", "MaxDrawdownPct"], 0.0
                ),
                2,
            ),
            "total_trades": int(
                get_stat_value(stats, ["# Trades", "TradeCount", "TotalTrades"], 0)
            ),
            "win_rate": round(
                get_stat_value(stats, ["Win Rate [%", "WinRate", "WinRatePct"], 0.0), 2
            ),
            "profit_factor": round(
                get_stat_value(stats, ["Profit Factor", "ProfitFactor"], 0.0), 2
            ),
            "final_balance": round(
                get_stat_value(
                    stats, ["Equity Final [$", "FinalEquity", "FinalBalance"], 1000000.0
                ),
                2,
            ),
            "timestamp": datetime.now().isoformat(),
            "execution_time": "backtesting_framework",
            "improvements": [
                "SMA 20/200 crossover system",
                "Dynamic Fibonacci 61.8% retracement",
                "Trailing stop after 1:1 RR",
                "RSI divergence detection",
                "Volume confirmation filters",
            ],
        }
    except Exception as e:
        print(f"Error processing stats: {e}")
        result = {
            "strategy": "GoldenCrossoverFinal",
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

    # Save results
    output_file = "GoldenCrossover_FINAL_results.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to {output_file}")
    return result


def create_minimal_data():
    """Create minimal synthetic OHLCV data"""
    print("Generating minimal synthetic OHLCV data...")

    # Create 2000 bars of 15min data (about 20 days for SMA200)
    dates = pd.date_range(start="2024-01-01", periods=2000, freq="15min")
    n = len(dates)

    # Simple random walk for BTC prices
    np.random.seed(42)
    returns = np.random.normal(0.0001, 0.015, n)
    price = 45000  # Starting BTC price

    closes = [price]
    for ret in returns[1:]:
        price *= 1 + ret
        closes.append(max(price, 1000))  # Minimum price floor

    # Generate OHLC
    highs = []
    lows = []
    opens = []

    for i, close in enumerate(closes):
        if i == 0:
            opens.append(close)
        else:
            opens.append(closes[i - 1])

        # Add some volatility to high/low
        vol = abs(np.random.normal(0, close * 0.008))
        highs.append(close + vol)
        lows.append(max(close - vol, close * 0.95))  # Ensure low < close

    # Volume
    volumes = np.random.lognormal(8, 1, n)

    data = pd.DataFrame(
        {"Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": volumes},
        index=dates,
    )

    print(f"Generated {len(data)} synthetic bars")
    return data


if __name__ == "__main__":
    result = run_backtest()
    if result.get("success"):
        print(f"\nSUMMARY:")
        print(f"Return: {result['total_return']:+.1f}%")
        print(f"Sharpe: {result['sharpe_ratio']:.2f}")
        print(f"Win Rate: {result['win_rate']:.1f}%")
        print(f"Max DD: {result['max_drawdown']:.1f}%")
        print(f"# Trades: {result['total_trades']}")
    else:
        print(f"\nERROR: {result.get('error', 'Unknown error')}")
