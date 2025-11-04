"""
📊 NOVAQUOTE - METRICS COLLECTOR
================================================================================
Système de collecte et d'agrégation des métriques en temps réel.
Centralise toutes les métriques des agents, cycles, et backtests
pour le dashboard et l'analyse de performance.

Fonctionnalités :
- Collecte métriques agents (4 agents IA)
- Agrégation métriques cycles (toutes les 20 minutes)
- Métriques backtests (validation temps réel)
- Dashboard data (temps réel)
- Historique et tendances

Built with love by Moon Dev 🚀
"""

import json
import asyncio
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import time

from termcolor import cprint, colored
from src.logger import get_logger

logger = get_logger("metrics_collector")


@dataclass
class AgentMetrics:
    """Métriques d'un agent pour un cycle"""
    agent_name: str
    timestamp: str
    status: str
    confidence: float
    llm_calls: int
    execution_time_ms: float
    data: Dict[str, Any]
    backtest_validation: Optional[Dict] = None


@dataclass
class CycleAggregateMetrics:
    """Métriques agrégées d'un cycle"""
    cycle_id: str
    timestamp: str
    duration_ms: float
    agents_count: int
    agents_status: Dict[str, str]
    combined_decision: str
    decision_confidence: float
    backtests_passed: int
    backtests_failed: int
    total_llm_calls: int
    total_execution_time_ms: float
    performance_score: float


@dataclass
class DashboardMetrics:
    """Métriques pour le dashboard temps réel"""
    timestamp: str
    current_cycle: Optional[str]
    next_cycle: Optional[str]
    system_status: str
    active_agents: Dict[str, Dict[str, Any]]
    current_decision: Optional[Dict[str, Any]]
    performance_stats: Dict[str, Any]
    recent_cycles: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]


