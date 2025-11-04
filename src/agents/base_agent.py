#!/usr/bin/env python3
"""
Base Agent Class for NOVAQUOTE Trading Platform
Provides common functionality for all agents
Built with love by Moon Dev 🚀
"""

import time
import json
from typing import Dict, Optional, Any
from pathlib import Path


class BaseAgent:
    """
    Base class for all trading agents
    Provides common functionality like logging, state management, etc.
    """

    def __init__(self, agent_type: str):
        """Initialize the base agent"""
        self.agent_type = agent_type
        self.name = f"{agent_type.title()} Agent"
        self.start_time = time.time()
        self.last_update = time.time()
        self.is_running = False
        self.state = {}

        # Create data directory
        self.data_dir = Path(__file__).parent.parent / "data" / agent_type
        self.data_dir.mkdir(parents=True, exist_ok=True)

        print(f"[{self.name}] Initialized")

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] [{self.name}] {message}")

    def save_state(self, filename: str = None):
        """Save agent state to file"""
        if filename is None:
            filename = f"{self.agent_type}_state.json"

        state_file = self.data_dir / filename

        state_data = {
            "agent_type": self.agent_type,
            "name": self.name,
            "start_time": self.start_time,
            "last_update": self.last_update,
            "is_running": self.is_running,
            "state": self.state
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

        self.log(f"State saved to {state_file}")

    def load_state(self, filename: str = None):
        """Load agent state from file"""
        if filename is None:
            filename = f"{self.agent_type}_state.json"

        state_file = self.data_dir / filename

        if state_file.exists():
            with open(state_file, 'r') as f:
                state_data = json.load(f)

            self.start_time = state_data.get("start_time", time.time())
            self.last_update = state_data.get("last_update", time.time())
            self.is_running = state_data.get("is_running", False)
            self.state = state_data.get("state", {})

            self.log(f"State loaded from {state_file}")
            return True

        return False

    def update_state(self, key: str, value: Any):
        """Update a specific state value"""
        self.state[key] = value
        self.last_update = time.time()

    def get_uptime(self) -> float:
        """Get agent uptime in seconds"""
        return time.time() - self.start_time

    def start(self):
        """Start the agent"""
        self.is_running = True
        self.log("Agent started")

    def stop(self):
        """Stop the agent"""
        self.is_running = False
        self.log("Agent stopped")
        self.save_state()

    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_type": self.agent_type,
            "name": self.name,
            "is_running": self.is_running,
            "uptime": self.get_uptime(),
            "last_update": self.last_update,
            "state": self.state
        }
