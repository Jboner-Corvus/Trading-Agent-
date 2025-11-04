"""
🌙 Permission Controller
Manages wallet permissions and access control for Hyperliquid trading
Built with love by Moon Dev 🚀
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from termcolor import cprint


class PermissionController:
    """
    Controls permissions for wallet operations
    Validates actions against wallet permissions and risk limits
    """

    def __init__(self):
        """Initialize the permission controller"""
        self.name = "Permission Controller"
        self.version = "1.0.0"

        # Permission levels
        self.permission_levels = {
            "read_only": {
                "description": "Read-only access (positions, balance, market data)",
                "allowed_actions": [
                    "get_positions",
                    "get_balance",
                    "get_account_value",
                    "get_data",
                ],
                "max_leverage": 1,
                "max_position_size": 0,  # No trading
                "risk_level": "low",
            },
            "trading": {
                "description": "Full trading access with risk limits",
                "allowed_actions": [
                    "get_positions",
                    "get_balance",
                    "get_account_value",
                    "get_data",
                    "place_order",
                    "cancel_order",
                    "modify_order",
                    "close_position",
                    "update_leverage",
                    "update_margin",
                ],
                "max_leverage": int(os.environ.get("MAX_LEVERAGE", "10")),
                "max_position_size": float(
                    os.environ.get("MAX_POSITION_SIZE_USD", "1000")
                ),
                "risk_level": "medium",
            },
            "full_access": {
                "description": "Complete wallet access including transfers",
                "allowed_actions": [
                    "*",  # All actions allowed
                    "transfer_funds",
                    "withdraw",
                    "deposit",
                    "send_asset",
                    "approve_wallet",
                    "manage_permissions",
                ],
                "max_leverage": int(os.environ.get("MAX_LEVERAGE", "50")),
                "max_position_size": float(
                    os.environ.get("MAX_POSITION_SIZE_USD", "10000")
                ),
                "risk_level": "high",
            },
        }

        # Risk limits
        self.global_risk_limits = {
            "max_total_exposure": float(os.environ.get("MAX_TOTAL_EXPOSURE", "50000")),
            "max_daily_loss": float(os.environ.get("MAX_DAILY_LOSS", "1000")),
            "max_concurrent_positions": int(
                os.environ.get("MAX_CONCURRENT_POSITIONS", "10")
            ),
            "require_ai_confirmation": os.environ.get(
                "REQUIRE_AI_CONFIRMATION", "true"
            ).lower()
            == "true",
        }

        # Action tracking
        self.action_log = []
        self.daily_stats = {
            "date": datetime.now().date().isoformat(),
            "total_trades": 0,
            "total_volume": 0.0,
            "total_pnl": 0.0,
            "max_loss": 0.0,
        }

        cprint(f"🛡️ {self.name} v{self.version} initialized", "cyan")
        cprint(
            f"   Risk limits: ${self.global_risk_limits['max_total_exposure']} exposure",
            "cyan",
        )
        cprint(
            f"   AI confirmation: {self.global_risk_limits['require_ai_confirmation']}",
            "cyan",
        )

    def validate_action(
        self,
        wallet_address: str,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        wallet_permissions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Validate if an action is allowed for a wallet

        Args:
            wallet_address: Address of the wallet
            action: Action to validate
            params: Action parameters
            wallet_permissions: Wallet's permission levels

        Returns:
            Validation result dictionary
        """
        try:
            params = params or {}

            # Check if action is allowed by permissions
            permission_check = self._check_permissions(action, wallet_permissions or [])
            if not permission_check["allowed"]:
                return {
                    "allowed": False,
                    "reason": permission_check["reason"],
                    "risk_level": "blocked",
                }

            # Check risk limits
            risk_check = self._check_risk_limits(wallet_address, action, params)
            if not risk_check["allowed"]:
                return {
                    "allowed": False,
                    "reason": risk_check["reason"],
                    "risk_level": risk_check["risk_level"],
                }

            # Check AI confirmation requirement
            if self._requires_ai_confirmation(action, params):
                return {
                    "allowed": True,
                    "requires_ai_confirmation": True,
                    "reason": "Action requires AI confirmation",
                    "risk_level": "high",
                }

            # Action is allowed
            return {
                "allowed": True,
                "requires_ai_confirmation": False,
                "risk_level": self._get_action_risk_level(action, params),
                "limits": self._get_action_limits(action, wallet_permissions or []),
            }

        except Exception as e:
            cprint(f"❌ Permission validation error: {str(e)}", "red")
            return {
                "allowed": False,
                "reason": f"Validation error: {str(e)}",
                "risk_level": "blocked",
            }

    def _check_permissions(
        self, action: str, wallet_permissions: List[str]
    ) -> Dict[str, Any]:
        """Check if action is allowed by wallet permissions"""
        allowed_actions = set()

        # Aggregate all allowed actions from permission levels
        for perm_level in wallet_permissions:
            level_config = self.permission_levels.get(perm_level, {})
            level_actions = level_config.get("allowed_actions", [])

            if "*" in level_actions:
                # Full access permission
                return {"allowed": True, "reason": "Full access granted"}

            allowed_actions.update(level_actions)

        # Check if action is allowed
        if action in allowed_actions:
            return {"allowed": True, "reason": "Action permitted"}
        else:
            return {
                "allowed": False,
                "reason": f"Action '{action}' not permitted. Allowed: {list(allowed_actions)}",
            }

    def _check_risk_limits(
        self, wallet_address: str, action: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if action complies with risk limits"""
        try:
            # Trading action checks
            if action in ["place_order", "modify_order"]:
                size = params.get("size", 0)
                leverage = params.get("leverage", 1)

                # Check position size limit
                if size * leverage > self.global_risk_limits["max_total_exposure"]:
                    return {
                        "allowed": False,
                        "reason": f"Position size ${size * leverage} exceeds limit ${self.global_risk_limits['max_total_exposure']}",
                        "risk_level": "high",
                    }

            # Withdrawal/transfer checks
            if action in ["withdraw", "transfer_funds", "send_asset"]:
                amount = params.get("amount", 0)

                # Check daily loss limit
                if amount > self.global_risk_limits["max_daily_loss"]:
                    return {
                        "allowed": False,
                        "reason": f"Amount ${amount} exceeds daily limit ${self.global_risk_limits['max_daily_loss']}",
                        "risk_level": "high",
                    }

            return {"allowed": True, "reason": "Risk limits OK"}

        except Exception as e:
            return {
                "allowed": False,
                "reason": f"Risk check error: {str(e)}",
                "risk_level": "medium",
            }

    def _requires_ai_confirmation(self, action: str, params: Dict[str, Any]) -> bool:
        """Check if action requires AI confirmation"""
        if not self.global_risk_limits["require_ai_confirmation"]:
            return False

        # High-risk actions always require confirmation
        high_risk_actions = [
            "withdraw",
            "transfer_funds",
            "send_asset",
            "approve_wallet",
            "manage_permissions",
        ]

        if action in high_risk_actions:
            return True

        # Large trades require confirmation
        if action in ["place_order", "modify_order"]:
            size = params.get("size", 0)
            leverage = params.get("leverage", 1)
            if size * leverage > 5000:  # $5000 threshold
                return True

        return False

    def _get_action_risk_level(self, action: str, params: Dict[str, Any]) -> str:
        """Get risk level for an action"""
        high_risk_actions = [
            "withdraw",
            "transfer_funds",
            "send_asset",
            "approve_wallet",
        ]
        medium_risk_actions = ["place_order", "modify_order", "update_leverage"]

        if action in high_risk_actions:
            return "high"
        elif action in medium_risk_actions:
            # Check size for trading actions
            size = params.get("size", 0)
            leverage = params.get("leverage", 1)
            if size * leverage > 2000:
                return "high"
            else:
                return "medium"
        else:
            return "low"

    def _get_action_limits(
        self, action: str, wallet_permissions: List[str]
    ) -> Dict[str, Any]:
        """Get limits for an action based on permissions"""
        limits = {}

        # Get the highest permission level
        for perm_level in ["full_access", "trading", "read_only"]:
            if perm_level in wallet_permissions:
                level_config = self.permission_levels[perm_level]
                limits.update(
                    {
                        "max_leverage": level_config["max_leverage"],
                        "max_position_size": level_config["max_position_size"],
                        "risk_level": level_config["risk_level"],
                    }
                )
                break

        return limits

    def log_action(
        self,
        wallet_address: str,
        action: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
        agent_name: Optional[str] = None,
    ):
        """
        Log an action for audit and monitoring

        Args:
            wallet_address: Address performing the action
            action: Action performed
            params: Action parameters
            result: Action result
            agent_name: Name of the agent performing action
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "wallet_address": wallet_address,
            "agent_name": agent_name,
            "action": action,
            "params": params,
            "result": result,
            "risk_level": result.get("risk_level", "unknown"),
        }

        self.action_log.append(log_entry)

        # Update daily stats
        self._update_daily_stats(action, params, result)

        # Keep only last 1000 actions in memory
        if len(self.action_log) > 1000:
            self.action_log = self.action_log[-1000:]

    def _update_daily_stats(
        self, action: str, params: Dict[str, Any], result: Dict[str, Any]
    ):
        """Update daily statistics"""
        today = datetime.now().date().isoformat()

        # Reset stats if new day
        if self.daily_stats["date"] != today:
            self.daily_stats = {
                "date": today,
                "total_trades": 0,
                "total_volume": 0.0,
                "total_pnl": 0.0,
                "max_loss": 0.0,
            }

        # Update based on action
        if action in ["place_order", "modify_order"] and result.get("success", False):
            self.daily_stats["total_trades"] += 1
            size = params.get("size", 0)
            self.daily_stats["total_volume"] += size

        if action == "close_position":
            pnl = params.get("pnl", 0)
            self.daily_stats["total_pnl"] += pnl
            if pnl < 0:
                self.daily_stats["max_loss"] = min(self.daily_stats["max_loss"], pnl)

    def get_wallet_permissions(self, wallet_permissions: List[str]) -> Dict[str, Any]:
        """Get detailed permission information for a wallet"""
        permissions_info = {}

        for perm_level in wallet_permissions:
            if perm_level in self.permission_levels:
                permissions_info[perm_level] = self.permission_levels[perm_level]

        return {
            "permission_levels": wallet_permissions,
            "details": permissions_info,
            "global_limits": self.global_risk_limits,
        }

    def get_audit_log(
        self, wallet_address: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit log entries

        Args:
            wallet_address: Filter by wallet address (optional)
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries
        """
        log_entries = self.action_log

        if wallet_address:
            log_entries = [
                entry
                for entry in log_entries
                if entry["wallet_address"] == wallet_address
            ]

        return log_entries[-limit:]

    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily statistics"""
        return self.daily_stats.copy()

    def get_risk_status(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get risk status for a wallet

        Args:
            wallet_address: Wallet address to check

        Returns:
            Risk status information
        """
        # Get recent actions for this wallet
        recent_actions = self.get_audit_log(wallet_address, limit=50)

        # Calculate risk metrics
        high_risk_actions = len(
            [a for a in recent_actions if a.get("risk_level") == "high"]
        )
        failed_actions = len(
            [a for a in recent_actions if not a.get("result", {}).get("success", True)]
        )

        return {
            "wallet_address": wallet_address,
            "recent_high_risk_actions": high_risk_actions,
            "recent_failed_actions": failed_actions,
            "daily_stats": self.daily_stats,
            "risk_alerts": self._generate_risk_alerts(
                high_risk_actions, failed_actions
            ),
        }

    def _generate_risk_alerts(
        self, high_risk_count: int, failed_count: int
    ) -> List[str]:
        """Generate risk alerts based on activity"""
        alerts = []

        if high_risk_count > 10:
            alerts.append("High frequency of high-risk actions detected")
        if failed_count > 5:
            alerts.append("High number of failed actions detected")
        if self.daily_stats["max_loss"] < -500:
            alerts.append(f"Large daily loss: ${abs(self.daily_stats['max_loss'])}")

        return alerts

    def emergency_stop(self, wallet_address: str, reason: str) -> bool:
        """
        Emergency stop all trading for a wallet

        Args:
            wallet_address: Wallet to stop
            reason: Reason for emergency stop

        Returns:
            Success status
        """
        try:
            # Log emergency stop
            self.log_action(
                wallet_address=wallet_address,
                action="emergency_stop",
                params={"reason": reason},
                result={"success": True, "action": "stopped"},
                agent_name="system",
            )

            cprint(
                f"🚨 Emergency stop activated for {wallet_address[:8]}...: {reason}",
                "red",
            )
            return True

        except Exception as e:
            cprint(f"❌ Failed to activate emergency stop: {str(e)}", "red")
            return False