class MetricsCollector:
    """
    📊 COLLECTEUR DE MÉTRIQUES UNIFIÉES
    Centralise toutes les métriques du système
    """

    def __init__(self, max_history: int = 100):
        """Initialise le collecteur de métriques"""
        self.max_history = max_history

        # Répertoires
        self.metrics_dir = Path(__file__).parent / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Historique des métriques (en mémoire)
        self.agents_history: deque = deque(maxlen=max_history)
        self.cycles_history: deque = deque(maxlen=max_history)
        self.backtests_history: deque = deque(maxlen=max_history)

        # Métriques temps réel
        self.current_metrics: Dict[str, Any] = {}
        self.dashboard_data: DashboardMetrics = DashboardMetrics(
            timestamp=datetime.now().isoformat(),
            current_cycle=None,
            next_cycle=None,
            system_status="INIT",
            active_agents={},
            current_decision=None,
            performance_stats={},
            recent_cycles=[],
            alerts=[]
        )

        # Compteurs globaux
        self.global_stats = {
            "total_cycles": 0,
            "total_agents_runs": 0,
            "total_llm_calls": 0,
            "system_uptime_seconds": 0,
            "start_time": time.time()
        }

        cprint(f"\n{'='*80}", "cyan")
        cprint("📊 NOVAQUOTE METRICS COLLECTOR", "cyan", attrs=["bold"])
        cprint(f"{'='*80}\n", "cyan")

        cprint("✅ Metrics Collector initialisé", "green")
        cprint(f"   📁 Metrics directory: {self.metrics_dir}", "blue")
        cprint(f"   📊 Max history: {max_history} éléments", "blue")
        cprint("\n")

    async def collect_agent_metrics(self, agent_name: str, metrics: Dict[str, Any]) -> AgentMetrics:
        """
        🎯 COLLECTE LES MÉTRIQUES D'UN AGENT
        """
        agent_metrics = AgentMetrics(
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            status=metrics.get("status", "UNKNOWN"),
            confidence=metrics.get("confidence", 0.0),
            llm_metrics=metrics.get("llm_calls", 0),
            execution_time_ms=metrics.get("execution_time_ms", 0.0),
            data=metrics.get("data", {}),
            backtest_validation=metrics.get("backtest_validation")
        )

        # Ajouter à l'historique
        self.agents_history.append(agent_metrics)

        # Mettre à jour les stats globales
        self.global_stats["total_agents_runs"] += 1
        self.global_stats["total_llm_calls"] += agent_metrics.llm_metrics

        # Logger
        logger.info(f"Métriques agent collectées: {agent_name}", extra={
            "agent": agent_name,
            "status": agent_metrics.status,
            "confidence": agent_metrics.confidence,
            "llm_calls": agent_metrics.llm_metrics
        })

        return agent_metrics

    async def collect_cycle_metrics(self, cycle_data: Dict[str, Any]) -> CycleAggregateMetrics:
        """
        🔄 COLLECTE LES MÉTRIQUES D'UN CYCLE
        """
        # Calculer les métriques agrégées
        agents_status = {}
        total_llm_calls = 0
        total_execution_time = 0.0

        for result in cycle_data.get("agents_results", []):
            agent_name = result.agent_name
            agents_status[agent_name] = result.status
            total_llm_calls += result.llm_calls
            total_execution_time += result.execution_time_ms

        # Calculer le score de performance
        performance_score = self.calculate_cycle_performance_score(cycle_data)

        cycle_metrics = CycleAggregateMetrics(
            cycle_id=cycle_data["cycle_id"],
            timestamp=cycle_data["start_time"],
            duration_ms=cycle_data["duration_ms"],
            agents_count=len(cycle_data.get("agents_results", [])),
            agents_status=agents_status,
            combined_decision=cycle_data.get("combined_decision", "UNKNOWN"),
            decision_confidence=cycle_data.get("decision_confidence", 0.0),
            backtests_passed=cycle_data.get("backtests_validation", {}).get("strategies_passed", 0),
            backtests_failed=cycle_data.get("backtests_validation", {}).get("strategies_failed", 0),
            total_llm_calls=total_llm_calls,
            total_execution_time_ms=total_execution_time,
            performance_score=performance_score
        )

        # Ajouter à l'historique
        self.cycles_history.append(cycle_metrics)

        # Mettre à jour les stats globales
        self.global_stats["total_cycles"] += 1
        self.global_stats["total_llm_calls"] += total_llm_calls

        # Logger
        logger.info(f"Métriques cycle collectées: {cycle_metrics.cycle_id}", extra={
            "cycle_id": cycle_metrics.cycle_id,
            "decision": cycle_metrics.combined_decision,
            "confidence": cycle_metrics.decision_confidence,
            "performance_score": cycle_metrics.performance_score
        })

        return cycle_metrics

    def calculate_cycle_performance_score(self, cycle_data: Dict[str, Any]) -> float:
        """
        📊 CALCUL LE SCORE DE PERFORMANCE D'UN CYCLE (0.0 - 1.0)
        """
        score = 0.0
        total_weight = 0.0

        # 1. Statut des agents (40% du score)
        agents_results = cycle_data.get("agents_results", [])
        if agents_results:
            success_count = sum(1 for r in agents_results if r.get("status") == "SUCCESS")
            agent_score = success_count / len(agents_results)
            score += agent_score * 0.4
            total_weight += 0.4

        # 2. Confiance de la décision (30% du score)
        confidence = cycle_data.get("decision_confidence", 0.0)
        score += confidence * 0.3
        total_weight += 0.3

        # 3. Validation backtests (20% du score)
        bv = cycle_data.get("backtests_validation", {})
        if bv:
            total_strategies = bv.get("total_strategies_tested", 0)
            passed_strategies = bv.get("strategies_passed", 0)
            if total_strategies > 0:
                backtest_score = passed_strategies / total_strategies
                score += backtest_score * 0.2
                total_weight += 0.2

        # 4. Efficacité d'exécution (10% du score)
        duration_ms = cycle_data.get("duration_ms", 0)
        if duration_ms > 0:
            # Score basé sur la rapidité (moins de 10s = score max)
            execution_score = min(1.0, 10000 / duration_ms)
            score += execution_score * 0.1
            total_weight += 0.1

        # Normaliser le score
        if total_weight > 0:
            score = score / total_weight

        return max(0.0, min(1.0, score))

    async def update_dashboard_data(self, cycle_data: Optional[Dict[str, Any]] = None):
        """
        📱 MET À JOUR LES DONNÉES DU DASHBOARD
        """
        now = datetime.now()

        # Calculer le temps de fonctionnement
        self.global_stats["system_uptime_seconds"] = time.time() - self.global_stats["start_time"]

        # Déterminer le statut du système
        system_status = self.determine_system_status()

        # Agents actifs (dernières métriques)
        active_agents = {}
        for agent_metrics in reversed(self.agents_history):
            if agent_metrics.agent_name not in active_agents:
                active_agents[agent_metrics.agent_name] = {
                    "status": agent_metrics.status,
                    "confidence": agent_metrics.confidence,
                    "llm_calls": agent_metrics.llm_metrics,
                    "last_update": agent_metrics.timestamp,
                    "execution_time_ms": agent_metrics.execution_time_ms
                }

        # Décision actuelle
        current_decision = None
        if cycle_data:
            current_decision = {
                "decision": cycle_data.get("combined_decision"),
                "confidence": cycle_data.get("decision_confidence"),
                "summary": cycle_data.get("execution_summary", {}),
                "timestamp": cycle_data.get("end_time")
            }

        # Cycles récents
        recent_cycles = []
        for cycle_metrics in list(self.cycles_history)[-10:]:  # 10 derniers cycles
            recent_cycles.append({
                "cycle_id": cycle_metrics.cycle_id,
                "timestamp": cycle_metrics.timestamp,
                "decision": cycle_metrics.combined_decision,
                "confidence": cycle_metrics.decision_confidence,
                "performance_score": cycle_metrics.performance_score,
                "status": "SUCCESS" if cycle_metrics.performance_score > 0.7 else "WARNING" if cycle_metrics.performance_score > 0.4 else "FAIL"
            })

        # Alertes
        alerts = self.generate_alerts()

        # Statistiques de performance
        performance_stats = self.calculate_performance_stats()

        # Mettre à jour les données du dashboard
        self.dashboard_data = DashboardMetrics(
            timestamp=now.isoformat(),
            current_cycle=cycle_data.get("cycle_id") if cycle_data else self.dashboard_data.current_cycle,
            next_cycle=cycle_data.get("next_cycle_time") if cycle_data else self.dashboard_data.next_cycle,
            system_status=system_status,
            active_agents=active_agents,
            current_decision=current_decision,
            performance_stats=performance_stats,
            recent_cycles=recent_cycles,
            alerts=alerts
        )

        # Sauvegarder pour le backend
        await self.save_dashboard_data()

        return self.dashboard_data

    def determine_system_status(self) -> str:
        """
        🔍 DÉTERMINE LE STATUT GLOBAL DU SYSTÈME
        """
        if not self.cycles_history:
            return "INIT"

        # Analyser les 5 derniers cycles
        recent_cycles = list(self.cycles_history)[-5:]
        avg_performance = sum(c.performance_score for c in recent_cycles) / len(recent_cycles)

        # Compter les erreurs récentes
        errors_count = sum(
            1 for c in recent_cycles
            if c.combined_decision == "EMERGENCY_STOP" or c.performance_score < 0.3
        )

        if errors_count >= 2:
            return "CRITICAL"
        elif avg_performance > 0.8:
            return "EXCELLENT"
        elif avg_performance > 0.6:
            return "GOOD"
        elif avg_performance > 0.4:
            return "WARNING"
        else:
            return "DEGRADED"

    def generate_alerts(self) -> List[Dict[str, Any]]:
        """
        🚨 GÉNÈRE LES ALERTES DU SYSTÈME
        """
        alerts = []

        # Alerte système critique
        if self.dashboard_data.system_status == "CRITICAL":
            alerts.append({
                "type": "CRITICAL",
                "message": "Système en état critique - Vérification manuelle requise",
                "timestamp": datetime.now().isoformat(),
                "severity": "high"
            })

        # Alerte performance faible
        if self.cycles_history:
            recent_cycles = list(self.cycles_history)[-3:]
            if all(c.performance_score < 0.5 for c in recent_cycles):
                alerts.append({
                    "type": "PERFORMANCE",
                    "message": "Performance faible détectée sur les 3 derniers cycles",
                    "timestamp": datetime.now().isoformat(),
                    "severity": "medium"
                })

        # Alerte trop d'appels LLM
        avg_llm_calls = self.global_stats["total_llm_calls"] / max(1, self.global_stats["total_agents_runs"])
        if avg_llm_calls > 10:
            alerts.append({
                "type": "USAGE",
                "message": f"Usage LLM élevé: {avg_llm_calls:.1f} appels en moyenne",
                "timestamp": datetime.now().isoformat(),
                "severity": "low"
            })

        return alerts

    def calculate_performance_stats(self) -> Dict[str, Any]:
        """
        📊 CALCUL LES STATISTIQUES DE PERFORMANCE
        """
        stats = {
            "global": {
                "total_cycles": self.global_stats["total_cycles"],
                "total_agents_runs": self.global_stats["total_agents_runs"],
                "total_llm_calls": self.global_stats["total_llm_calls"],
                "system_uptime_hours": self.global_stats["system_uptime_seconds"] / 3600,
                "start_time": datetime.fromtimestamp(self.global_stats["start_time"]).isoformat()
            },
            "cycles": {},
            "agents": {},
            "backtests": {}
        }

        # Statistiques des cycles
        if self.cycles_history:
            cycles_list = list(self.cycles_history)
            stats["cycles"] = {
                "count": len(cycles_list),
                "avg_performance_score": sum(c.performance_score for c in cycles_list) / len(cycles_list),
                "avg_duration_ms": sum(c.duration_ms for c in cycles_list) / len(cycles_list),
                "avg_llm_calls": sum(c.total_llm_calls for c in cycles_list) / len(cycles_list),
                "success_rate": sum(1 for c in cycles_list if c.performance_score > 0.6) / len(cycles_list),
                "last_cycle": cycles_list[-1].cycle_id
            }

        # Statistiques des agents
        if self.agents_history:
            agents_list = list(self.agents_history)
            agent_stats = defaultdict(list)

            for agent in agents_list:
                agent_stats[agent.agent_name].append(agent.confidence)

            stats["agents"] = {
                agent_name: {
                    "runs": len(confidences),
                    "avg_confidence": sum(confidences) / len(confidences),
                    "last_run": agents_list[-1].timestamp if agents_list else None
                }
                for agent_name, confidences in agent_stats.items()
            }

        return stats

    async def save_dashboard_data(self):
        """
        💾 SAUVEGARDE LES DONNÉES DU DASHBOARD
        """
        dashboard_file = Path(__file__).parent.parent.parent / "backend" / "dashboard_data.json"

        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.dashboard_data), f, indent=2, ensure_ascii=False)

    async def get_trending_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        📈 CALCUL LES MÉTRIQUES DE TENDANCE
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filtrer les cycles récents
        recent_cycles = [
            c for c in self.cycles_history
            if datetime.fromisoformat(c.timestamp) > cutoff_time
        ]

        if not recent_cycles:
            return {"error": "Pas de données récentes"}

        # Calculer les tendances
        performance_trend = []
        confidence_trend = []
        decision_trends = defaultdict(int)

        for cycle in recent_cycles:
            performance_trend.append(cycle.performance_score)
            confidence_trend.append(cycle.decision_confidence)
            decision_trends[cycle.combined_decision] += 1

        # Calculer les tendances (slope)
        def calculate_trend(values: List[float]) -> str:
            if len(values) < 2:
                return "STABLE"

            # Calcul simple de tendance
            first_half = np.mean(values[:len(values)//2])
            second_half = np.mean(values[len(values)//2:])

            diff = second_half - first_half
            if diff > 0.05:
                return "IMPROVING"
            elif diff < -0.05:
                return "DECLINING"
            else:
                return "STABLE"

        return {
            "time_period_hours": hours,
            "cycles_count": len(recent_cycles),
            "performance": {
                "trend": calculate_trend(performance_trend),
                "avg": np.mean(performance_trend),
                "min": np.min(performance_trend),
                "max": np.max(performance_trend)
            },
            "confidence": {
                "trend": calculate_trend(confidence_trend),
                "avg": np.mean(confidence_trend),
                "min": np.min(confidence_trend),
                "max": np.max(confidence_trend)
            },
            "decisions": dict(decision_trends),
            "top_decision": max(decision_trends.items(), key=lambda x: x[1])[0] if decision_trends else None
        }

    async def export_metrics(self, format: str = "json") -> str:
        """
        💾 EXPORTE LES MÉTRIQUES
        """
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "global_stats": self.global_stats,
            "dashboard_data": asdict(self.dashboard_data),
            "agents_history": [asdict(m) for m in self.agents_history],
            "cycles_history": [asdict(m) for m in self.cycles_history],
            "backtests_history": [asdict(m) for m in self.backtests_history]
        }

        if format.lower() == "json":
            export_file = self.metrics_dir / f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return str(export_file)

        else:
            raise ValueError(f"Format non supporté: {format}")

    def get_real_time_status(self) -> Dict[str, Any]:
        """
        ⚡ RETOURNE LE STATUS TEMPS RÉEL
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": self.dashboard_data.system_status,
            "current_cycle": self.dashboard_data.current_cycle,
            "agents_active": len(self.dashboard_data.active_agents),
            "recent_alerts": len(self.dashboard_data.alerts),
            "last_update": self.dashboard_data.timestamp,
            "performance_score": (
                self.dashboard_data.performance_stats.get("cycles", {}).get("avg_performance_score", 0.0)
            )
        }


async def main():
    """Test du collecteur de métriques"""
    cprint("\n📊 TEST DU METRICS COLLECTOR", "cyan", attrs=["bold"])

    collector = MetricsCollector()

    # Simuler des données d'agents
    await collector.collect_agent_metrics("risk_agent", {
        "status": "SUCCESS",
        "confidence": 0.85,
        "llm_calls": 2,
        "execution_time_ms": 150.5,
        "data": {"risk_score": 0.15}
    })

    await collector.collect_agent_metrics("strategy_agent", {
        "status": "SUCCESS",
        "confidence": 0.92,
        "llm_calls": 1,
        "execution_time_ms": 230.8,
        "data": {"signals_count": 3}
    })

    # Mettre à jour le dashboard
    dashboard_data = await collector.update_dashboard_data()

    # Afficher le statut
    status = collector.get_real_time_status()
    cprint(f"\n⚡ STATUS TEMPS RÉEL:", "yellow", attrs=["bold"])
    for key, value in status.items():
        cprint(f"   {key}: {value}", "white")

    # Calculer les tendances
    trends = await collector.get_trending_metrics(hours=1)
    cprint(f"\n📈 TENDANCES:", "yellow", attrs=["bold"])
    cprint(f"   Performance: {trends['performance']['trend']}", "green")
    cprint(f"   Confiance: {trends['confidence']['trend']}", "green")

    # Exporter les métriques
    export_file = await collector.export_metrics()
    cprint(f"\n💾 MÉTRIQUES EXPORTÉES: {export_file}", "blue")


if __name__ == "__main__":
    asyncio.run(main())
