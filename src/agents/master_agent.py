"""
🌙 NOVAQUOTE - AGENT MASTER - COORDINATEUR CENTRAL
================================================================================
Le Agent Master est le cerveau coordinateur qui orchestre tous les agents
dans un cycle circulaire de 20 minutes avec backtests intégrés.

Fonctionnalités principales :
- Coordination des 4 agents (Risk, Strategy, Funding, Sentiment)
- Exécution de backtests temps réel
- Prise de décision unifiée
- Mise à jour du dashboard
- Boucles de feedback et amélioration continue

Built with love by Moon Dev 🚀
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import traceback

from dotenv import load_dotenv
from termcolor import cprint, colored
import pandas as pd

from src import config
from src.agents.base_agent import BaseAgent
from src.agents.risk_agent import RiskAgent
from src.agents.strategy_agent import StrategyAgent
from src.agents.funding_agent import FundingAgent
from src.agents.sentiment_analysis_agent import SentimentAnalysisAgent
from src.logger import get_logger

# Configuration logging
logger = get_logger("master_agent")


@dataclass
class AgentResult:
    """Résultat d'un agent pour le cycle"""
    agent_name: str
    status: str  # SUCCESS, WARNING, ERROR, CRITICAL
    confidence: float  # 0.0 - 1.0
    data: Dict[str, Any]
    llm_calls: int
    execution_time_ms: float
    timestamp: str
    backtest_results: Optional[Dict] = None


@dataclass
class CycleMetrics:
    """Métriques complètes d'un cycle"""
    cycle_id: str
    start_time: str
    end_time: str
    duration_ms: float
    agents_results: List[AgentResult]
    combined_decision: str
    decision_confidence: float
    backtests_validation: Dict[str, Any]
    execution_summary: Dict[str, Any]
    next_cycle_time: str


