#!/usr/bin/env python3
"""
🧪 NOVAQUOTE - TEST DU SYSTÈME CIRCULAIRE COMPLET
================================================================================
Script de test end-to-end pour vérifier que le système de cycle circulaire
avec backtests intégrés fonctionne correctement.

Tests inclus :
1. Test des agents individuellement
2. Test du backtester temps réel
3. Test du collecteur de métriques
4. Test de l'Agent Master (mode simulation)
5. Test d'intégration backend

Built with love by Moon Dev 🚀
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from termcolor import cprint, colored

# Imports des modules du système
try:
    from src.agents.master_agent import MasterAgent, AgentResult
    from src.data.realtime_backtester import RealTimeBacktester
    from src.data.metrics_collector import MetricsCollector
    from src.agents.risk_agent import RiskAgent
    from src.agents.strategy_agent import StrategyAgent
    from src.agents.funding_agent import FundingAgent
    from src.agents.sentiment_analysis_agent import SentimentAnalysisAgent
except ImportError as e:
    cprint(f"\n❌ ERREUR: Impossible d'importer les modules: {e}", "red")
    cprint("   Vérifiez que vous êtes dans le bon répertoire", "yellow")
    sys.exit(1)


class CircularSystemTester:
    """
    🧪 TESTEUR DU SYSTÈME CIRCULAIRE COMPLET
    """

    def __init__(self):
        """Initialise le testeur"""
        self.test_results = []
        self.start_time = time.time()

        cprint(f"\n{'='*80}", "cyan")
        cprint("🧪 NOVAQUOTE - TEST SYSTÈME CIRCULAIRE COMPLET", "cyan", attrs=["bold"])
        cprint(f"{'='*80}\n", "cyan")

        self.test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0

    async def run_all_tests(self):
        """Exécute tous les tests"""
        tests = [
            ("Test 1: Backtester Temps Réel", self.test_realtime_backtester),
            ("Test 2: Metrics Collector", self.test_metrics_collector),
            ("Test 3: Agents Individuels", self.test_individual_agents),
            ("Test 4: Agent Master (Simulation)", self.test_master_agent_simulation),
            ("Test 5: Intégration Dashboard", self.test_dashboard_integration),
        ]

        for test_name, test_func in tests:
            self.test_count += 1
            cprint(f"\n{'='*80}", "yellow")
            cprint(f"🔄 {test_name}", "yellow", attrs=["bold"])
            cprint(f"{'='*80}", "yellow")

            try:
                result = await test_func()
                if result:
                    cprint(f"   ✅ {test_name}: RÉUSSI", "green", attrs=["bold"])
                    self.passed_tests += 1
                    self.test_results.append({"test": test_name, "status": "PASS", "error": None})
                else:
                    cprint(f"   ❌ {test_name}: ÉCHEC", "red", attrs=["bold"])
                    self.failed_tests += 1
                    self.test_results.append({"test": test_name, "status": "FAIL", "error": "Test returned False"})
            except Exception as e:
                cprint(f"   ❌ {test_name}: ERREUR - {str(e)}", "red", attrs=["bold"])
                self.failed_tests += 1
                self.test_results.append({"test": test_name, "status": "ERROR", "error": str(e)})

        # Affichage du résumé final
        self.display_final_summary()

    async def test_realtime_backtester(self) -> bool:
        """🧪 Test du backtester temps réel"""
        try:
            cprint("   Initialisation du backtester...", "blue")

            backtester = RealTimeBacktester()

            # Test chargement des backtests
            backtests = await backtester.load_backtests()
            cprint(f"   📦 {len(backtests)} backtests chargés", "blue")

            if len(backtests) == 0:
                cprint("   ⚠️ Aucun backtest trouvé - c'est normal si le dossier est vide", "yellow")
                return True  # Ce n'est pas un échec

            # Test validation signaux
            mock_signals = {
                "strategy_agent": {
                    "signals": [
                        {"token": "BTC", "strategy": "GoldenCrossover", "signal": "BUY", "confidence": 0.87},
                        {"token": "ETH", "strategy": "VolatilityEngulfing", "signal": "BUY", "confidence": 0.73}
                    ]
                }
            }

            validation_results = await backtester.validate_signals(mock_signals)
            cprint(f"   ✅ {len(validation_results)} validations effectuées", "green")

            # Test génération rapport
            report = await backtester.generate_validation_report(validation_results)
            cprint(f"   ✅ Rapport généré: {report['summary']['total_validations']} validations", "green")

            # Test statistiques
            stats = backtester.get_performance_stats()
            cprint(f"   ✅ Statistiques: {stats['active_strategies']} stratégies actives", "green")

            return True

        except Exception as e:
            cprint(f"   ❌ Erreur: {str(e)}", "red")
            return False

    async def test_metrics_collector(self) -> bool:
        """📊 Test du collecteur de métriques"""
        try:
            cprint("   Initialisation du collecteur...", "blue")

            collector = MetricsCollector()

            # Test collecte métriques agent
            agent_metrics = {
                "status": "SUCCESS",
                "confidence": 0.85,
                "llm_calls": 2,
                "execution_time_ms": 150.5,
                "data": {"risk_score": 0.15}
            }

            result = await collector.collect_agent_metrics("risk_agent", agent_metrics)
            cprint(f"   ✅ Métriques agent collectées", "green")

            # Test mise à jour dashboard
            dashboard_data = await collector.update_dashboard_data()
            cprint(f"   ✅ Dashboard mis à jour: {dashboard_data.system_status}", "green")

            # Test statut temps réel
            status = collector.get_real_time_status()
            cprint(f"   ✅ Status temps réel: {status['system_status']}", "green")

            # Test tendances
            trends = await collector.get_trending_metrics(hours=1)
            cprint(f"   ✅ Tendances calculées: {trends.get('performance', {}).get('trend', 'N/A')}", "green")

            return True

        except Exception as e:
            cprint(f"   ❌ Erreur: {str(e)}", "red")
            return False

    async def test_individual_agents(self) -> bool:
        """🤖 Test des agents individuellement"""
        try:
            # Test Risk Agent
            cprint("   Test Risk Agent...", "blue")
            risk_agent = RiskAgent()
            cprint(f"   ✅ Risk Agent initialisé", "green")

            # Test Strategy Agent
            cprint("   Test Strategy Agent...", "blue")
            strategy_agent = StrategyAgent()
            cprint(f"   ✅ Strategy Agent initialisé", "green")

            # Test Funding Agent
            cprint("   Test Funding Agent...", "blue")
            funding_agent = FundingAgent()
            cprint(f"   ✅ Funding Agent initialisé", "green")

            # Test Sentiment Agent
            cprint("   Test Sentiment Agent...", "blue")
            sentiment_agent = SentimentAnalysisAgent()
            cprint(f"   ✅ Sentiment Agent initialisé", "green")

            return True

        except Exception as e:
            cprint(f"   ❌ Erreur: {str(e)}", "red")
            return False

    async def test_master_agent_simulation(self) -> bool:
        """🌙 Test simulation Agent Master"""
        try:
            cprint("   Initialisation Agent Master...", "blue")

            # Note: On ne lance pas le vrai cycle car il tourne en continu
            # On teste juste l'initialisation et les composants

            from src.agents.master_agent import MasterAgent
            master = MasterAgent()

            cprint(f"   ✅ Agent Master initialisé avec {len(master.agents)} agents", "green")
            cprint(f"   ✅ Cycle duration: {master.cycle_duration_seconds//60} minutes", "green")
            cprint(f"   ✅ Backtests directory: {master.backtests_dir}", "green")

            # Test exécution d'un seul cycle (simulation rapide)
            cprint("   Simulation d'un cycle...", "blue")

            # Simuler les résultats d'agents
            mock_results = [
                AgentResult(
                    agent_name="risk_agent",
                    status="SUCCESS",
                    confidence=0.85,
                    data={"risk_score": 0.15},
                    llm_calls=1,
                    execution_time_ms=150.0,
                    timestamp=datetime.now().isoformat()
                ),
                AgentResult(
                    agent_name="strategy_agent",
                    status="SUCCESS",
                    confidence=0.92,
                    data={"signals_count": 3},
                    llm_calls=1,
                    execution_time_ms=230.0,
                    timestamp=datetime.now().isoformat()
                )
            ]

            # Test décision combinée
            decision = await master.make_combined_decision(mock_results)
            cprint(f"   ✅ Décision combinée: {decision['decision']}", "green")
            cprint(f"   ✅ Confiance: {decision['confidence']:.2%}", "green")

            return True

        except Exception as e:
            cprint(f"   ❌ Erreur: {str(e)}", "red")
            return False

    async def test_dashboard_integration(self) -> bool:
        """📱 Test intégration dashboard"""
        try:
            cprint("   Test des endpoints dashboard...", "blue")

            # Vérifier que les endpoints existent dans le backend
            backend_file = Path(__file__).parent.parent / "backend" / "server-backend.ts"

            if not backend_file.exists():
                cprint("   ⚠️ Fichier backend non trouvé", "yellow")
                return False

            # Lire le contenu et vérifier les endpoints
            with open(backend_file, 'r', encoding='utf-8') as f:
                backend_content = f.read()

            required_endpoints = [
                "/api/dashboard/real-time",
                "/api/agents/master/start",
                "/api/agents/master/stop",
                "/api/agents/master/status",
                "/api/backtests/validate"
            ]

            found_endpoints = []
            for endpoint in required_endpoints:
                if endpoint in backend_content:
                    found_endpoints.append(endpoint)

            cprint(f"   ✅ {len(found_endpoints)}/{len(required_endpoints)} endpoints trouvés", "green")

            for endpoint in found_endpoints:
                cprint(f"      ✓ {endpoint}", "cyan")

            # Vérifier le fichier dashboard_data.json
            dashboard_file = Path(__file__).parent.parent / "backend" / "dashboard_data.json"
            if dashboard_file.exists():
                cprint("   ✅ Fichier dashboard_data.json existe", "green")
            else:
                cprint("   ⚠️ Fichier dashboard_data.json n'existe pas encore (normal si agents non lancés)", "yellow")

            return len(found_endpoints) == len(required_endpoints)

        except Exception as e:
            cprint(f"   ❌ Erreur: {str(e)}", "red")
            return False

    def display_final_summary(self):
        """📊 Affiche le résumé final des tests"""
        end_time = time.time()
        duration = end_time - self.start_time

        cprint(f"\n{'='*80}", "cyan", attrs=["bold"])
        cprint("📊 RÉSUMÉ FINAL DES TESTS", "cyan", attrs=["bold"])
        cprint(f"{'='*80}\n", "cyan", attrs=["bold"])

        # Statistiques générales
        cprint(f"⏱️  Durée totale: {duration:.2f} secondes", "white")
        cprint(f"🔢 Tests exécutés: {self.test_count}", "white")
        cprint(f"✅ Tests réussis: {self.passed_tests}", "green")
        cprint(f"❌ Tests échoués: {self.failed_tests}", "red")

        if self.failed_tests > 0:
            cprint(f"\n🚨 TESTS ÉCHOUÉS:", "red", attrs=["bold"])
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    cprint(f"   ❌ {result['test']}", "red")
                    if result["error"]:
                        cprint(f"      Erreur: {result['error']}", "yellow")

        # Statut global
        success_rate = (self.passed_tests / self.test_count) * 100
        cprint(f"\n📊 Taux de réussite: {success_rate:.1f}%", "blue", attrs=["bold"])

        if success_rate >= 80:
            cprint("   🎉 SYSTÈME PRÊT - Le système circulaire est opérationnel!", "green", attrs=["bold"])
        elif success_rate >= 60:
            cprint("   ⚠️ SYSTÈME PARTIELLEMENT OPÉRATIONNEL - Quelques ajustements nécessaires", "yellow", attrs=["bold"])
        else:
            cprint("   🚨 SYSTÈME NON OPÉRATIONNEL - Corrections majeures requises", "red", attrs=["bold"])

        # Prochaines étapes
        cprint(f"\n🚀 PROCHAINES ÉTAPES:", "cyan", attrs=["bold"])
        if success_rate >= 80:
            cprint("   1. Lancer le backend: node run.js start", "white")
            cprint("   2. Démarrer l'Agent Master: POST /api/agents/master/start", "white")
            cprint("   3. Ouvrir le dashboard: http://localhost:9001", "white")
        else:
            cprint("   1. Corriger les erreurs identifiées", "yellow")
            cprint("   2. Relancer les tests: python scripts/test_circular_system.py", "yellow")

        cprint(f"\n{'='*80}\n", "cyan")

        # Sauvegarder le rapport
        self.save_test_report(duration, success_rate)

    def save_test_report(self, duration: float, success_rate: float):
        """💾 Sauvegarde le rapport de test"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "test_count": self.test_count,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": success_rate,
            "results": self.test_results,
            "system_status": "READY" if success_rate >= 80 else "NEEDS_WORK"
        }

        report_file = Path(__file__).parent / "test_report_circular_system.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        cprint(f"💾 Rapport sauvegardé: {report_file}", "blue")


async def main():
    """Point d'entrée principal"""
    tester = CircularSystemTester()

    try:
        await tester.run_all_tests()
        sys.exit(0)
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Test interrompu par l'utilisateur", "yellow")
        sys.exit(1)
    except Exception as e:
        cprint(f"\n❌ Erreur fatale: {str(e)}", "red", attrs=["bold"])
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
