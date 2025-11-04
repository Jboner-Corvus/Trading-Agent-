"""
🌙 Hyperliquid API Client
Complete REST API client for Hyperliquid DEX
Built with love by Moon Dev 🚀
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import aiohttp
from termcolor import cprint

from .types import (
    AssetInfo,
    Candle,
    L2Book,
    Order,
    Position,
    Trade,
    get_asset_id,
    get_symbol_from_asset_id,
)


class HyperliquidClient:
    """
    Hyperliquid REST API Client
    Handles all interactions with /info and /exchange endpoints
    """

    def __init__(
        self,
        base_url: str = "https://api.hyperliquid.xyz",
        testnet: bool = False,
        timeout: int = 30,
    ):
        """Initialize the Hyperliquid API client"""
        self.name = "Hyperliquid API Client"
        self.version = "1.0.0"

        # Configuration
        self.testnet = testnet
        self.base_url = (
            base_url if not testnet else "https://api.hyperliquid-testnet.xyz"
        )
        self.info_url = f"{self.base_url}/info"
        self.exchange_url = f"{self.base_url}/exchange"
        self.timeout = timeout

        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None

        # Cached data
        self._meta_cache: Optional[Dict[str, Any]] = None
        self._spot_meta_cache: Optional[Dict[str, Any]] = None
        self._asset_info_cache: Dict[int, AssetInfo] = {}

        cprint(f"🔗 {self.name} v{self.version} initialized", "cyan")
        cprint(f"   Base URL: {self.base_url}", "cyan")
        cprint(f"   Network: {'Testnet' if testnet else 'Mainnet'}", "cyan")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def start(self):
        """Start the HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        cprint("✅ HTTP session started", "green")

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
        cprint("🔌 HTTP session closed", "yellow")

    async def _post_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API

        Args:
            url: API endpoint URL
            payload: Request payload

        Returns:
            Response data
        """
        if not self.session:
            raise RuntimeError("HTTP session not started. Call start() first.")

        try:
            async with self.session.post(
                url, json=payload, headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            cprint(f"❌ HTTP request failed: {str(e)}", "red")
            raise

    # ===============================
    # INFO ENDPOINT METHODS
    # ===============================

    async def get_meta(self) -> Dict[str, Any]:
        """
        Get exchange metadata (universe, asset info, etc.)

        Returns:
            Meta data dictionary
        """
        if self._meta_cache is None:
            payload = {"type": "meta"}
            self._meta_cache = await self._post_request(self.info_url, payload)

        return self._meta_cache

    async def get_spot_meta(self) -> Dict[str, Any]:
        """
        Get spot trading metadata

        Returns:
            Spot meta data dictionary
        """
        if self._spot_meta_cache is None:
            payload = {"type": "spotMeta"}
            self._spot_meta_cache = await self._post_request(self.info_url, payload)

        return self._spot_meta_cache

    async def get_asset_info(self, asset_id: int) -> AssetInfo:
        """
        Get asset information

        Args:
            asset_id: Asset ID

        Returns:
            AssetInfo object
        """
        if asset_id in self._asset_info_cache:
            return self._asset_info_cache[asset_id]

        meta = await self.get_meta()
        universe = meta.get("universe", [])

        if asset_id < len(universe):
            asset_data = universe[asset_id]
            asset_info = AssetInfo.from_dict(asset_data)
            self._asset_info_cache[asset_id] = asset_info
            return asset_info

        raise ValueError(f"Asset ID {asset_id} not found in universe")

    async def get_all_mids(self) -> Dict[str, str]:
        """
        Get all current mid prices

        Returns:
            Dictionary of symbol -> price
        """
        payload = {"type": "allMids"}
        response = await self._post_request(self.info_url, payload)
        return response

    async def get_user_state(self, user_address: str) -> Dict[str, Any]:
        """
        Get user account state

        Args:
            user_address: User wallet address

        Returns:
            User state data
        """
        payload = {"type": "clearinghouseState", "user": user_address}
        return await self._post_request(self.info_url, payload)

    async def get_open_orders(self, user_address: str) -> List[Order]:
        """
        Get user's open orders

        Args:
            user_address: User wallet address

        Returns:
            List of Order objects
        """
        payload = {"type": "openOrders", "user": user_address}
        response = await self._post_request(self.info_url, payload)

        orders = []
        for order_data in response:
            if isinstance(order_data, dict):
                orders.append(Order.from_dict(order_data))

        return orders

    async def get_user_fills(
        self,
        user_address: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Trade]:
        """
        Get user's recent fills

        Args:
            user_address: User wallet address
            start_time: Start time (optional)
            end_time: End time (optional)

        Returns:
            List of Trade objects
        """
        payload = {"type": "userFills", "user": user_address}

        if start_time:
            payload["startTime"] = start_time
        if end_time:
            payload["endTime"] = end_time

        response = await self._post_request(self.info_url, payload)

        trades = []
        for trade_data in response:
            if isinstance(trade_data, dict):
                trades.append(Trade.from_dict(trade_data))

        return trades

    async def get_positions(self, user_address: str) -> List[Position]:
        """
        Get user's positions

        Args:
            user_address: User wallet address

        Returns:
            List of Position objects
        """
        user_state = await self.get_user_state(user_address)
        positions_data = user_state.get("assetPositions", [])

        positions = []
        for pos_data in positions_data:
            position = pos_data.get("position", {})
            if position and isinstance(position, dict):
                positions.append(Position.from_dict(position))

        return positions

    async def get_l2_book(self, symbol: str) -> L2Book:
        """
        Get L2 order book for a symbol

        Args:
            symbol: Trading symbol (e.g., 'BTC')

        Returns:
            L2Book object
        """
        payload = {"type": "l2Book", "coin": symbol}
        response = await self._post_request(self.info_url, payload)
        return L2Book.from_dict(response)

    async def get_candles(
        self,
        symbol: str,
        interval: str = "15m",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Candle]:
        """
        Get candlestick data

        Args:
            symbol: Trading symbol
            interval: Time interval ('1m', '5m', '15m', '1h', '1d')
            start_time: Start timestamp (optional)
            end_time: End timestamp (optional)

        Returns:
            List of Candle objects
        """
        payload = {
            "type": "candleSnapshot",
            "req": {"coin": symbol, "interval": interval},
        }

        if start_time:
            payload["req"]["startTime"] = start_time
        if end_time:
            payload["req"]["endTime"] = end_time

        response = await self._post_request(self.info_url, payload)

        candles = []
        for candle_data in response:
            candles.append(Candle.from_dict(candle_data))

        return candles

    # ===============================
    # EXCHANGE ENDPOINT METHODS
    # ===============================

    async def place_order(
        self, action: Dict[str, Any], signature: Dict[str, Any], nonce: int
    ) -> Dict[str, Any]:
        """
        Place an order via exchange endpoint

        Args:
            action: Order action
            signature: Signature dictionary
            nonce: Nonce value

        Returns:
            Exchange response
        """
        payload = {"action": action, "nonce": nonce, "signature": signature}

        return await self._post_request(self.exchange_url, payload)

    async def cancel_order(
        self, cancels: List[Dict[str, Any]], signature: Dict[str, Any], nonce: int
    ) -> Dict[str, Any]:
        """
        Cancel orders

        Args:
            cancels: List of cancel actions
            signature: Signature dictionary
            nonce: Nonce value

        Returns:
            Exchange response
        """
        action = {"type": "cancel", "cancels": cancels}

        payload = {"action": action, "nonce": nonce, "signature": signature}

        return await self._post_request(self.exchange_url, payload)

    async def modify_order(
        self, oid: int, order: Dict[str, Any], signature: Dict[str, Any], nonce: int
    ) -> Dict[str, Any]:
        """
        Modify an existing order

        Args:
            oid: Order ID to modify
            order: New order parameters
            signature: Signature dictionary
            nonce: Nonce value

        Returns:
            Exchange response
        """
        action = {"type": "modify", "oid": oid, "order": order}

        payload = {"action": action, "nonce": nonce, "signature": signature}

        return await self._post_request(self.exchange_url, payload)

    async def update_leverage(
        self,
        asset: int,
        leverage: int,
        is_cross: bool = True,
        signature: Optional[Dict[str, Any]] = None,
        nonce: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update leverage for an asset

        Args:
            asset: Asset ID
            leverage: Leverage value
            is_cross: Whether to use cross margin
            signature: Signature dictionary
            nonce: Nonce value

        Returns:
            Exchange response
        """
        action = {
            "type": "updateLeverage",
            "asset": asset,
            "isCross": is_cross,
            "leverage": leverage,
        }

        payload = {"action": action, "nonce": nonce, "signature": signature}

        return await self._post_request(self.exchange_url, payload)

    async def usd_send(
        self,
        hyperliquid_chain: str,
        signature_chain_id: str,
        destination: str,
        amount: str,
        time: int,
        signature: Dict[str, Any],
        nonce: int,
    ) -> Dict[str, Any]:
        """
        Send USD to another address

        Args:
            hyperliquid_chain: Chain name ('Mainnet' or 'Testnet')
            signature_chain_id: Signature chain ID
            destination: Destination address
            amount: Amount to send
            time: Timestamp
            signature: Signature dictionary
            nonce: Nonce value

        Returns:
            Exchange response
        """
        action = {
            "type": "usdSend",
            "hyperliquidChain": hyperliquid_chain,
            "signatureChainId": signature_chain_id,
            "destination": destination,
            "amount": amount,
            "time": time,
        }

        payload = {"action": action, "nonce": nonce, "signature": signature}

        return await self._post_request(self.exchange_url, payload)

    # ===============================
    # UTILITY METHODS
    # ===============================

    def create_order_action(
        self,
        asset_id: int,
        is_buy: bool,
        price: float,
        size: float,
        reduce_only: bool = False,
        time_in_force: str = "Gtc",
    ) -> Dict[str, Any]:
        """
        Create an order action payload

        Args:
            asset_id: Asset ID
            is_buy: True for buy, False for sell
            price: Order price
            size: Order size
            reduce_only: Whether order should only reduce position
            time_in_force: Time in force ('Gtc', 'Ioc', 'Alo', 'Market')

        Returns:
            Order action dictionary
        """
        order = {
            "a": asset_id,
            "b": is_buy,
            "p": str(price),
            "s": str(size),
            "r": reduce_only,
            "t": {
                "limit" if time_in_force != "Market" else "market": {
                    "tif": time_in_force
                }
            },
        }

        return {"type": "order", "orders": [order], "grouping": "na"}

    def create_cancel_action(self, asset_id: int, order_id: int) -> Dict[str, Any]:
        """
        Create a cancel action payload

        Args:
            asset_id: Asset ID
            order_id: Order ID to cancel

        Returns:
            Cancel action dictionary
        """
        return {"type": "cancel", "cancels": [{"a": asset_id, "o": order_id}]}

    async def get_current_price(self, symbol: str) -> float:
        """
        Get current mid price for a symbol

        Args:
            symbol: Trading symbol

        Returns:
            Current price
        """
        mids = await self.get_all_mids()
        price_str = mids.get(symbol)

        if not price_str:
            raise ValueError(f"Symbol {symbol} not found in mids")

        return float(price_str)

    async def get_account_value(self, user_address: str) -> float:
        """
        Get account value in USD

        Args:
            user_address: User wallet address

        Returns:
            Account value in USD
        """
        user_state = await self.get_user_state(user_address)
        return float(user_state.get("marginSummary", {}).get("accountValue", "0"))

    async def get_margin_used(self, user_address: str) -> float:
        """
        Get margin used

        Args:
            user_address: User wallet address

        Returns:
            Margin used
        """
        user_state = await self.get_user_state(user_address)
        return float(user_state.get("marginSummary", {}).get("totalMarginUsed", "0"))

    def clear_cache(self):
        """Clear all cached data"""
        self._meta_cache = None
        self._spot_meta_cache = None
        self._asset_info_cache.clear()
        cprint("🧹 Cache cleared", "yellow")

    async def health_check(self) -> bool:
        """
        Check if the API is healthy

        Returns:
            True if healthy
        """
        try:
            await self.get_all_mids()
            return True
        except Exception:
            return False
