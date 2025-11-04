"""
🌙 Hyperliquid Signing Module
Signature generation for HyperLiquid API requests
Built with love by Moon Dev 🚀
"""

import hashlib
import json
from typing import Any, Dict

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3


def sign_user_action(
    action: Dict[str, Any], account: Account, nonce: int
) -> Dict[str, Any]:
    """
    Sign a user action for HyperLiquid exchange endpoint

    Args:
        action: Action dictionary to sign
        account: Ethereum account (from eth_account)
        nonce: Nonce value (timestamp in milliseconds)

    Returns:
        Signature dictionary
    """
    # Create the message to sign
    message = {"action": action, "nonce": nonce}

    # Serialize the message
    message_json = json.dumps(message, separators=(",", ":"), sort_keys=True)
    message_bytes = message_json.encode("utf-8")

    # Create the hash
    message_hash = hashlib.sha256(message_bytes).digest()

    # Sign the hash
    signed_message = account.sign_message(encode_defunct(primitive=message_hash))

    return {
        "hash": message_hash.hex(),
        "signature": signed_message.signature.hex(),
        "sender": account.address,
    }


def sign_l1_action(
    action: Dict[str, Any], account: Account, nonce: int
) -> Dict[str, Any]:
    """
    Sign an L1 action for HyperLiquid info endpoint

    Args:
        action: Action dictionary to sign
        account: Ethereum account (from eth_account)
        nonce: Nonce value (timestamp in milliseconds)

    Returns:
        Signature dictionary
    """
    # Create the message to sign
    message = {"action": action, "nonce": nonce}

    # Serialize the message
    message_json = json.dumps(message, separators=(",", ":"), sort_keys=True)
    message_bytes = message_json.encode("utf-8")

    # Create the hash
    message_hash = hashlib.sha256(message_bytes).digest()

    # Sign the hash
    signed_message = account.sign_message(encode_defunct(primitive=message_hash))

    return {
        "hash": message_hash.hex(),
        "signature": signed_message.signature.hex(),
        "sender": account.address,
    }


def get_nonce() -> int:
    """
    Get current timestamp as nonce

    Returns:
        Current timestamp in milliseconds
    """
    import time

    return int(time.time() * 1000)


def verify_signature(
    action: Dict[str, Any], signature_dict: Dict[str, Any], expected_sender: str = None
) -> bool:
    """
    Verify a signature

    Args:
        action: Action that was signed
        signature_dict: Signature dictionary
        expected_sender: Expected sender address (optional)

    Returns:
        True if signature is valid
    """
    try:
        # Check sender if provided
        if expected_sender and signature_dict.get("sender") != expected_sender:
            return False

        # Recreate the message
        nonce = signature_dict.get("nonce")
        if not nonce:
            return False

        message = {"action": action, "nonce": nonce}

        # Serialize the message
        message_json = json.dumps(message, separators=(",", ":"), sort_keys=True)
        message_bytes = message_json.encode("utf-8")

        # Create the hash
        message_hash = hashlib.sha256(message_bytes).digest()

        # Check hash matches
        if signature_dict.get("hash") != message_hash.hex():
            return False

        # Verify signature using eth_account
        account = Account()
        recovered = account.recover_message(
            encode_defunct(primitive=message_hash),
            signature=bytes.fromhex(signature_dict["signature"]),
        )

        return recovered == signature_dict["sender"]

    except Exception:
        return False


# Convenience function for trading
def create_signed_order(
    order_action: Dict[str, Any], account: Account, nonce: int = None
) -> Dict[str, Any]:
    """
    Create a signed order action

    Args:
        order_action: Order action from client.create_order_action()
        account: Ethereum account
        nonce: Nonce value (auto-generated if None)

    Returns:
        Dictionary with action, signature, and nonce
    """
    if nonce is None:
        nonce = get_nonce()

    signature = sign_user_action(order_action, account, nonce)

    return {"action": order_action, "signature": signature, "nonce": nonce}


# Convenience function for cancellations
def create_signed_cancel(
    cancel_action: Dict[str, Any], account: Account, nonce: int = None
) -> Dict[str, Any]:
    """
    Create a signed cancel action

    Args:
        cancel_action: Cancel action from client.create_cancel_action()
        account: Ethereum account
        nonce: Nonce value (auto-generated if None)

    Returns:
        Dictionary with action, signature, and nonce
    """
    if nonce is None:
        nonce = get_nonce()

    signature = sign_user_action(cancel_action, account, nonce)

    return {"action": cancel_action, "signature": signature, "nonce": nonce}


# Example usage:
"""
from eth_account import Account
from src.hyperliquid.signing import sign_user_action, get_nonce
from src.hyperliquid.client import HyperliquidClient

# Initialize account
account = Account.from_key(private_key)

# Create order action (from client)
client = HyperliquidClient()
order_action = client.create_order_action(
    asset_id=0,  # BTC
    is_buy=True,
    price=50000,
    size=0.001
)

# Sign the action
nonce = get_nonce()
signature = sign_user_action(order_action, account, nonce)

# Use in exchange call
result = await client.place_order(
    action=order_action,
    signature=signature,
    nonce=nonce
)
"""
