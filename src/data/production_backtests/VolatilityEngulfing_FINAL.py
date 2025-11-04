#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volatility Engulfing Strategy - FINAL VERSION
Compatible with backtesting framework - Fully working
"""

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy


class VolatilityEngulfingFinal(Strategy):
    """
    Final Volatility Engulfing Strategy
    Based on Bollinger Bands breakout with engulfing patterns
    """

    bb_period = 20
    bb_std = 2.0
    vol_period = 20
    vol_multiplier = 1.5
    sma_period = 50
    atr_period = 14
    risk_per_trade = 0.01
    rr_ratio = 2.0
    atr_multiplier_sl = 1.0

    def init(self):
        # Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_std,
            nbdevdn=self.bb_std,
            matype=0,
        )

        # Volume SMA
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_period)

        # 50 SMA
        self.sma50 = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period)

        # ATR
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.atr_period,
        )

    def next(self):
        # Skip if not enough data
        if (
            len(self.data)
            < max(self.bb_period, self.vol_period, self.sma_period, self.atr_period) + 1
        ):
            return

        # Current and previous values
        curr_o = self.data.Open[-1]
        curr_h = self.data.High[-1]
        curr_l = self.data.Low[-1]
        curr_c = self.data.Close[-1]
        curr_v = self.data.Volume[-1]

        prev_o = self.data.Open[-2]
        prev_c = self.data.Close[-2]

        # Bullish Engulfing detection
        bearish_prev = prev_c < prev_o
        bullish_curr = curr_c > curr_o
        engulfs = (curr_o < prev_c) and (curr_c > prev_o)
        is_bullish_engulfing = bearish_prev and bullish_curr and engulfs

        # Bearish Engulfing for exit
        bearish_engulfs = (
            prev_c > prev_o
            and (curr_c < curr_o)
            and (curr_o > prev_c)
            and (curr_c < prev_o)
        )
        is_bearish_engulfing = bearish_engulfs

        # Entry conditions
        breakout = curr_c > self.bb_upper[-1]
        vol_confirm = curr_v > self.vol_multiplier * self.vol_sma[-1]
        trend_filter = curr_c > self.sma50[-1]
        pattern_confirm = is_bullish_engulfing

        # Entry logic
        if (
            not self.position
            and breakout
            and vol_confirm
            and pattern_confirm
            and trend_filter
        ):
            self._execute_long_entry(curr_c, curr_l)

        # Position management
        if self.position:
            # Exit if close below middle BB
            if curr_c < self.bb_middle[-1]:
                self.position.close()
                print("Exit - Close below Middle BB")
                return

            # Exit on bearish engulfing
            if is_bearish_engulfing:
                self.position.close()
                print("Exit - Bearish Engulfing Pattern")
                return

    def _execute_long_entry(self, entry_price, current_low):
        """Execute long entry with proper risk management"""
        # SL below current low minus ATR buffer
        sl_price = current_low - (self.atr_multiplier_sl * self.atr[-1])
        risk_dist = entry_price - sl_price
        if risk_dist > 0:
            # Use fixed capital like other strategies
            capital = 1000000
            risk_amount = capital * self.risk_per_trade
            units = risk_amount / risk_dist
            size = int(round(units))
            tp_price = entry_price + (self.rr_ratio * risk_dist)

            if size > 0:
                self.buy(size=size, sl=sl_price, tp=tp_price)
                print(
                    f"LONG ENTRY at {entry_price:.2f}, SL {sl_price:.2f}, Size {size}"
                )


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

    print(f"Volatility Engulfing Strategy Test - FINAL VERSION")
    print(f"Data loaded: {len(data)} bars")
    print(f"Period: {data.index[0]} to {data.index[-1]}")
    print("=" * 50)

    # Configure and run backtest
    bt = Backtest(data, VolatilityEngulfingFinal, cash=1000000, commission=0.002)
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
            "strategy": "VolatilityEngulfingFinal",
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
                "Bollinger Bands breakout detection",
                "Bullish engulfing pattern confirmation",
                "Volume confirmation filters",
                "Dynamic risk management",
                "Multiple exit conditions",
            ],
        }
    except Exception as e:
        print(f"Error processing stats: {e}")
        result = {
            "strategy": "VolatilityEngulfingFinal",
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

    # Save results
    output_file = "VolatilityEngulfing_FINAL_results.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to {output_file}")
    return result


def create_minimal_data():
    """Create minimal synthetic OHLCV data"""
    print("Generating minimal synthetic OHLCV data...")

    # Create 1000 bars of 15min data
    dates = pd.date_range(start="2024-01-01", periods=1000, freq="15min")
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
