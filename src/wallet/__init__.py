"""
Wallet System Module for AI Trading Agents

This module contains wallet management functionality including:
- Configured wallet management for Hyperliquid trading
- Permission controls and signature handling
- Wallet registry and tracking
"""

from .api_wallet_manager import WalletManager
from .permission_controller import PermissionController
from .signature_engine import SignatureEngine
from .wallet_registry import WalletRegistry

# Define what gets imported with "from src.wallet import *"
__all__ = [
    "WalletManager",
    "PermissionController",
    "SignatureEngine",
    "WalletRegistry",
]
