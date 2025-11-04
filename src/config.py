"""
🚀 HYPERLIQUID Trading System Configuration
Specialized for HyperLiquid Perpetuals Trading
Built with love by Moon Dev 🌙
"""

import os

# 🎯 EXCHANGE CONFIGURATION - HYPERLIQUID ONLY
EXCHANGE = "hyperliquid"  # The only exchange we support
EXCHANGE_NAME = "HyperLiquid"  # Display name

# 💰 HyperLiquid Configuration
# Trading symbols on HyperLiquid perpetuals
HYPERLIQUID_SYMBOLS = [
    "BTC",  # Bitcoin
    "ETH",  # Ethereum
    "SOL",  # Solana
    "ARB",  # Arbitrum
    "APT",  # Aptos
    "ADA",  # Cardano
    "AVAX",  # Avalanche
    "BNB",  # BNB
    "DOT",  # Polkadot
    "MATIC",  # Polygon
    "LINK",  # Chainlink
    "UNI",  # Uniswap
    "ATOM",  # Cosmos
    "FIL",  # Filecoin
    "TRX",  # Tron
    "XRP",  # Ripple
    "DOGE",  # Dogecoin
    "LTC",  # Litecoin
    "BCH",  # Bitcoin Cash
    "ETC",  # Ethereum Classic
]

# Default leverage for HyperLiquid trades (1-50)
HYPERLIQUID_DEFAULT_LEVERAGE = 5
HYPERLIQUID_MAX_LEVERAGE = 50

# Risk Management Settings 🛡️ - CONSERVATIVE SETTINGS
CASH_PERCENTAGE = 30  # Minimum % to keep as safety buffer (0-100)
MAX_POSITION_PERCENTAGE = 20  # Maximum % allocation per position (0-100)
STOPLOSS_PRICE = 0  # Not used yet
BREAKOUT_PRICE = 0  # Not used yet
SLEEP_AFTER_CLOSE = 900  # Prevent overtrading - 15 minutes

# Position sizing 🎯 - CAPITAL MANAGEMENT
POSITION_SIZE_USD = 100  # Default position size in USD
MAX_ORDER_SIZE_USD = 100  # Maximum order size in USD

# Trading Parameters
LEVERAGE = 5  # Default leverage for trades

# Risk Control Settings
MAX_LOSS_GAIN_CHECK_HOURS = (
    12  # How far back to check for max loss/gain limits (in hours)
)
SLEEP_BETWEEN_RUNS_MINUTES = 20  # How long to sleep between agent runs

# Loss/Gain Limits
USE_PERCENTAGE = (
    False  # If True, use percentage-based limits. If False, use USD-based limits
)

# USD-based limits (used if USE_PERCENTAGE is False)
MAX_LOSS_USD = 50  # Maximum loss in USD before stopping trading
MAX_GAIN_USD = 200  # Maximum gain in USD before stopping trading

# Minimum balance control
MINIMUM_BALANCE_USD = (
    100  # If balance falls below this, risk management will be triggered
)
USE_AI_CONFIRMATION = True  # Consult AI before closing positions

# Percentage-based limits (used if USE_PERCENTAGE is True)
MAX_LOSS_PERCENT = 5  # Maximum loss as percentage
MAX_GAIN_PERCENT = 20  # Maximum gain as percentage

# Data collection settings 📈
DAYS_BACK_FOR_DATA = 30
DATA_TIMEFRAME = "1H"  # 1m, 3m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 8H, 12H, 1D, 3D, 1W, 1M
SAVE_OHLCV_DATA = True  # Set to True to save data permanently

# AI Model Settings 🤖
AI_MODEL = "claude-3-sonnet-20240229"  # Default model
# Available models:
# - claude-3-haiku-20240307 (Fast, efficient)
# - claude-3-sonnet-20240229 (Balanced)
# - claude-3-opus-20240229 (Most powerful)
# - deepseek-chat (Fast & efficient)
# - deepseek-reasoner (Enhanced reasoning)
AI_MAX_TOKENS = 2048
AI_TEMPERATURE = 0.7

# 🌙 WALLET SYSTEM CONFIGURATION
# Complete wallet permission management for HyperLiquid trading

# Wallet Management Settings
MAX_API_WALLETS_PER_USER = int(os.environ.get("MAX_API_WALLETS_PER_USER", "5"))
WALLET_ROTATION_DAYS = int(os.environ.get("WALLET_ROTATION_DAYS", "30"))
API_WALLET_AUTO_APPROVE = (
    os.environ.get("API_WALLET_AUTO_APPROVE", "true").lower() == "true"
)

# Permission & Risk Management
MAX_TOTAL_EXPOSURE = float(os.environ.get("MAX_TOTAL_EXPOSURE", "50000"))
MAX_DAILY_LOSS = float(os.environ.get("MAX_DAILY_LOSS", "1000"))
MAX_CONCURRENT_POSITIONS = int(os.environ.get("MAX_CONCURRENT_POSITIONS", "10"))
REQUIRE_AI_CONFIRMATION = (
    os.environ.get("REQUIRE_AI_CONFIRMATION", "true").lower() == "true"
)

# Network Configuration
HYPERLIQUID_TESTNET = (
    os.environ.get("HYPERLIQUID_TESTNET", "false").lower() == "true"
)  # Production = mainnet

# Wallet Permission Levels
WALLET_PERMISSION_LEVELS = {
    "read_only": {
        "description": "Read-only access (positions, balance, market data)",
        "allowed_actions": [
            "get_positions",
            "get_balance",
            "get_account_value",
            "get_candles",
            "get_l2_book",
        ],
        "max_leverage": 1,
        "max_position_size": 0,
        "risk_level": "low",
    },
    "trading": {
        "description": "Full trading access with risk limits",
        "allowed_actions": [
            "get_positions",
            "get_balance",
            "get_account_value",
            "get_candles",
            "get_l2_book",
            "place_order",
            "cancel_order",
            "modify_order",
            "close_position",
            "update_leverage",
            "update_margin",
        ],
        "max_leverage": HYPERLIQUID_MAX_LEVERAGE,
        "max_position_size": MAX_ORDER_SIZE_USD,
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
        "max_leverage": HYPERLIQUID_MAX_LEVERAGE,
        "max_position_size": 10000,  # Higher position size
        "risk_level": "high",
    },
}

# Trading Strategy Settings
ENABLE_STRATEGIES = True  # Enable automated strategies
STRATEGY_MIN_CONFIDENCE = 0.7  # Minimum confidence to act on signals

# Market Analysis Settings
MIN_TRADES_LAST_HOUR = 2  # Minimum trades to consider a symbol active

# Real-Time Features (Optional)
REALTIME_CLIPS_ENABLED = False  # Enable/disable real-time clips
REALTIME_CLIPS_AUTO_INTERVAL = 120  # Check every N seconds
REALTIME_CLIPS_LENGTH = 2  # Minutes to analyze per check
REALTIME_CLIPS_AI_MODEL = "claude"  # Model for analysis
REALTIME_CLIPS_TWITTER = False  # Auto-open Twitter

# Future variables (not active yet) 🔮
SELL_AT_MULTIPLE = 3
USDC_SIZE = 1
LIMIT = 49
TIMEFRAME = "15m"
STOP_LOSS_PERCENTAGE = -0.24
EXIT_ALL_POSITIONS = False
DO_NOT_TRADE_LIST = []
CLOSED_POSITIONS_TXT = ""
MINIMUM_TRADES_IN_LAST_HOUR = 2
