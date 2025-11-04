"""
🌙 Wallet Registry
Central registry for managing approved wallets and their permissions
Built with love by Moon Dev 🚀
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from termcolor import cprint


class WalletRegistry:
    """
    Registry for managing wallet permissions and metadata
    Tracks approved wallets, permissions, and activity
    """

    def __init__(self):
        """Initialize the wallet registry"""
        self.name = "Wallet Registry"
        self.version = "1.0.0"

        # Storage
        self.registry_file = "data/wallet_registry.json"
        self._ensure_data_directory()

        # Load registry
        self.registry = self._load_registry()

        cprint(f"📋 {self.name} v{self.version} initialized", "cyan")
        cprint(
            f"   Registered wallets: {len(self.registry.get('wallets', {}))}", "cyan"
        )

    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)

    def _load_registry(self) -> Dict[str, Any]:
        """Load wallet registry from storage"""
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            cprint(f"⚠️ Failed to load registry: {str(e)}", "yellow")

        return {
            "master_address": "",
            "wallets": {},
            "last_updated": datetime.now().isoformat(),
            "version": self.version,
        }

    def _save_registry(self):
        """Save wallet registry to storage"""
        try:
            self.registry["last_updated"] = datetime.now().isoformat()
            with open(self.registry_file, "w") as f:
                json.dump(self.registry, f, indent=2, default=str)
        except Exception as e:
            cprint(f"❌ Failed to save registry: {str(e)}", "red")

    def register_wallet(self, wallet_address: str, metadata: Dict[str, Any]) -> bool:
        """
        Register a new wallet in the registry

        Args:
            wallet_address: Address of the wallet
            metadata: Wallet metadata

        Returns:
            Success status
        """
        try:
            if "wallets" not in self.registry:
                self.registry["wallets"] = {}

            # Create wallet entry
            wallet_entry = {
                "address": wallet_address,
                "registered_at": datetime.now().isoformat(),
                "is_active": True,
                "permissions": metadata.get("permissions", ["read"]),
                "agent_name": metadata.get("agent_name", ""),
                "description": metadata.get("description", ""),
                "risk_level": metadata.get("risk_level", "medium"),
                "max_daily_volume": metadata.get("max_daily_volume", 10000),
                "last_activity": None,
                "activity_count": 0,
                "approved_actions": [],
                "blocked_actions": [],
            }

            self.registry["wallets"][wallet_address] = wallet_entry
            self._save_registry()

            cprint(
                f"✅ Registered wallet: {wallet_address[:8]}...{wallet_address[-6:]}",
                "green",
            )
            return True

        except Exception as e:
            cprint(f"❌ Failed to register wallet: {str(e)}", "red")
            return False

    def update_wallet_permissions(
        self, wallet_address: str, permissions: List[str]
    ) -> bool:
        """
        Update permissions for a wallet

        Args:
            wallet_address: Address of the wallet
            permissions: New permissions list

        Returns:
            Success status
        """
        try:
            if wallet_address not in self.registry.get("wallets", {}):
                cprint(f"⚠️ Wallet not found: {wallet_address[:8]}...", "yellow")
                return False

            self.registry["wallets"][wallet_address]["permissions"] = permissions
            self.registry["wallets"][wallet_address][
                "updated_at"
            ] = datetime.now().isoformat()
            self._save_registry()

            cprint(
                f"✅ Updated permissions for wallet: {wallet_address[:8]}...", "green"
            )
            return True

        except Exception as e:
            cprint(f"❌ Failed to update permissions: {str(e)}", "red")
            return False

    def get_wallet_info(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Get information for a wallet

        Args:
            wallet_address: Address of the wallet

        Returns:
            Wallet information or None
        """
        return self.registry.get("wallets", {}).get(wallet_address)

    def get_wallet_permissions(self, wallet_address: str) -> List[str]:
        """
        Get permissions for a wallet

        Args:
            wallet_address: Address of the wallet

        Returns:
            List of permissions
        """
        wallet_info = self.get_wallet_info(wallet_address)
        if wallet_info:
            return wallet_info.get("permissions", [])
        return []

    def is_wallet_active(self, wallet_address: str) -> bool:
        """
        Check if a wallet is active

        Args:
            wallet_address: Address of the wallet

        Returns:
            True if wallet is active
        """
        wallet_info = self.get_wallet_info(wallet_address)
        if wallet_info:
            return wallet_info.get("is_active", False)
        return False

    def deactivate_wallet(self, wallet_address: str, reason: str = "") -> bool:
        """
        Deactivate a wallet

        Args:
            wallet_address: Address of the wallet
            reason: Reason for deactivation

        Returns:
            Success status
        """
        try:
            if wallet_address not in self.registry.get("wallets", {}):
                cprint(f"⚠️ Wallet not found: {wallet_address[:8]}...", "yellow")
                return False

            self.registry["wallets"][wallet_address]["is_active"] = False
            self.registry["wallets"][wallet_address][
                "deactivated_at"
            ] = datetime.now().isoformat()
            self.registry["wallets"][wallet_address]["deactivation_reason"] = reason
            self._save_registry()

            cprint(f"🚫 Deactivated wallet: {wallet_address[:8]}... ({reason})", "red")
            return True

        except Exception as e:
            cprint(f"❌ Failed to deactivate wallet: {str(e)}", "red")
            return False

    def log_wallet_activity(
        self,
        wallet_address: str,
        action: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Log activity for a wallet

        Args:
            wallet_address: Address of the wallet
            action: Action performed
            success: Whether the action was successful
            details: Additional details
        """
        try:
            if wallet_address not in self.registry.get("wallets", {}):
                return

            wallet = self.registry["wallets"][wallet_address]

            # Update activity info
            wallet["last_activity"] = datetime.now().isoformat()
            wallet["activity_count"] += 1

            # Log action
            action_log = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "success": success,
                "details": details or {},
            }

            if success:
                if "approved_actions" not in wallet:
                    wallet["approved_actions"] = []
                wallet["approved_actions"].append(action_log)

                # Keep only last 100 actions
                if len(wallet["approved_actions"]) > 100:
                    wallet["approved_actions"] = wallet["approved_actions"][-100:]
            else:
                if "blocked_actions" not in wallet:
                    wallet["blocked_actions"] = []
                wallet["blocked_actions"].append(action_log)

                # Keep only last 50 blocked actions
                if len(wallet["blocked_actions"]) > 50:
                    wallet["blocked_actions"] = wallet["blocked_actions"][-50:]

            self._save_registry()

        except Exception as e:
            cprint(f"⚠️ Failed to log activity: {str(e)}", "yellow")

    def get_active_wallets(self) -> List[Dict[str, Any]]:
        """Get all active wallets"""
        wallets = []
        for addr, data in self.registry.get("wallets", {}).items():
            if data.get("is_active", False):
                wallets.append({"address": addr, **data})
        return wallets

    def get_wallet_stats(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get statistics for a wallet

        Args:
            wallet_address: Address of the wallet

        Returns:
            Wallet statistics
        """
        wallet_info = self.get_wallet_info(wallet_address)
        if not wallet_info:
            return {}

        approved_actions = wallet_info.get("approved_actions", [])
        blocked_actions = wallet_info.get("blocked_actions", [])

        # Calculate stats
        total_actions = len(approved_actions) + len(blocked_actions)
        success_rate = len(approved_actions) / total_actions if total_actions > 0 else 0

        # Recent activity (last 24 hours)
        now = datetime.now()
        recent_approved = [
            a
            for a in approved_actions
            if (now - datetime.fromisoformat(a["timestamp"])).total_seconds() < 86400
        ]
        recent_blocked = [
            a
            for a in blocked_actions
            if (now - datetime.fromisoformat(a["timestamp"])).total_seconds() < 86400
        ]

        return {
            "wallet_address": wallet_address,
            "total_actions": total_actions,
            "approved_actions": len(approved_actions),
            "blocked_actions": len(blocked_actions),
            "success_rate": success_rate,
            "recent_approved": len(recent_approved),
            "recent_blocked": len(recent_blocked),
            "last_activity": wallet_info.get("last_activity"),
            "is_active": wallet_info.get("is_active", False),
        }

    def cleanup_expired_wallets(self, max_age_days: int = 90) -> int:
        """
        Clean up wallets that haven't been active for a long time

        Args:
            max_age_days: Maximum age in days for inactive wallets

        Returns:
            Number of wallets cleaned up
        """
        cleaned = 0
        now = datetime.now()
        cutoff = now - timedelta(days=max_age_days)

        wallets_to_remove = []

        for addr, data in self.registry.get("wallets", {}).items():
            last_activity = data.get("last_activity")
            if last_activity:
                last_activity_dt = datetime.fromisoformat(last_activity)
                if last_activity_dt < cutoff and not data.get("is_active", False):
                    wallets_to_remove.append(addr)
            elif not data.get("is_active", False):
                # No activity ever and not active
                created_at = data.get("registered_at")
                if created_at:
                    created_dt = datetime.fromisoformat(created_at)
                    if created_dt < cutoff:
                        wallets_to_remove.append(addr)

        # Remove expired wallets
        for addr in wallets_to_remove:
            del self.registry["wallets"][addr]
            cleaned += 1

        if cleaned > 0:
            self._save_registry()
            cprint(f"🧹 Cleaned up {cleaned} expired wallets", "blue")

        return cleaned

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get overall registry statistics"""
        wallets = self.registry.get("wallets", {})

        active_wallets = len([w for w in wallets.values() if w.get("is_active", False)])
        inactive_wallets = len(
            [w for w in wallets.values() if not w.get("is_active", False)]
        )

        total_actions = sum(
            len(w.get("approved_actions", [])) + len(w.get("blocked_actions", []))
            for w in wallets.values()
        )

        return {
            "total_wallets": len(wallets),
            "active_wallets": active_wallets,
            "inactive_wallets": inactive_wallets,
            "total_actions": total_actions,
            "last_updated": self.registry.get("last_updated"),
            "version": self.registry.get("version", self.version),
        }

    def export_registry(self, filepath: str) -> bool:
        """
        Export the registry to a file

        Args:
            filepath: Path to export file

        Returns:
            Success status
        """
        try:
            with open(filepath, "w") as f:
                json.dump(self.registry, f, indent=2, default=str)
            cprint(f"✅ Registry exported to: {filepath}", "green")
            return True
        except Exception as e:
            cprint(f"❌ Failed to export registry: {str(e)}", "red")
            return False

    def import_registry(self, filepath: str) -> bool:
        """
        Import registry from a file

        Args:
            filepath: Path to import file

        Returns:
            Success status
        """
        try:
            with open(filepath, "r") as f:
                imported_registry = json.load(f)

            # Merge with existing registry
            if "wallets" in imported_registry:
                if "wallets" not in self.registry:
                    self.registry["wallets"] = {}

                self.registry["wallets"].update(imported_registry["wallets"])

            self._save_registry()
            cprint(f"✅ Registry imported from: {filepath}", "green")
            return True
        except Exception as e:
            cprint(f"❌ Failed to import registry: {str(e)}", "red")
            return False
