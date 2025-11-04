"""
🚀 NOVAQUOTE API Module
Compatibility layer for API connections
"""

import json
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("novaquote_api")


class DeamonDevAPI:
    """Mock API client for compatibility"""

    def __init__(self, base_url="http://localhost:7000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.is_connected = False

    def connect(self) -> bool:
        """Connect to API"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            self.is_connected = response.status_code == 200
            logger.info(
                f"API connection: {'✅ Success' if self.is_connected else '❌ Failed'}"
            )
            return self.is_connected
        except Exception as e:
            logger.error(f"API connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from API"""
        self.session.close()
        self.is_connected = False
        logger.info("API disconnected")

    def get_agents(self) -> Dict:
        """Get agents from API"""
        if not self.is_connected:
            return {"success": False, "error": "Not connected"}

        try:
            response = self.session.get(f"{self.base_url}/api/agents", timeout=10)
            return (
                response.json() if response.status_code == 200 else {"success": False}
            )
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return {"success": False, "error": str(e)}

    def get_dashboard(self) -> Dict:
        """Get dashboard data"""
        if not self.is_connected:
            return {"success": False, "error": "Not connected"}

        try:
            response = self.session.get(f"{self.base_url}/api/dashboard", timeout=10)
            return (
                response.json() if response.status_code == 200 else {"success": False}
            )
        except Exception as e:
            logger.error(f"Failed to get dashboard: {e}")
            return {"success": False, "error": str(e)}

    def post_data(self, endpoint: str, data: Dict) -> Dict:
        """Post data to API"""
        if not self.is_connected:
            return {"success": False, "error": "Not connected"}

        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}", json=data, timeout=10
            )
            return (
                response.json() if response.status_code == 200 else {"success": False}
            )
        except Exception as e:
            logger.error(f"Failed to post data: {e}")
            return {"success": False, "error": str(e)}


# Global API instance
api_client = DeamonDevAPI()


def get_api_client() -> DeamonDevAPI:
    """Get API client instance"""
    return api_client


def connect_to_backend(base_url: str = "http://localhost:7000") -> bool:
    """Connect to backend API"""
    api_client.base_url = base_url
    return api_client.connect()
