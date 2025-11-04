"""
🌙 Wallet Manager
Manages the configured wallet for Hyperliquid trading operations
Built with love by Moon Dev 🚀
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from eth_account import Account
from termcolor import cprint

# Load environment variables
load_dotenv()


class WalletManager:
    """
    Manages the configured wallet for Hyperliquid trading
    Provides wallet information, permissions, and status
    """

    def __init__(self):
        """Initialize the wallet manager"""
        self.name = "Wallet Manager"
        self.version = "2.0.0"

        # Configuration
        self.base_url = "https://api.hyperliquid.xyz"
        self.testnet_url = "https://api.hyperliquid-testnet.xyz"
        self.is_testnet = (
            os.environ.get("HYPERLIQUID_TESTNET", "false").lower() == "true"
        )
        self.api_url = (
            self.testnet_url if self.is_testnet else self.base_url
        )  # Mainnet by default

        # Load configured wallet - REQUIRE REAL KEY
        self.private_key = os.environ.get("HYPER_LIQUID_KEY")

        if not self.private_key:
            raise ValueError(
                "❌ HYPER_LIQUID_KEY not found in environment variables. Please set your real Ethereum private key in the .env file."
            )

        if (
            self.private_key == "your_eth_private_key_here"
            or len(self.private_key.strip()) < 64
        ):
            raise ValueError(
                "❌ HYPER_LIQUID_KEY is set to placeholder or invalid value. Please set your real 64-character hex Ethereum private key."
            )

        try:
            # Validate and load the real private key
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
            cprint(
                f"✅ Real wallet loaded: {self.address[:8]}...{self.address[-6:]}",
                "green",
            )
        except Exception as e:
            raise ValueError(
                f"❌ Invalid HYPER_LIQUID_KEY format: {str(e)}. Please check your private key."
            )

        # Wallet permissions (from config)
        self.permissions = self._load_wallet_permissions()

        # Wallet status
        self.wallet_info = {
            "address": self.address,
            "permissions": self.permissions,
            "network": "testnet" if self.is_testnet else "mainnet",
            "is_configured": self.private_key is not None,
            "last_updated": datetime.now().isoformat(),
        }

        cprint(f"🔐 {self.name} v{self.version} initialized", "cyan")
        cprint(f"   Wallet: {self.address[:8]}...{self.address[-6:]}", "cyan")
        cprint(f"   Network: {'Testnet' if self.is_testnet else 'Mainnet'}", "cyan")
        cprint(f"   Permissions: {', '.join(self.permissions)}", "cyan")

    def _load_wallet_permissions(self) -> List[str]:
        """Load wallet permissions from config"""
        # Default permissions for configured wallet
        return ["trading", "read", "full_access"]

    def get_wallet_info(self) -> Dict[str, Any]:
        """Get wallet information"""
        return self.wallet_info.copy()

    def get_wallet_address(self) -> str:
        """Get wallet address"""
        return self.address

    def get_wallet_permissions(self) -> List[str]:
        """Get wallet permissions"""
        return self.permissions.copy()

    def is_wallet_configured(self) -> bool:
        """Check if wallet is configured"""
        return self.private_key is not None

    def get_wallet_status(self) -> Dict[str, Any]:
        """Get wallet status"""
        return {
            "address": self.address,
            "permissions": self.permissions,
            "network": "testnet" if self.is_testnet else "mainnet",
            "is_configured": self.private_key is not None,
            "has_private_key": self.account is not None,
            "last_updated": datetime.now().isoformat(),
        }

    def get_account(self) -> Optional[Account]:
        """Get the wallet account (for signing operations)"""
        return self.account

    def update_permissions(self, permissions: List[str]):
        """
        Update wallet permissions

        Args:
            permissions: New permissions list
        """
        self.permissions = permissions
        self.wallet_info["permissions"] = self.permissions
        self.wallet_info["last_updated"] = datetime.now().isoformat()

        cprint(f"✅ Updated wallet permissions: {', '.join(self.permissions)}", "green")

    # Legacy methods for backward compatibility
    def get_active_wallets(self) -> List[Dict[str, Any]]:
        """Get active wallets (returns configured wallet)"""
        return [
            {
                "address": self.address,
                "name": "configured_wallet",
                "permissions": self.permissions,
                "is_active": True,
                "approved": True,
                "network": "testnet" if self.is_testnet else "mainnet",
            }
        ]

    def get_wallet_for_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet for agent (returns configured wallet for all agents)

        Args:
            agent_name: Name of the agent

        Returns:
            Wallet data
        """
        return {
            "address": self.address,
            "name": f"{agent_name}_wallet",
            "permissions": self.permissions,
            "is_active": True,
            "approved": True,
            "network": "testnet" if self.is_testnet else "mainnet",
        }
