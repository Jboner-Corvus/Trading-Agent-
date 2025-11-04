"""
🚀 NOVAQUOTE HyperLiquid Functions
Compatibility layer for HyperLiquid integration
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("novaquote_hyperliquid")


class HyperLiquidClient:
    """Mock HyperLiquid client for compatibility"""

    def __init__(self, base_url="https://api.hyperliquid.xyz/info"):
        self.base_url = base_url
        self.is_connected = False

    def connect(self):
        """Mock connection"""
        self.is_connected = True
        logger.info("HyperLiquid client connected (mock)")
        return True

    def disconnect(self):
        """Mock disconnection"""
        self.is_connected = False
        logger.info("HyperLiquid client disconnected (mock)")

    def get_positions(self) -> List[Dict]:
        """Get mock positions"""
        return []

    def get_balance(self) -> Dict:
        """Get mock balance"""
        return {"usd": 1000.0, "available": 800.0, "used": 200.0}

    def place_order(
        self, symbol: str, side: str, size: float, price: Optional[float] = None
    ) -> Dict:
        """Mock order placement"""
        return {
            "success": True,
            "order_id": f"mock_{symbol}_{side}_{size}",
            "status": "filled",
        }


# Global client instance
client = HyperLiquidClient()


def get_client() -> HyperLiquidClient:
    """Get HyperLiquid client instance"""
    return client


def format_hl_symbol(symbol: str) -> str:
    """Format symbol for HyperLiquid"""
    return symbol.upper()


def get_hl_price(symbol: str) -> float:
    """Get mock price"""
    prices = {"BTC": 109500, "ETH": 3850, "SOL": 187}
    return prices.get(symbol.upper(), 100.0)
