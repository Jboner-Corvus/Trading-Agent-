"""
🌙 Hyperliquid API Types
Type definitions for Hyperliquid API responses and requests
Built with love by Moon Dev 🚀
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class AssetInfo:
    """Asset information from meta endpoint"""

    name: str
    sz_decimals: int
    max_leverage: int
    only_isolated: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetInfo":
        return cls(
            name=data["name"],
            sz_decimals=data["szDecimals"],
            max_leverage=data.get("maxLeverage", 1),
            only_isolated=data.get("onlyIsolated", False),
        )


@dataclass
class Order:
    """Order information"""

    coin: str
    side: str  # 'B' for buy, 'A' for sell
    price: float
    size: float
    order_id: int
    timestamp: int
    tif: str = "Gtc"  # Time in force
    reduce_only: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        return cls(
            coin=data["coin"],
            side=data["side"],
            price=float(data["px"]),
            size=float(data["sz"]),
            order_id=data["oid"],
            timestamp=data["timestamp"],
            tif=data.get("tif", "Gtc"),
            reduce_only=data.get("reduceOnly", False),
        )


@dataclass
class Position:
    """Position information"""

    coin: str
    size: float
    entry_price: float
    unrealized_pnl: float
    leverage: float
    liquidation_price: Optional[float] = None
    max_leverage: Optional[int] = None

    @property
    def is_long(self) -> bool:
        return self.size > 0

    @property
    def notional_value(self) -> float:
        return abs(self.size) * self.entry_price

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        return cls(
            coin=data["coin"],
            size=float(data["szi"]),
            entry_price=float(data["entryPx"]),
            unrealized_pnl=float(data["unrealizedPnl"]),
            leverage=float(data.get("leverage", 1)),
            liquidation_price=(
                float(data["liquidationPx"]) if "liquidationPx" in data else None
            ),
            max_leverage=data.get("maxLeverage"),
        )


@dataclass
class Trade:
    """Trade/fill information"""

    coin: str
    side: str
    price: float
    size: float
    time: int
    fee: float
    order_id: Optional[int] = None
    trade_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trade":
        return cls(
            coin=data["coin"],
            side=data["side"],
            price=float(data["px"]),
            size=float(data["sz"]),
            time=data["time"],
            fee=float(data["fee"]),
            order_id=data.get("oid"),
            trade_id=data.get("tid"),
        )


@dataclass
class L2Book:
    """L2 Order book"""

    coin: str
    bids: List[List[float]]  # [[price, size], ...]
    asks: List[List[float]]  # [[price, size], ...]
    timestamp: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "L2Book":
        # Handle different response formats
        levels = data.get("levels", [])
        if isinstance(levels, list) and len(levels) > 0:
            if isinstance(levels[0], dict):
                # Format: levels[0] = {'bids': [...], 'asks': [...]}
                bids_data = levels[0].get("bids", [])
                asks_data = levels[0].get("asks", [])
            else:
                # Format: levels = [[bids], [asks]]
                bids_data = levels[0] if len(levels) > 0 else []
                asks_data = levels[1] if len(levels) > 1 else []
        else:
            bids_data = []
            asks_data = []

        return cls(
            coin=data["coin"],
            bids=[[float(level[0]), float(level[1])] for level in bids_data],
            asks=[[float(level[0]), float(level[1])] for level in asks_data],
            timestamp=data.get("time", 0),
        )


@dataclass
class Candle:
    """OHLCV candle data"""

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Candle":
        return cls(
            timestamp=data["t"],
            open=float(data["o"]),
            high=float(data["h"]),
            low=float(data["l"]),
            close=float(data["c"]),
            volume=float(data["v"]),
        )


# API Request/Response Types
InfoRequest = Dict[str, Any]
InfoResponse = Union[Dict[str, Any], List[Any]]

ExchangeRequest = Dict[str, Any]
ExchangeResponse = Dict[str, Any]

# Asset ID mappings
ASSET_IDS = {
    # Perpetual assets (index in meta.universe)
    "BTC": 0,
    "ETH": 1,
    "SOL": 2,
    "ARB": 3,
    "APE": 4,
    "AVAX": 5,
    "BNB": 6,
    "DOGE": 7,
    "FTM": 8,
    "GMX": 9,
    "LINK": 10,
    "LTC": 11,
    "NEAR": 12,
    "OP": 13,
    "ORDI": 14,
    "PEPE": 15,
    "SHIB": 16,
    "SUI": 17,
    "SUSHI": 18,
    "TIA": 19,
    "TRX": 20,
    "UNI": 21,
    "WLD": 22,
    "XRP": 23,
    "ZKS": 24,
    "SEI": 25,
    "INJ": 26,
    "STX": 27,
    "FIL": 28,
    "ETC": 29,
    "CFX": 30,
    "ICP": 31,
    "APT": 32,
    "IMX": 33,
    "GALA": 34,
    "XLM": 35,
    "DOT": 36,
    "ADA": 37,
    "MATIC": 38,
    "ATOM": 39,
    "LDO": 40,
    "ONDO": 41,
    "ALT": 42,
    "JTO": 43,
    "ZRO": 44,
    "ENA": 45,
    "WIF": 46,
    "TIA": 47,
    "MERL": 48,
    "PYTH": 49,
    "REZ": 50,
    "STRK": 51,
    "TON": 52,
    "AXL": 53,
    "MYRO": 54,
    "MEW": 55,
    "AUCTION": 56,
    "RARI": 57,
    "BOME": 58,
    "PNUT": 59,
    "MOTHER": 60,
    "GRIFFAIN": 61,
    "AI16Z": 62,
    "FARTCOIN": 63,
    "GOAT": 64,
    "HYPER": 65,
    "TURBO": 66,
    "ZEREBRO": 67,
    "POPCAT": 68,
    "CUMMIES": 69,
    "S": 70,
    "AIXBT": 71,
    "SPX": 72,
    "KMNO": 73,
    "MOODENG": 74,
    "BANANA": 75,
    "PONKE": 76,
    "SSB": 77,
    "KAIA": 78,
    "CETUS": 79,
    "KAS": 80,
    "BEAM": 81,
    "CAKE": 82,
    "ENA": 83,
    "ENA": 84,
    "ENA": 85,
    "ENA": 86,
    "ENA": 87,
    "ENA": 88,
    "ENA": 89,
    "ENA": 90,
    "ENA": 91,
    "ENA": 92,
    "ENA": 93,
    "ENA": 94,
    "ENA": 95,
    "ENA": 96,
    "ENA": 97,
    "ENA": 98,
    "ENA": 99,
}

# Spot asset IDs (10000 + spotIndex)
SPOT_ASSET_OFFSET = 10000


def get_asset_id(symbol: str, is_spot: bool = False) -> int:
    """
    Get asset ID for symbol

    Args:
        symbol: Asset symbol (e.g., 'BTC')
        is_spot: Whether this is a spot asset

    Returns:
        Asset ID
    """
    if is_spot:
        # For spot assets, we need to look up the index in spotMeta
        # This is a placeholder - in practice, you'd fetch from /info meta
        spot_indices = {
            "PURR/USDC": 0,
            "HYPE/USDC": 1,
            # Add more as needed
        }
        spot_index = spot_indices.get(symbol, 0)
        return SPOT_ASSET_OFFSET + spot_index
    else:
        return ASSET_IDS.get(symbol.upper(), 0)


def get_symbol_from_asset_id(asset_id: int) -> str:
    """
    Get symbol from asset ID

    Args:
        asset_id: Asset ID

    Returns:
        Symbol string
    """
    if asset_id >= SPOT_ASSET_OFFSET:
        # Spot asset
        spot_index = asset_id - SPOT_ASSET_OFFSET
        spot_symbols = {
            0: "PURR/USDC",
            1: "HYPE/USDC",
            # Add more as needed
        }
        return spot_symbols.get(spot_index, f"SPOT_{spot_index}")
    else:
        # Perpetual asset
        for symbol, aid in ASSET_IDS.items():
            if aid == asset_id:
                return symbol
        return f"UNKNOWN_{asset_id}"