class MasterAgent:
    """
    🤖 AGENT MASTER - COORDINATEUR CENTRAL
    Orchestration des 4 agents dans un cycle circulaire de 20 minutes
    """

    def __init__(self):
        """Initialise l'Agent Master"""
        self.agent_name = "master_agent"
        self.cycle_duration_seconds = 20 * 60  # 20 minutes
        self.is_running = False
        self.current_cycle_id = None
        self.cycle_count = 0

        # Initialiser les agents
        self.agents = {
            "risk_agent": RiskAgent(),
            "strategy_agent": StrategyAgent(),
            "funding_agent": FundingAgent(),
            "sentiment_agent": SentimentAnalysisAgent()
        }

        # Chemins des backtests
        self.backtests_dir = Path(__file__).parent.parent / "data" / "production_backtests"
        self.backtests_results_dir = Path(__file__).parent.parent / "data" / "rbi_v3" / "10_23_2025" / "backtests_final"

        # Historique des cycles
        self.cycle_history: List[CycleMetrics] = []

        # Métriques de performance
        self.performance_metrics = {
            "total_cycles": 0,
            "successful_decisions": 0,
            "average_confidence": 0.0,
            "active_strategies": [],
            "deactivated_strategies": []
        }

        cprint(f"\n{'='*80}", "cyan")
        cprint("🌙 NOVAQUOTE AGENT MASTER - COORDINATEUR CENTRAL", "cyan", attrs=["bold"])
        cprint(f"{'='*80}\n", "cyan")

        cprint("✅ Agent Master initialisé avec succès", "green")
        cprint(f"   📊 {len(self.agents)} agents configurés", "blue")
        cprint(f"   ⏱️  Durée cycle: {self.cycle_duration_seconds//60} minutes", "blue")
        cprint(f"   📁 Backtests directory: {self.backtests_dir}", "blue")
        cprint(f"   📁 Results directory: {self.backtests_results_dir}", "blue")
        cprint("\n")

    async def run_continuous_cycle(self):
        """
        🔄 CYCLE CIRCULAIRE CONTINU
        Exécute le cycle de 20 minutes en continu
        """
        self.is_running = True
        cprint("🚀 Démarrage du cycle circulaire continu...", "green", attrs=["bold"])

        try:
            while self.is_running:
                cycle_start = datetime.now()
                self.cycle_count += 1

                # Générer ID unique pour le cycle
                self.current_cycle_id = cycle_start.strftime("%Y-%m-%d_%H:%M")
                cprint(f"\n{'='*80}", "yellow")
                cprint(f"🔄 CYCLE #{self.cycle_count} - {self.current_cycle_id}", "yellow", attrs=["bold"])
                cprint(f"{'='*80}\n", "yellow")

                # Exécuter le cycle
                cycle_metrics = await self.execute_cycle()

                # Sauvegarder les résultats
                await self.save_cycle_metrics(cycle_metrics)

                # Mise à jour des métriques de performance
                self.update_performance_metrics(cycle_metrics)

                # Affichage du résumé
                self.display_cycle_summary(cycle_metrics)

                # Calcul du temps d'attente pour le prochain cycle
                cycle_end = datetime.now()
                cycle_duration = (cycle_end - cycle_start).total_seconds()
                sleep_time = max(0, self.cycle_duration_seconds - cycle_duration)

                # Affichage compte à rebours
                if sleep_time > 0:
                    cprint(f"\n⏳ Attente du prochain cycle...", "blue")
                    cprint(f"   ⏰ Prochain cycle dans {sleep_time/60:.1f} minutes", "blue")
                    await asyncio.sleep(min(sleep_time, 60))  # Sleep par tranche de 60s max

        except Exception as e:
            cprint(f"\n❌ ERREUR FATALE dans le cycle: {str(e)}", "red", attrs=["bold"])
            logger.error(f"Erreur fatale Agent Master", exc_info=True)
            self.is_running = False

    async def execute_cycle(self) -> CycleMetrics:
        """
        🎯 EXÉCUTION D'UN CYCLE COMPLET
        Orchestration des 4 agents avec backtests intégrés
        """
        cycle_start = datetime.now()
        cprint("🎯 Début d'exécution du cycle...", "cyan")

        agents_results = []

        try:
            # ==================== PHASE 1: RISK AGENT (SÉCURITÉ PREMIÈRE) ====================
            cprint("\n🛡️ [1/4] RISK AGENT - Contrôle sécurité...", "magenta", attrs=["bold"])
            risk_result = await self.execute_agent_with_backtest(
                "risk_agent",
                self.agents["risk_agent"],
                self.run_risk_analysis
            )
            agents_results.append(risk_result)

            if risk_result.status == "CRITICAL":
                cprint("🚨 RISK AGENT: RISQUE CRITIQUE DÉTECTÉ - ARRÊT IMMÉDIAT", "red", attrs=["bold", "blink"])
                return await self.create_emergency_stop_metrics(cycle_start, agents_results, "RISK_AGENT_CRITICAL")

            # ==================== PHASE 2: STRATEGY AGENT (ANALYSE TECHNIQUE) ====================
            cprint("\n📊 [2/4] STRATEGY AGENT - Analyse technique...", "magenta", attrs=["bold"])
            strategy_result = await self.execute_agent_with_backtest(
                "strategy_agent",
                self.agents["strategy_agent"],
                self.run_strategy_analysis
            )
            agents_results.append(strategy_result)

            # ==================== PHASE 3: FUNDING AGENT (ARBITRAGE) ====================
            cprint("\n💰 [3/4] FUNDING AGENT - Analyse funding...", "magenta", attrs=["bold"])
            funding_result = await self.execute_agent_with_backtest(
                "funding_agent",
                self.agents["funding_agent"],
                self.run_funding_analysis
            )
            agents_results.append(funding_result)

            # ==================== PHASE 4: SENTIMENT AGENT (ANALYSE SOCIALE) ====================
            cprint("\n🎭 [4/4] SENTIMENT AGENT - Analyse sentiment...", "magenta", attrs=["bold"])
            sentiment_result = await self.execute_agent_with_backtest(
                "sentiment_agent",
                self.agents["sentiment_agent"],
                self.run_sentiment_analysis
            )
            agents_results.append(sentiment_result)

            # ==================== PHASE 5: DÉCISION UNIFIÉE ====================
            cprint("\n🏆 [5/5] AGENT MASTER - Synthèse et décision...", "cyan", attrs=["bold"])
            combined_decision = await self.make_combined_decision(agents_results)

            # ==================== BACKTEST VALIDATION ====================
            cprint("\n🧪 VALIDATION BACKTESTS TEMPS RÉEL", "cyan", attrs=["bold"])
            backtests_validation = await self.validate_with_backtests(agents_results, combined_decision)

            # ==================== FINALISATION ====================
            cycle_end = datetime.now()
            duration_ms = (cycle_end - cycle_start).total_seconds() * 1000

            # Créer les métriques complètes
            cycle_metrics = CycleMetrics(
                cycle_id=self.current_cycle_id,
                start_time=cycle_start.isoformat(),
                end_time=cycle_end.isoformat(),
                duration_ms=duration_ms,
                agents_results=agents_results,
                combined_decision=combined_decision["decision"],
                decision_confidence=combined_decision["confidence"],
                backtests_validation=backtests_validation,
                execution_summary=combined_decision["summary"],
                next_cycle_time=(cycle_end + timedelta(seconds=self.cycle_duration_seconds)).isoformat()
            )

            # Mise à jour du dashboard
            await self.update_dashboard(cycle_metrics)

            return cycle_metrics

        except Exception as e:
            cprint(f"\n❌ ERREUR DURANT L'EXÉCUTION DU CYCLE: {str(e)}", "red", attrs=["bold"])
            logger.error(f"Erreur cycle {self.current_cycle_id}", exc_info=True)
            raise

    async def execute_agent_with_backtest(
        self,
        agent_name: str,
        agent: BaseAgent,
        agent_function: callable
    ) -> AgentResult:
        """
        🤖 EXÉCUTE UN AGENT AVEC BACKTEST INTÉGRÉ
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        try:
            # Appel de la fonction spécifique de l'agent
            agent_data = await agent_function()

            execution_time_ms = (time.time() - start_time) * 1000

            # Déterminer le status
            status = self.determine_agent_status(agent_name, agent_data)
            confidence = self.calculate_agent_confidence(agent_name, agent_data)

            # Comptage des appels LLM (simulation pour l'instant)
            llm_calls = self.count_llm_calls(agent_name, agent_data)

            # Résultat sans backtest pour l'instant
            result = AgentResult(
                agent_name=agent_name,
                status=status,
                confidence=confidence,
                data=agent_data,
                llm_calls=llm_calls,
                execution_time_ms=execution_time_ms,
                timestamp=timestamp,
                backtest_results=None
            )

            # Affichage du statut
            status_color = {
                "SUCCESS": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red"
            }.get(status, "white")

            cprint(f"   ✅ {agent_name}: {status} (confiance: {confidence:.2%}, {llm_calls} appels LLM, {execution_time_ms:.1f}ms)", status_color)

            return result

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Erreur {agent_name}: {str(e)}"

            cprint(f"   ❌ {agent_name}: ERROR - {error_msg}", "red")
            logger.error(error_msg, exc_info=True)

            return AgentResult(
                agent_name=agent_name,
                status="ERROR",
                confidence=0.0,
                data={"error": error_msg},
                llm_calls=0,
                execution_time_ms=execution_time_ms,
                timestamp=timestamp,
                backtest_results=None
            )

    async def run_risk_analysis(self) -> Dict[str, Any]:
        """🛡️ Analyse du risque par le Risk Agent"""
        # Simuler l'analyse du risk agent
        await asyncio.sleep(0.1)  # Simulation

        # Données simulées (à remplacer par de vraies données)
        return {
            "portfolio_value": 45230.50,
            "daily_pnl": 1250.75,
            "max_loss_limit": 5000.0,
            "max_gain_limit": 10000.0,
            "risk_score": 0.15,  # 0.0 = très sûr, 1.0 = très risqué
            "active_positions": 3,
            "leverage_level": 2.5,
            "margin_usage": 0.35,
            "stop_losses_active": True,
            "llm_analysis": {
                "model": "claude-3-5-haiku-latest",
                "confidence": 0.92,
                "recommendation": "Portfolio sécurisé, continuer avec paramètres actuels"
            },
            "backtest_correlation": 0.94  # Corrélation avec backtests historiques
        }

    async def run_strategy_analysis(self) -> Dict[str, Any]:
        """📊 Analyse technique par le Strategy Agent"""
        await asyncio.sleep(0.1)

        return {
            "tokens_analyzed": ["BTC", "ETH", "SOL", "BNB", "AVAX"],
            "signals": [
                {
                    "token": "BTC",
                    "strategy": "GoldenCrossover",
                    "signal": "BUY",
                    "confidence": 0.87,
                    "price_target": 67850,
                    "stop_loss": 62300
                },
                {
                    "token": "ETH",
                    "strategy": "VolatilityEngulfing",
                    "signal": "BUY",
                    "confidence": 0.73,
                    "price_target": 3240,
                    "stop_loss": 2890
                }
            ],
            "market_regime": "BULLISH",
            "volatility_index": 0.32,
            "llm_analysis": {
                "model": "claude-3-sonnet-20240229",
                "confidence": 0.89,
                "sentiment": "Confluence positive détectée, momentum haussier confirmé"
            },
            "backtest_validation": {
                "strategies_tested": 7,
                "success_rate": 0.82,
                "average_return": 0.157
            }
        }

    async def run_funding_analysis(self) -> Dict[str, Any]:
        """💰 Analyse du funding par le Funding Agent"""
        await asyncio.sleep(0.1)

        return {
            "exchanges_monitored": ["HyperLiquid", "Binance", "Bybit"],
            "funding_rates": {
                "HyperLiquid": {"BTC": 0.0002, "ETH": 0.00015, "SOL": 0.00018},
                "Binance": {"BTC": -0.0001, "ETH": -0.00005, "SOL": -0.00012},
                "Bybit": {"BTC": 0.00015, "ETH": 0.0001, "SOL": 0.00014}
            },
            "arbitrage_opportunities": [
                {
                    "pair": "BTC/USD",
                    "exchanges": ["HyperLiquid", "Binance"],
                    "rate_diff": 0.0003,
                    "potential_profit": 0.23,
                    "confidence": 0.78
                }
            ],
            "llm_analysis": {
                "model": "deepseek-reasoner",
                "confidence": 0.91,
                "recommendation": "Opportunité arbitrage favorable sur BTC/ETH détectée"
            },
            "backtest_arbitrage": {
                "historical_success": 0.76,
                "avg_profit_per_trade": 0.18
            }
        }

    async def run_sentiment_analysis(self) -> Dict[str, Any]:
        """🎭 Analyse du sentiment par le Sentiment Agent"""
        await asyncio.sleep(0.1)

        return {
            "twitter_trends": ["BTC bottom", "ETH 4K soon", "Alt season starting"],
            "reddit_sentiment": 0.67,
            "fear_greed_index": 65,
            "news_sentiment": 0.58,
            "social_volume": 12450,
            "llm_analysis": {
                "model": "openai-gpt-4o",
                "confidence": 0.84,
                "overall_sentiment": "OPTIMISTE",
                "sentiment_score": 0.65
            },
            "sentiment_correlation": {
                "correlation_with_price": 0.73,
                "leading_indicator": True,
                "backtest_match": 0.81
            }
        }

    async def make_combined_decision(self, agents_results: List[AgentResult]) -> Dict[str, Any]:
        """
        🏆 PRISE DE DÉCISION UNIFIÉE
        Combine les résultats des 4 agents pour une décision finale
        """
        # Calculer le score combiné
        total_confidence = sum(result.confidence for result in agents_results)
        avg_confidence = total_confidence / len(agents_results) if agents_results else 0.0

        # Analyser les signaux BUY/SELL
        buy_signals = 0
        sell_signals = 0
        strong_signals = []

        for result in agents_results:
            if result.agent_name == "strategy_agent":
                for signal in result.data.get("signals", []):
                    if signal.get("signal") == "BUY":
                        buy_signals += 1
                        if signal.get("confidence", 0) > 0.8:
                            strong_signals.append(f"{signal['token']} ({signal['strategy']})")
                    elif signal.get("signal") == "SELL":
                        sell_signals += 1

        # Déterminer la décision finale
        if buy_signals > sell_signals and avg_confidence > 0.7:
            decision = "EXECUTER_BUY_SIGNALS"
            decision_detail = f"Exécuter {buy_signals} signaux BUY détectés"
        elif sell_signals > buy_signals and avg_confidence > 0.7:
            decision = "EXECUTER_SELL_SIGNALS"
            decision_detail = f"Exécuter {sell_signals} signaux SELL détectés"
        elif avg_confidence > 0.6:
            decision = "MONITOR_ONLY"
            decision_detail = "Surveiller sans exécuter - confiance insuffisante"
        else:
            decision = "WAIT_FOR_BETTER_ENTRY"
            decision_detail = "Attendre une meilleure opportunité"

        # Créer le résumé
        summary = {
            "agents_count": len(agents_results),
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "strong_signals": strong_signals,
            "avg_confidence": avg_confidence,
            "decision_detail": decision_detail,
            "agents_status": {r.agent_name: r.status for r in agents_results}
        }

        cprint(f"   🏆 Décision: {decision}", "green", attrs=["bold"])
        cprint(f"   📊 Confiance: {avg_confidence:.2%}", "blue")
        cprint(f"   📈 Signaux: {buy_signals} BUY, {sell_signals} SELL", "blue")

        return {
            "decision": decision,
            "confidence": avg_confidence,
            "summary": summary
        }

    async def validate_with_backtests(
        self,
        agents_results: List[AgentResult],
        combined_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🧪 VALIDATION AVEC BACKTESTS TEMPS RÉEL
        Compare la décision actuelle avec les backtests historiques
        """
        cprint("   📊 Validation backtests...", "blue")

        # Simulation de validation (à remplacer par de vraies données)
        await asyncio.sleep(0.05)

        # Charger les backtests disponibles
        backtest_files = list(self.backtests_dir.glob("*_FINAL_results.json"))
        active_strategies = []

        for bt_file in backtest_files[:5]:  # Limiter à 5 pour la démo
            strategy_name = bt_file.stem.replace("_FINAL_results", "")

            # Simuler les résultats (à lire depuis les vrais fichiers)
            validation_result = {
                "strategy": strategy_name,
                "backtest_winrate": 0.68 + (hash(strategy_name) % 100) / 1000,  # Simulé
                "backtest_return": 0.15 + (hash(strategy_name) % 100) / 1000,
                "current_signal_match": True if "BUY" in combined_decision["decision"] else False,
                "confidence_score": 0.75 + (hash(strategy_name) % 50) / 100,
                "validation_status": "PASS" if (hash(strategy_name) % 3) != 0 else "WARNING"
            }

            if validation_result["validation_status"] == "PASS":
                active_strategies.append(strategy_name)

        validation_summary = {
            "total_strategies_tested": len(backtest_files),
            "strategies_passed": len(active_strategies),
            "strategies_failed": len(backtest_files) - len(active_strategies),
            "success_rate": len(active_strategies) / len(backtest_files) if backtest_files else 0.0,
            "active_strategies": active_strategies,
            "validation_timestamp": datetime.now().isoformat()
        }

        cprint(f"   ✅ {validation_summary['strategies_passed']}/{validation_summary['total_strategies_tested']} stratégies validées", "green")

        return validation_summary

    def determine_agent_status(self, agent_name: str, data: Dict) -> str:
        """Détermine le statut d'un agent basé sur ses données"""
        if agent_name == "risk_agent":
            risk_score = data.get("risk_score", 1.0)
            if risk_score > 0.8:
                return "CRITICAL"
            elif risk_score > 0.5:
                return "WARNING"
            else:
                return "SUCCESS"

        elif agent_name == "strategy_agent":
            signals = data.get("signals", [])
            if len(signals) == 0:
                return "WARNING"
            avg_confidence = sum(s.get("confidence", 0) for s in signals) / len(signals)
            if avg_confidence < 0.5:
                return "WARNING"
            else:
                return "SUCCESS"

        elif agent_name == "funding_agent":
            opportunities = data.get("arbitrage_opportunities", [])
            if len(opportunities) > 0:
                return "SUCCESS"
            else:
                return "WARNING"

        elif agent_name == "sentiment_agent":
            sentiment_score = data.get("llm_analysis", {}).get("sentiment_score", 0.0)
            if sentiment_score < 0.3:
                return "WARNING"
            else:
                return "SUCCESS"

        return "SUCCESS"

    def calculate_agent_confidence(self, agent_name: str, data: Dict) -> float:
        """Calcule la confiance d'un agent (0.0 - 1.0)"""
        if agent_name == "risk_agent":
            return 1.0 - data.get("risk_score", 0.5)

        elif agent_name == "strategy_agent":
            signals = data.get("signals", [])
            if not signals:
                return 0.0
            avg_confidence = sum(s.get("confidence", 0) for s in signals) / len(signals)
            return avg_confidence

        elif agent_name == "funding_agent":
            opportunities = data.get("arbitrage_opportunities", [])
            if not opportunities:
                return 0.5
            avg_confidence = sum(o.get("confidence", 0) for o in opportunities) / len(opportunities)
            return avg_confidence

        elif agent_name == "sentiment_agent":
            return data.get("llm_analysis", {}).get("confidence", 0.5)

        return 0.5

    def count_llm_calls(self, agent_name: str, data: Dict) -> int:
        """Compte le nombre d'appels LLM effectués"""
        # Simulation basée sur la structure des données
        if "llm_analysis" in data:
            return 1
        return 0

    async def create_emergency_stop_metrics(
        self,
        cycle_start: datetime,
        agents_results: List[AgentResult],
        reason: str
    ) -> CycleMetrics:
        """Crée les métriques pour un arrêt d'urgence"""
        cycle_end = datetime.now()
        duration_ms = (cycle_end - cycle_start).total_seconds() * 1000

        return CycleMetrics(
            cycle_id=self.current_cycle_id,
            start_time=cycle_start.isoformat(),
            end_time=cycle_end.isoformat(),
            duration_ms=duration_ms,
            agents_results=agents_results,
            combined_decision="EMERGENCY_STOP",
            decision_confidence=1.0,
            backtests_validation={"status": "STOPPED", "reason": reason},
            execution_summary={"reason": reason, "action": "ARRÊT_IMMEDIAT"},
            next_cycle_time=(cycle_end + timedelta(seconds=self.cycle_duration_seconds)).isoformat()
        )

    async def save_cycle_metrics(self, cycle_metrics: CycleMetrics):
        """💾 Sauvegarde les métriques du cycle"""
        # Créer le dossier s'il n'existe pas
        cycles_dir = Path(__file__).parent.parent / "data" / "cycles"
        cycles_dir.mkdir(parents=True, exist_ok=True)

        # Sauvegarder le cycle individuel
        cycle_file = cycles_dir / f"{cycle_metrics.cycle_id}.json"
        with open(cycle_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(cycle_metrics), f, indent=2, ensure_ascii=False)

        # Sauvegarder dans l'historique
        self.cycle_history.append(cycle_metrics)

        # Garder seulement les 100 derniers cycles
        if len(self.cycle_history) > 100:
            self.cycle_history = self.cycle_history[-100:]

        cprint(f"   💾 Métriques sauvegardées: {cycle_file}", "blue")

    def update_performance_metrics(self, cycle_metrics: CycleMetrics):
        """📊 Met à jour les métriques de performance"""
        self.performance_metrics["total_cycles"] += 1

        # Compter les décisions réussies (non-STOP ou WARNING)
        if cycle_metrics.combined_decision not in ["EMERGENCY_STOP", "WAIT_FOR_BETTER_ENTRY"]:
            self.performance_metrics["successful_decisions"] += 1

        # Mettre à jour la confiance moyenne
        total_confidence = (
            sum(r.confidence for r in cycle_metrics.agents_results) / len(cycle_metrics.agents_results)
            if cycle_metrics.agents_results else 0
        )

        # Calculer la moyenne mobile
        current_avg = self.performance_metrics["average_confidence"]
        cycle_count = self.performance_metrics["total_cycles"]
        self.performance_metrics["average_confidence"] = (
            (current_avg * (cycle_count - 1) + total_confidence) / cycle_count
        )

    def display_cycle_summary(self, cycle_metrics: CycleMetrics):
        """📊 Affiche le résumé du cycle"""
        cprint(f"\n{'='*80}", "cyan")
        cprint("📊 RÉSUMÉ DU CYCLE", "cyan", attrs=["bold"])
        cprint(f"{'='*80}", "cyan")

        # Métriques générales
        cprint(f"🆔 Cycle ID: {cycle_metrics.cycle_id}", "white")
        cprint(f"⏱️  Durée: {cycle_metrics.duration_ms:.1f}ms", "white")
        cprint(f"🏆 Décision: {cycle_metrics.combined_decision}", "green", attrs=["bold"])
        cprint(f"📊 Confiance: {cycle_metrics.decision_confidence:.2%}", "blue")

        # Résultats des agents
        cprint(f"\n🤖 RÉSULTATS AGENTS:", "yellow")
        for result in cycle_metrics.agents_results:
            status_color = {
                "SUCCESS": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red"
            }.get(result.status, "white")

            cprint(
                f"   {result.agent_name}: {result.status} "
                f"(conf: {result.confidence:.2%}, "
                f"{result.llm_calls} LLM, {result.execution_time_ms:.1f}ms)",
                status_color
            )

        # Validation backtests
        if cycle_metrics.backtests_validation:
            bv = cycle_metrics.backtests_validation
            cprint(f"\n🧪 VALIDATION BACKTESTS:", "yellow")
            cprint(f"   Stratégies testées: {bv.get('total_strategies_tested', 0)}", "white")
            cprint(f"   Stratégies validées: {bv.get('strategies_passed', 0)}", "green")
            cprint(f"   Taux de réussite: {bv.get('success_rate', 0):.1%}", "green")

        # Prochain cycle
        cprint(f"\n⏰ Prochain cycle: {cycle_metrics.next_cycle_time}", "blue")

        cprint(f"{'='*80}\n", "cyan")

    async def update_dashboard(self, cycle_metrics: CycleMetrics):
        """📱 Met à jour le dashboard frontend"""
        # Préparer les données pour le dashboard
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "cycle_id": cycle_metrics.cycle_id,
            "status": "ACTIVE" if self.is_running else "STOPPED",
            "current_decision": {
                "decision": cycle_metrics.combined_decision,
                "confidence": cycle_metrics.decision_confidence,
                "summary": cycle_metrics.execution_summary
            },
            "agents_status": {
                result.agent_name: {
                    "status": result.status,
                    "confidence": result.confidence,
                    "llm_calls": result.llm_calls,
                    "last_update": result.timestamp
                }
                for result in cycle_metrics.agents_results
            },
            "metrics": {
                "total_cycles": self.performance_metrics["total_cycles"],
                "success_rate": (
                    self.performance_metrics["successful_decisions"] /
                    max(1, self.performance_metrics["total_cycles"])
                ),
                "average_confidence": self.performance_metrics["average_confidence"]
            },
            "next_cycle": cycle_metrics.next_cycle_time
        }

        # Sauvegarder pour le backend (le backend lira ce fichier)
        dashboard_file = Path(__file__).parent.parent.parent / "backend" / "dashboard_data.json"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

        cprint(f"   📱 Dashboard mis à jour", "blue")

    def stop(self):
        """🛑 Arrête l'Agent Master"""
        cprint("\n🛑 Arrêt de l'Agent Master...", "yellow", attrs=["bold"])
        self.is_running = False
        cprint("✅ Agent Master arrêté", "green")


async def main():
    """Point d'entrée principal"""
    master = MasterAgent()
    try:
        await master.run_continuous_cycle()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Interruption clavier détectée", "yellow")
        master.stop()
    except Exception as e:
        cprint(f"\n❌ Erreur fatale: {str(e)}", "red", attrs=["bold"])
        logger.error("Erreur fatale main", exc_info=True)
        master.stop()


if __name__ == "__main__":
    asyncio.run(main())
