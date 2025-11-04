"""
🌙 Signature Engine
Secure transaction signing for Hyperliquid API operations
Built with love by Moon Dev 🚀
"""

import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Tuple

from eth_account import Account
from eth_account.messages import encode_defunct
from termcolor import cprint


class SignatureEngine:
    """
    Handles secure signing of Hyperliquid transactions
    Supports both L1 actions and user-signed actions
    """

    def __init__(self, private_key: Optional[str] = None):
        """Initialize the signature engine"""
        self.name = "Signature Engine"
        self.version = "1.0.0"

        # Load private key - REQUIRE REAL KEY
        if private_key:
            self.private_key = private_key
        else:
            import os

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
                f"✅ Real signature wallet loaded: {self.address[:8]}...{self.address[-6:]}",
                "green",
            )
        except Exception as e:
            raise ValueError(
                f"❌ Invalid HYPER_LIQUID_KEY format: {str(e)}. Please check your private key."
            )

        # Nonce management
        self.current_nonce = int(time.time() * 1000)  # Start with timestamp

        cprint(f"🔐 {self.name} v{self.version} initialized", "cyan")
        cprint(f"   Address: {self.address[:8]}...{self.address[-6:]}", "cyan")

    def sign_l1_action(
        self, action: Dict[str, Any], nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sign an L1 action (exchange endpoint actions)

        Args:
            action: Action to sign
            nonce: Nonce to use (optional, will auto-increment)

        Returns:
            Signature dictionary
        """
        try:
            # Use provided nonce or auto-increment
            if nonce is None:
                nonce = self.current_nonce
                self.current_nonce += 1

            # Create the message to sign
            message = self._create_l1_message(action, nonce)

            # Sign the message with real account
            signed_message = self.account.sign_message(encode_defunct(text=message))

            # Return signature in expected format
            signature = {
                "r": signed_message.r.to_bytes(32, byteorder="big").hex(),
                "s": signed_message.s.to_bytes(32, byteorder="big").hex(),
                "v": signed_message.v,
            }

            cprint(f"✅ Signed L1 action: {action.get('type', 'unknown')}", "green")
            return signature

        except Exception as e:
            cprint(f"❌ Failed to sign L1 action: {str(e)}", "red")
            raise

    def sign_user_action(
        self, action: Dict[str, Any], nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sign a user-signed action (transfers, withdrawals, etc.)

        Args:
            action: Action to sign
            nonce: Nonce to use

        Returns:
            Signature dictionary
        """
        try:
            # Use provided nonce or auto-increment
            if nonce is None:
                nonce = self.current_nonce
                self.current_nonce += 1

            # Create typed data for EIP-712 signing
            typed_data = self._create_typed_data(action, nonce)

            # Sign the typed data with real account
            signed_message = self.account.sign_typed_data(typed_data)

            # Return signature
            signature = {
                "r": signed_message.r.to_bytes(32, byteorder="big").hex(),
                "s": signed_message.s.to_bytes(32, byteorder="big").hex(),
                "v": signed_message.v,
            }

            cprint(f"✅ Signed user action: {action.get('type', 'unknown')}", "green")
            return signature

        except Exception as e:
            cprint(f"❌ Failed to sign user action: {str(e)}", "red")
            raise

    def _create_l1_message(self, action: Dict[str, Any], nonce: int) -> str:
        """
        Create the message string for L1 action signing

        Args:
            action: Action dictionary
            nonce: Nonce value

        Returns:
            Message string to sign
        """
        # Convert action to canonical JSON string
        action_json = json.dumps(action, separators=(",", ":"), sort_keys=True)

        # Create message with vault address if present
        vault_address = action.get("vaultAddress", "")
        if vault_address:
            message = f"{self.address}{vault_address}{action_json}{nonce}"
        else:
            message = f"{self.address}{action_json}{nonce}"

        return message

    def _create_typed_data(self, action: Dict[str, Any], nonce: int) -> Dict[str, Any]:
        """
        Create EIP-712 typed data structure for user actions

        Args:
            action: Action dictionary
            nonce: Nonce value

        Returns:
            Typed data structure
        """
        action_type = action.get("type", "")

        # Define type structures based on action type
        if action_type == "usdSend":
            types = {
                "HyperliquidTransaction:UsdSend": [
                    {"name": "hyperliquidChain", "type": "string"},
                    {"name": "signatureChainId", "type": "string"},
                    {"name": "destination", "type": "address"},
                    {"name": "amount", "type": "string"},
                    {"name": "time", "type": "uint64"},
                ]
            }
            primary_type = "HyperliquidTransaction:UsdSend"
            message = {
                "hyperliquidChain": action.get("hyperliquidChain", "Mainnet"),
                "signatureChainId": action.get("signatureChainId", "0xa4b1"),
                "destination": action.get("destination", ""),
                "amount": action.get("amount", ""),
                "time": nonce,
            }

        elif action_type == "withdraw3":
            types = {
                "HyperliquidTransaction:Withdraw": [
                    {"name": "hyperliquidChain", "type": "string"},
                    {"name": "signatureChainId", "type": "string"},
                    {"name": "amount", "type": "string"},
                    {"name": "time", "type": "uint64"},
                ]
            }
            primary_type = "HyperliquidTransaction:Withdraw"
            message = {
                "hyperliquidChain": action.get("hyperliquidChain", "Mainnet"),
                "signatureChainId": action.get("signatureChainId", "0xa4b1"),
                "amount": action.get("amount", ""),
                "time": nonce,
            }

        elif action_type == "spotSend":
            types = {
                "HyperliquidTransaction:SpotSend": [
                    {"name": "hyperliquidChain", "type": "string"},
                    {"name": "destination", "type": "address"},
                    {"name": "token", "type": "string"},
                    {"name": "amount", "type": "string"},
                    {"name": "time", "type": "uint64"},
                ]
            }
            primary_type = "HyperliquidTransaction:SpotSend"
            message = {
                "hyperliquidChain": action.get("hyperliquidChain", "Mainnet"),
                "destination": action.get("destination", ""),
                "token": action.get("token", ""),
                "amount": action.get("amount", ""),
                "time": nonce,
            }

        elif action_type == "approveAgent":
            types = {
                "HyperliquidTransaction:ApproveAgent": [
                    {"name": "hyperliquidChain", "type": "string"},
                    {"name": "signatureChainId", "type": "string"},
                    {"name": "agentAddress", "type": "address"},
                    {"name": "agentName", "type": "string"},
                    {"name": "nonce", "type": "uint64"},
                ]
            }
            primary_type = "HyperliquidTransaction:ApproveAgent"
            message = {
                "hyperliquidChain": action.get("hyperliquidChain", "Mainnet"),
                "signatureChainId": action.get("signatureChainId", "0xa4b1"),
                "agentAddress": action.get("agentAddress", ""),
                "agentName": action.get("agentName", ""),
                "nonce": nonce,
            }

        else:
            raise ValueError(f"Unsupported action type for typed data: {action_type}")

        # Create the full typed data structure
        typed_data = {
            "types": types,
            "primaryType": primary_type,
            "domain": {
                "name": "HyperliquidSignTransaction",
                "version": "1",
                "chainId": 42161,  # Arbitrum One
                "verifyingContract": "0x0000000000000000000000000000000000000000",
            },
            "message": message,
        }

        return typed_data

    def verify_signature(self, message: str, signature: Dict[str, Any]) -> bool:
        """
        Verify a signature against a message

        Args:
            message: Original message
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        try:
            # Reconstruct signature object
            r = int(signature["r"], 16)
            s = int(signature["s"], 16)
            v = signature["v"]

            # Recover address from signature
            recovered_address = Account.recover_message(
                encode_defunct(text=message), signature=f"0x{r:064x}{s:064x}{v:02x}"
            )

            return recovered_address.lower() == self.address.lower()

        except Exception as e:
            cprint(f"❌ Signature verification failed: {str(e)}", "red")
            return False

    def get_next_nonce(self) -> int:
        """Get the next nonce value"""
        nonce = self.current_nonce
        self.current_nonce += 1
        return nonce

    def reset_nonce(self, nonce: int):
        """
        Reset the nonce counter

        Args:
            nonce: New nonce value
        """
        self.current_nonce = max(self.current_nonce, nonce + 1)
        cprint(f"🔄 Nonce reset to: {self.current_nonce}", "yellow")

    def create_order_signature(
        self, action: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        """
        Create a complete signed order action

        Args:
            action: Order action

        Returns:
            Tuple of (signature, nonce)
        """
        nonce = self.get_next_nonce()
        signature = self.sign_l1_action(action, nonce)
        return signature, nonce

    def create_transfer_signature(
        self, action: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        """
        Create a complete signed transfer action

        Args:
            action: Transfer action

        Returns:
            Tuple of (signature, nonce)
        """
        nonce = self.get_next_nonce()
        signature = self.sign_user_action(action, nonce)
        return signature, nonce

    def get_address(self) -> str:
        """Get the signing address"""
        return self.address

    def get_status(self) -> Dict[str, Any]:
        """Get signature engine status"""
        return {
            "address": self.address,
            "current_nonce": self.current_nonce,
            "version": self.version,
        }
