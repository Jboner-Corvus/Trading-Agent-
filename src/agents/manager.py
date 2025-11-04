#!/usr/bin/env python3
"""
🌙 AI Agents Manager - Système de gestion des 4 vrais agents IA
Uniquement les agents avec appels API LLM (ChatGPT, Claude, etc.)
"""

import json
import sys
from pathlib import Path

# Configuration des 4 vrais agents IA (avec appels LLM)
AGENTS_CONFIG = {
    "risk_agent": {
        "class": "RiskAgent",
        "module": "src.agents.risk_agent",
        "category": "risk",
        "description": "Gestion du risque en temps réel avec IA (Claude/DeepSeek)",
        "can_trade": True,
        "requires_wallet": True,
        "paper_trading": True,
        "is_ai_agent": True,  # ✅ VRAI agent IA
        "performance": "0%",
        "status": "active",
    },
    "funding_agent": {
        "class": "FundingAgent",
        "module": "src.agents.funding_agent",
        "category": "analysis",
        "description": "Monitoring des taux de funding avec IA (Claude/DeepSeek)",
        "can_trade": False,
        "requires_wallet": False,
        "paper_trading": False,
        "is_ai_agent": True,  # ✅ VRAI agent IA
        "performance": "0%",
        "status": "inactive",
    },
    "strategy_agent": {
        "class": "StrategyAgent",
        "module": "src.agents.strategy_agent",
        "category": "strategy",
        "description": "Génération de signaux techniques avec IA (Claude)",
        "can_trade": False,
        "requires_wallet": False,
        "paper_trading": False,
        "is_ai_agent": True,  # ✅ VRAI agent IA
        "performance": "0%",
        "status": "active",
    },
    "sentiment_analysis_agent": {
        "class": "SentimentAnalysisAgent",
        "module": "src.agents.sentiment_analysis_agent",
        "category": "analysis",
        "description": "Analyse de sentiment Twitter avec IA (BERT + TTS)",
        "can_trade": False,
        "requires_wallet": False,
        "paper_trading": False,
        "is_ai_agent": True,  # ✅ VRAI agent IA
        "performance": "0%",
        "status": "active",
    },
}


class AgentManager:
    """Gestionnaire des 4 vrais agents IA"""

    def __init__(self):
        self.running_agents = {}
        self.agent_stats = {}

    def get_all_agents(self):
        """Retourne uniquement les 4 vrais agents IA"""
        agents = []

        for agent_id, config in AGENTS_CONFIG.items():
            agents.append(
                {
                    "id": agent_id,
                    "name": config["class"].replace("Agent", " Agent"),
                    "description": config["description"],
                    "category": config["category"],
                    "status": config["status"],
                    "performance": config.get("performance", "0%"),
                    "can_trade": config["can_trade"],
                    "requires_wallet": config["requires_wallet"],
                    "paper_trading": config["paper_trading"],
                    "is_ai_agent": config.get("is_ai_agent", False),
                    "module": config["module"],
                    "class_name": config["class"],
                }
            )

        return agents

    def get_agent_statistics(self):
        """Statistiques des agents IA"""
        agents = self.get_all_agents()

        total = len(agents)
        active = len([a for a in agents if a["status"] == "active"])
        configured = len([a for a in agents if a["status"] in ["active", "configured"]])
        inactive = len([a for a in agents if a["status"] == "inactive"])

        # Trier par performance
        agents_sorted = sorted(
            agents,
            key=lambda x: float(x["performance"].replace("+", "").replace("%", "")),
            reverse=True,
        )

        return {
            "total": total,
            "active": active,
            "configured": configured,
            "inactive": inactive,
            "agents": agents_sorted,
        }

    def start_agent(self, agent_id, config=None):
        """Démarrer un agent IA"""
        if agent_id not in AGENTS_CONFIG:
            raise ValueError(f"Agent {agent_id} not found")

        agent_config = AGENTS_CONFIG[agent_id]

        self.running_agents[agent_id] = {
            "status": "running",
            "started_at": "2025-01-01T00:00:00Z",
            "config": config or {},
        }

        return {
            "success": True,
            "message": f"Agent {agent_id} démarré avec succès",
            "agent_info": AGENTS_CONFIG[agent_id],
        }

    def stop_agent(self, agent_id):
        """Arrêter un agent IA"""
        if agent_id in self.running_agents:
            del self.running_agents[agent_id]
            return {"success": True, "message": f"Agent {agent_id} arrêté avec succès"}
        return {
            "success": False,
            "message": f"Agent {agent_id} n'était pas en cours d'exécution",
        }

    def get_agent_status(self, agent_id):
        """Statut d'un agent IA"""
        if agent_id in self.running_agents:
            return {
                "status": "running",
                "started_at": self.running_agents[agent_id]["started_at"],
                "config": self.running_agents[agent_id]["config"],
            }
        else:
            config = AGENTS_CONFIG.get(agent_id, {})
            return {"status": "stopped", "last_run": None, "config": {}}

    def update_agent_config(self, agent_id, config):
        """Mettre à jour la configuration d'un agent IA"""
        if agent_id not in AGENTS_CONFIG:
            raise ValueError(f"Agent {agent_id} not found")

        # Simuler la sauvegarde de configuration
        return {
            "success": True,
            "message": f"Configuration de l'agent {agent_id} mise à jour",
            "updated_config": config,
        }

    def test_connection(self):
        """Tester la connexion avec le gestionnaire"""
        return {
            "success": True,
            "message": "✅ Connection to AI Agent Manager successful",
            "agents_count": len(AGENTS_CONFIG),
            "available_agents": list(AGENTS_CONFIG.keys()),
        }


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Agents Manager")
    parser.add_argument(
        "--command",
        required=True,
        choices=[
            "get_all_agents",
            "get_agent_statistics",
            "start_agent",
            "stop_agent",
            "get_agent_status",
            "update_agent_config",
            "test_connection",
        ],
    )
    parser.add_argument("--agent-id", help="ID de l'agent")
    parser.add_argument("--config", help="Configuration JSON", type=str)

    args = parser.parse_args()

    manager = AgentManager()

    try:
        if args.command == "get_all_agents":
            result = manager.get_all_agents()
        elif args.command == "get_agent_statistics":
            result = manager.get_agent_statistics()
        elif args.command == "start_agent":
            if not args.agent_id:
                raise ValueError("--agent-id requis pour start_agent")
            config = json.loads(args.config) if args.config else {}
            result = manager.start_agent(args.agent_id, config)
        elif args.command == "stop_agent":
            if not args.agent_id:
                raise ValueError("--agent-id requis pour stop_agent")
            result = manager.stop_agent(args.agent_id)
        elif args.command == "get_agent_status":
            if not args.agent_id:
                raise ValueError("--agent-id requis pour get_agent_status")
            result = manager.get_agent_status(args.agent_id)
        elif args.command == "update_agent_config":
            if not args.agent_id:
                raise ValueError("--agent-id requis pour update_agent_config")
            if not args.config:
                raise ValueError("--config requis pour update_agent_config")
            config = json.loads(args.config)
            result = manager.update_agent_config(args.agent_id, config)
        elif args.command == "test_connection":
            result = manager.test_connection()

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {"success": False, "error": str(e), "command": args.command}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
