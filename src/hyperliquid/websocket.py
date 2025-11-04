"""
🌙 Hyperliquid WebSocket Client
Real-time data streaming for Hyperliquid DEX
Built with love by Moon Dev 🚀
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import websockets
from termcolor import cprint
from websockets.exceptions import ConnectionClosedError, WebSocketException

from .types import L2Book, Trade


class HyperliquidWebSocket:
    """
    WebSocket client for real-time Hyperliquid data
    Supports trades, order books, and user updates
    """

    def __init__(
        self,
        base_url: str = "wss://api.hyperliquid.xyz/ws",
        testnet: bool = False,
        reconnect_delay: float = 5.0,
        max_reconnects: int = 10,
    ):
        """Initialize the WebSocket client"""
        self.name = "Hyperliquid WebSocket"
        self.version = "1.0.0"

        # Configuration
        self.testnet = testnet
        self.base_url = (
            base_url if not testnet else "wss://api.hyperliquid-testnet.xyz/ws"
        )
        self.reconnect_delay = reconnect_delay
        self.max_reconnects = max_reconnects

        # Connection state
        self.websocket: Optional[Any] = None
        self.connected = False
        self.reconnect_count = 0

        # Subscriptions and callbacks
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = {
            "trade": [],
            "l2Book": [],
            "orderUpdates": [],
            "user": [],
            "error": [],
            "connected": [],
            "disconnected": [],
        }

        # Background tasks
        self._receive_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None

        cprint(f"🔌 {self.name} v{self.version} initialized", "cyan")
        cprint(f"   WebSocket URL: {self.base_url}", "cyan")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    def on(self, event: str, callback: Callable):
        """
        Register an event callback

        Args:
            event: Event name ('trade', 'l2Book', 'orderUpdates', 'user', 'error', 'connected', 'disconnected')
            callback: Callback function
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
        else:
            cprint(f"⚠️ Unknown event type: {event}", "yellow")

    def off(self, event: str, callback: Callable):
        """
        Unregister an event callback

        Args:
            event: Event name
            callback: Callback function to remove
        """
        if event in self.callbacks:
            try:
                self.callbacks[event].remove(callback)
            except ValueError:
                pass

    async def _emit(self, event: str, data: Any = None):
        """
        Emit an event to all registered callbacks

        Args:
            event: Event name
            data: Event data
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    cprint(f"❌ Error in {event} callback: {str(e)}", "red")

    async def connect(self):
        """Connect to the WebSocket"""
        try:
            cprint("🔌 Connecting to Hyperliquid WebSocket...", "cyan")

            self.websocket = await websockets.connect(
                self.base_url,
                extra_headers={"User-Agent": "MoonDev-Hyperliquid-WS/1.0"},
            )

            self.connected = True
            self.reconnect_count = 0

            cprint("✅ WebSocket connected", "green")

            # Start background tasks
            self._receive_task = asyncio.create_task(self._receive_loop())
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            await self._emit("connected")

        except Exception as e:
            cprint(f"❌ WebSocket connection failed: {str(e)}", "red")
            await self._handle_reconnect()

    async def disconnect(self):
        """Disconnect from the WebSocket"""
        self.connected = False

        # Cancel background tasks
        if self._receive_task:
            self._receive_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._reconnect_task:
            self._reconnect_task.cancel()

        # Close WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass

        cprint("🔌 WebSocket disconnected", "yellow")
        await self._emit("disconnected")

    async def _handle_reconnect(self):
        """Handle reconnection logic"""
        if self.reconnect_count >= self.max_reconnects:
            cprint(f"❌ Max reconnect attempts ({self.max_reconnects}) reached", "red")
            return

        self.reconnect_count += 1
        cprint(
            f"🔄 Reconnecting in {self.reconnect_delay}s (attempt {self.reconnect_count})",
            "yellow",
        )

        await asyncio.sleep(self.reconnect_delay)

        if not self._reconnect_task or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self.connect())

    async def _receive_loop(self):
        """Main receive loop for WebSocket messages"""
        try:
            while self.connected and self.websocket:
                try:
                    message = await self.websocket.recv()
                    await self._handle_message(message)

                except ConnectionClosedError:
                    cprint("🔌 WebSocket connection closed", "yellow")
                    break

                except WebSocketException as e:
                    cprint(f"❌ WebSocket error: {str(e)}", "red")
                    break

        except asyncio.CancelledError:
            pass
        except Exception as e:
            cprint(f"❌ Receive loop error: {str(e)}", "red")

        # Handle disconnection
        if self.connected:
            self.connected = False
            await self._emit("disconnected")
            await self._handle_reconnect()

    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        try:
            while self.connected:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

                if self.websocket and self.connected:
                    try:
                        # Send a simple ping
                        await self.websocket.ping()
                    except Exception as e:
                        cprint(f"❌ Heartbeat failed: {str(e)}", "red")
                        break

        except asyncio.CancelledError:
            pass

    async def _handle_message(self, message: str):
        """
        Handle incoming WebSocket message

        Args:
            message: Raw message string
        """
        try:
            data = json.loads(message)

            # Handle different message types
            if "channel" in data:
                channel = data["channel"]
                payload = data.get("data", {})

                if channel == "trades":
                    await self._handle_trades(payload)
                elif channel == "l2Book":
                    await self._handle_l2_book(payload)
                elif channel == "orderUpdates":
                    await self._handle_order_updates(payload)
                elif channel == "user":
                    await self._handle_user_updates(payload)
                else:
                    cprint(f"⚠️ Unknown channel: {channel}", "yellow")

            elif "error" in data:
                await self._emit("error", data["error"])

            else:
                cprint(f"⚠️ Unknown message format: {data}", "yellow")

        except json.JSONDecodeError as e:
            cprint(f"❌ Failed to parse WebSocket message: {str(e)}", "red")
            cprint(f"   Raw message: {message[:200]}...", "red")

    async def _handle_trades(self, data: Dict[str, Any]):
        """Handle trade updates"""
        try:
            coin = data.get("coin", "")
            trades_data = data.get("trades", [])

            trades = []
            for trade_data in trades_data:
                if isinstance(trade_data, dict):
                    trade = Trade.from_dict(trade_data)
                    trades.append(trade)

            await self._emit("trade", {"coin": coin, "trades": trades})

        except Exception as e:
            cprint(f"❌ Error handling trades: {str(e)}", "red")

    async def _handle_l2_book(self, data: Dict[str, Any]):
        """Handle L2 order book updates"""
        try:
            l2_book = L2Book.from_dict(data)
            await self._emit("l2Book", l2_book)

        except Exception as e:
            cprint(f"❌ Error handling L2 book: {str(e)}", "red")

    async def _handle_order_updates(self, data: Dict[str, Any]):
        """Handle order updates"""
        try:
            await self._emit("orderUpdates", data)

        except Exception as e:
            cprint(f"❌ Error handling order updates: {str(e)}", "red")

    async def _handle_user_updates(self, data: Dict[str, Any]):
        """Handle user-specific updates"""
        try:
            await self._emit("user", data)

        except Exception as e:
            cprint(f"❌ Error handling user updates: {str(e)}", "red")

    async def subscribe_trades(self, coin: str) -> bool:
        """
        Subscribe to trade updates for a coin

        Args:
            coin: Coin symbol (e.g., 'BTC')

        Returns:
            True if subscription successful
        """
        return await self._subscribe({"type": "trades", "coin": coin})

    async def subscribe_l2_book(self, coin: str) -> bool:
        """
        Subscribe to L2 order book updates for a coin

        Args:
            coin: Coin symbol

        Returns:
            True if subscription successful
        """
        return await self._subscribe({"type": "l2Book", "coin": coin})

    async def subscribe_order_updates(self, user_address: str) -> bool:
        """
        Subscribe to order updates for a user

        Args:
            user_address: User wallet address

        Returns:
            True if subscription successful
        """
        return await self._subscribe({"type": "orderUpdates", "user": user_address})

    async def subscribe_user_updates(self, user_address: str) -> bool:
        """
        Subscribe to user-specific updates

        Args:
            user_address: User wallet address

        Returns:
            True if subscription successful
        """
        return await self._subscribe({"type": "user", "user": user_address})

    async def _subscribe(self, subscription: Dict[str, Any]) -> bool:
        """
        Send a subscription request

        Args:
            subscription: Subscription payload

        Returns:
            True if successful
        """
        if not self.connected or not self.websocket:
            cprint("❌ WebSocket not connected", "red")
            return False

        try:
            message = {"method": "subscribe", "subscription": subscription}

            await self.websocket.send(json.dumps(message))

            # Store subscription for tracking
            sub_key = f"{subscription['type']}_{subscription.get('coin', subscription.get('user', ''))}"
            self.subscriptions[sub_key] = subscription

            cprint(
                f"✅ Subscribed to {subscription['type']} for {subscription.get('coin', subscription.get('user', ''))}",
                "green",
            )
            return True

        except Exception as e:
            cprint(f"❌ Subscription failed: {str(e)}", "red")
            return False

    async def unsubscribe(self, subscription: Dict[str, Any]) -> bool:
        """
        Unsubscribe from updates

        Args:
            subscription: Subscription to remove

        Returns:
            True if successful
        """
        if not self.connected or not self.websocket:
            cprint("❌ WebSocket not connected", "red")
            return False

        try:
            message = {"method": "unsubscribe", "subscription": subscription}

            await self.websocket.send(json.dumps(message))

            # Remove from tracking
            sub_key = f"{subscription['type']}_{subscription.get('coin', subscription.get('user', ''))}"
            self.subscriptions.pop(sub_key, None)

            cprint(f"✅ Unsubscribed from {subscription['type']}", "green")
            return True

        except Exception as e:
            cprint(f"❌ Unsubscription failed: {str(e)}", "red")
            return False

    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Get current subscriptions

        Returns:
            List of active subscriptions
        """
        return list(self.subscriptions.values())

    async def health_check(self) -> bool:
        """
        Check if WebSocket is healthy

        Returns:
            True if healthy
        """
        return self.connected and self.websocket is not None
