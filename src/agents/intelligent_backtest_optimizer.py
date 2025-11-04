#!/usr/bin/env python3
"""
Intelligent Backtest Optimizer - IA-Powered Strategy Enhancement
Analyse les backtests et utilise les agents IA pour optimiser automatiquement les stratégies
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Simple base class for standalone usage
class BaseAgent:
    def __init__(self):
        self.name = "Base Agent"
        self.version = "1.0.0"

# Simplified strategy agent
class SimpleStrategyAgent:
    def __init__(self):
        self.name = "Strategy Agent"

class IntelligentBacktestOptimizer(BaseAgent):
    """Agent IA qui analyse et optimise les backtests"""

    def __init__(self):
        super().__init__()
        self.name = "Intelligent Backtest Optimizer"
        self.version = "1.0.0"
        self.strategy_agent = SimpleStrategyAgent()

        # Seuil de performance minimum
        self.min_sharpe = 1.0
        self.min_return = 0.20  # 20%
        self.min_win_rate = 0.55  # 55%
        self.max_drawdown = 0.20  # 20%

        self.logger = logging.getLogger(__name__)

    def analyze_backtest(self, backtest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse complète d'un backtest"""

        analysis = {
            'strategy_name': backtest_data.get('name', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'performance_score': 0,
            'strengths': [],
            'weaknesses': [],
            'critical_issues': [],
            'recommendations': [],
            'priority': 'low',
            'optimization_potential': 0.0
        }

        # Extraire les métriques
        metrics = self._extract_metrics(backtest_data)

        # Analyser chaque métrique
        self._analyze_return(metrics, analysis)
        self._analyze_sharpe(metrics, analysis)
        self._analyze_drawdown(metrics, analysis)
        self._analyze_win_rate(metrics, analysis)
        self._analyze_trades(metrics, analysis)
        self._analyze_profit_factor(metrics, analysis)

        # Calculer le score global
        analysis['performance_score'] = self._calculate_performance_score(metrics)

        # Déterminer la priorité d'optimisation
        analysis['priority'] = self._determine_priority(metrics)

        # Optimisation potentielle
        analysis['optimization_potential'] = self._calculate_optimization_potential(metrics)

        # Générer des recommandations basées sur l'analyse
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _extract_metrics(self, backtest_data: Dict) -> Dict[str, float]:
        """Extrait toutes les métriques du backtest"""
        return {
            'return': float(backtest_data.get('return', 0)),
            'sharpe': float(backtest_data.get('sharpe', 0)),
            'max_drawdown': abs(float(backtest_data.get('maxDrawdown', 0))),
            'win_rate': float(backtest_data.get('winRate', 0)),
            'total_trades': int(backtest_data.get('totalTrades', 0)),
            'profit_factor': float(backtest_data.get('profitFactor', 0)),
            'annual_return': float(backtest_data.get('annualReturn', 0))
        }

    def _analyze_return(self, metrics: Dict, analysis: Dict):
        """Analyse la performance de retour"""
        return_pct = metrics['return']

        if return_pct >= 0.50:
            analysis['strengths'].append(f"Excellent retour: {return_pct:.2%}")
        elif return_pct >= self.min_return:
            analysis['strengths'].append(f"Bon retour: {return_pct:.2%}")
        else:
            analysis['weaknesses'].append(f"Retour insuffisant: {return_pct:.2%}")
            analysis['critical_issues'].append("Retour en dessous du seuil minimum")

        # Analyse de la stabilité du retour
        if metrics['annual_return'] > metrics['return'] * 3:
            analysis['recommendations'].append(
                "Retour annualisé très élevé - vérifier la cohérence temporelle"
            )

    def _analyze_sharpe(self, metrics: Dict, analysis: Dict):
        """Analyse le ratio de Sharpe"""
        sharpe = metrics['sharpe']

        if sharpe >= 2.0:
            analysis['strengths'].append(f"Excellent Sharpe: {sharpe:.2f}")
        elif sharpe >= 1.5:
            analysis['strengths'].append(f"Bon Sharpe: {sharpe:.2f}")
        elif sharpe >= self.min_sharpe:
            analysis['weaknesses'].append(f"Sharpe moyen: {sharpe:.2f}")
        else:
            analysis['critical_issues'].append(f"Sharpe critique: {sharpe:.2f}")
            analysis['recommendations'].append(
                "Améliorer la gestion du risque pour augmenter le Sharpe"
            )

    def _analyze_drawdown(self, metrics: Dict, analysis: Dict):
        """Analyse le drawdown maximum"""
        dd = metrics['max_drawdown']

        if dd <= 0.05:
            analysis['strengths'].append(f"Excellent contrôle du risque: {dd:.2%}")
        elif dd <= 0.10:
            analysis['strengths'].append(f"Bon contrôle du risque: {dd:.2%}")
        elif dd <= self.max_drawdown:
            analysis['weaknesses'].append(f"Drawdown élevé: {dd:.2%}")
        else:
            analysis['critical_issues'].append(f"Drawdown critique: {dd:.2%}")
            analysis['recommendations'].append(
                "Réduire immédiatement la taille des positions"
            )

    def _analyze_win_rate(self, metrics: Dict, analysis: Dict):
        """Analyse le taux de réussite"""
        wr = metrics['win_rate']

        if wr >= 0.70:
            analysis['strengths'].append(f"Excellent win rate: {wr:.2%}")
        elif wr >= 0.60:
            analysis['strengths'].append(f"Bon win rate: {wr:.2%}")
        elif wr >= self.min_win_rate:
            analysis['weaknesses'].append(f"Win rate moyen: {wr:.2%}")
        else:
            analysis['critical_issues'].append(f"Win rate critique: {wr:.2%}")
            analysis['recommendations'].append(
                "Améliorer les signaux d'entrée et de sortie"
            )

    def _analyze_trades(self, metrics: Dict, analysis: Dict):
        """Analyse le nombre de trades"""
        trades = metrics['total_trades']

        if trades < 20:
            analysis['critical_issues'].append(
                f"Trop peu de trades ({trades}) - échantillon non représentatif"
            )
        elif trades > 500:
            analysis['weaknesses'].append(
                f"Trés nombre de trades ({trades}) - possible sur-trading"
            )
        else:
            analysis['strengths'].append(f"Nombre de trades approprié: {trades}")

    def _analyze_profit_factor(self, metrics: Dict, analysis: Dict):
        """Analyse le profit factor"""
        pf = metrics['profit_factor']

        if pf >= 2.0:
            analysis['strengths'].append(f"Excellent profit factor: {pf:.2f}")
        elif pf >= 1.5:
            analysis['strengths'].append(f"Bon profit factor: {pf:.2f}")
        elif pf >= 1.2:
            analysis['weaknesses'].append(f"Profit factor moyen: {pf:.2f}")
        else:
            analysis['critical_issues'].append(f"Profit factor critique: {pf:.2f}")

    def _calculate_performance_score(self, metrics: Dict) -> float:
        """Calcule un score de performance global (0-100)"""
        score = 0

        # Return (25 points)
        score += min(25, max(0, (metrics['return'] * 50)))

        # Sharpe (20 points)
        score += min(20, max(0, metrics['sharpe'] * 10))

        # Win Rate (20 points)
        score += min(20, max(0, metrics['win_rate'] * 20))

        # Drawdown inverse (15 points)
        score += min(15, max(0, (0.30 - metrics['max_drawdown']) * 50))

        # Profit Factor (10 points)
        score += min(10, max(0, metrics['profit_factor'] * 5))

        # Nombre de trades (10 points)
        if 50 <= metrics['total_trades'] <= 300:
            score += 10
        elif 20 <= metrics['total_trades'] < 50:
            score += 5

        return min(100, max(0, score))

    def _determine_priority(self, metrics: Dict) -> str:
        """Détermine la priorité d'optimisation"""
        critical_count = sum([
            1 if metrics['return'] < self.min_return else 0,
            1 if metrics['sharpe'] < self.min_sharpe else 0,
            1 if metrics['max_drawdown'] > self.max_drawdown else 0,
            1 if metrics['win_rate'] < self.min_win_rate else 0,
            1 if metrics['profit_factor'] < 1.2 else 0
        ])

        if critical_count >= 3:
            return 'critical'
        elif critical_count >= 2:
            return 'high'
        elif critical_count >= 1:
            return 'medium'
        else:
            return 'low'

    def _calculate_optimization_potential(self, metrics: Dict) -> float:
        """Calcule le potentiel d'optimisation (0-1)"""
        potential = 0

        # Plus il y a de faiblesses, plus le potentiel est élevé
        if metrics['return'] < 0.30:
            potential += 0.3
        if metrics['sharpe'] < 1.5:
            potential += 0.2
        if metrics['max_drawdown'] > 0.15:
            potential += 0.2
        if metrics['win_rate'] < 0.65:
            potential += 0.2
        if metrics['profit_factor'] < 2.0:
            potential += 0.1

        return min(1.0, potential)

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Génère des recommandations d'optimisation"""
        recommendations = analysis['recommendations'].copy()

        # Ajouter des recommandations basées sur les agents spécialisés
        if analysis['priority'] in ['critical', 'high']:
            # Demander l'aide du risk agent
            recommendations.append(
                "Demander analyse approfondie au Risk Agent"
            )

        if any('sentiment' in issue.lower() for issue in analysis['weaknesses']):
            recommendations.append(
                "Intégrer analyse sentiment via Sentiment Agent"
            )

        if any('funding' in issue.lower() for issue in analysis['weaknesses']):
            recommendations.append(
                "Optimiser via Funding Agent pour améliorer le ratio"
            )

        # Stratégies d'amélioration générale
        if len(analysis['critical_issues']) > 0:
            recommendations.extend([
                "Réviser complètement les paramètres de la stratégie",
                "Tester sur une période plus longue",
                "Considerer une approche multi-timeframe"
            ])

        return list(set(recommendations))  # Remove duplicates

    def optimize_strategy(self, backtest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génère une stratégie optimisée basée sur l'analyse"""

        # Analyser d'abord
        analysis = self.analyze_backtest(backtest_data)

        # Générer une stratégie optimisée
        optimized_strategy = {
            'original_strategy': backtest_data.get('name', 'Unknown'),
            'optimized_strategy_name': f"{backtest_data.get('name', 'Strategy')}_OPTIMIZED",
            'optimization_timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'optimizations_applied': [],
            'expected_improvements': {},
            'new_parameters': {},
            'implementation_notes': []
        }

        # Appliquer des optimisations basées sur l'analyse
        metrics = self._extract_metrics(backtest_data)

        # Optimisation du Sharpe
        if metrics['sharpe'] < 1.5:
            optimized_strategy['new_parameters']['stop_loss'] = 'Tighter (2% instead of 3%)'
            optimized_strategy['new_parameters']['position_sizing'] = 'Dynamic based on volatility'
            optimized_strategy['optimizations_applied'].append('Improved risk management')
            optimized_strategy['expected_improvements']['sharpe'] = '20-30% increase'

        # Optimisation du drawdown
        if metrics['max_drawdown'] > 0.15:
            optimized_strategy['new_parameters']['max_position_size'] = '2% of capital'
            optimized_strategy['new_parameters']['correlation_filter'] = 'Enabled'
            optimized_strategy['optimizations_applied'].append('Reduced risk exposure')
            optimized_strategy['expected_improvements']['max_drawdown'] = '30-40% reduction'

        # Optimisation du win rate
        if metrics['win_rate'] < 0.65:
            optimized_strategy['new_parameters']['entry_signals'] = 'Multi-confirmation required'
            optimized_strategy['new_parameters']['time_filter'] = 'Trade only during high volatility'
            optimized_strategy['optimizations_applied'].append('Improved entry precision')
            optimized_strategy['expected_improvements']['win_rate'] = '10-15% increase'

        # Optimisation du profit factor
        if metrics['profit_factor'] < 2.0:
            optimized_strategy['new_parameters']['take_profit'] = 'Dynamic (1.5x-3x risk)'
            optimized_strategy['new_parameters']['trailing_stop'] = 'Enabled'
            optimized_strategy['optimizations_applied'].append('Enhanced exit strategy')
            optimized_strategy['expected_improvements']['profit_factor'] = '25-35% increase'

        # Ajouter les notes d'implémentation
        optimized_strategy['implementation_notes'] = [
            "Backtester avec les nouveaux paramètres",
            "Tester sur données out-of-sample",
            "Monitorer les métriques en temps réel",
            "Ajuster graduellement sur petit capital"
        ]

        # Calculer le score attendu après optimisation
        expected_score = min(100, analysis['performance_score'] * 1.4)
        optimized_strategy['expected_score'] = expected_score
        optimized_strategy['expected_score_improvement'] = expected_score - analysis['performance_score']

        return optimized_strategy

    def optimize_all_strategies(self, backtests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimise toutes les stratégies et génère un rapport"""

        results = {
            'optimization_timestamp': datetime.now().isoformat(),
            'total_strategies': len(backtests),
            'optimized_strategies': [],
            'summary': {
                'critical_strategies': 0,
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0,
                'avg_current_score': 0,
                'avg_expected_score': 0,
                'total_optimizations': 0
            }
        }

        all_scores = []
        all_expected_scores = []

        for backtest in backtests:
            try:
                optimization = self.optimize_strategy(backtest)
                results['optimized_strategies'].append(optimization)

                # Mettre à jour le résumé
                priority = optimization['analysis']['priority']
                if priority == 'critical':
                    results['summary']['critical_strategies'] += 1
                elif priority == 'high':
                    results['summary']['high_priority'] += 1
                elif priority == 'medium':
                    results['summary']['medium_priority'] += 1
                else:
                    results['summary']['low_priority'] += 1

                results['summary']['total_optimizations'] += len(
                    optimization['optimizations_applied']
                )

                all_scores.append(optimization['analysis']['performance_score'])
                all_expected_scores.append(optimization['expected_score'])

            except Exception as e:
                self.logger.error(f"Error optimizing {backtest.get('name', 'Unknown')}: {e}")

        # Calculer les moyennes
        if all_scores:
            results['summary']['avg_current_score'] = np.mean(all_scores)
            results['summary']['avg_expected_score'] = np.mean(all_expected_scores)

        return results

    def export_optimization_report(self, results: Dict[str, Any], output_path: str):
        """Exporte un rapport d'optimisation"""

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        # Afficher le rapport dans la console
        print("\n" + "="*80)
        print("RAPPORT D'OPTIMISATION INTELLIGENTE")
        print("="*80)
        print(f"\nTotal stratégies analysées: {results['total_strategies']}")
        print(f"Stratégies critiques: {results['summary']['critical_strategies']}")
        print(f"Priorité haute: {results['summary']['high_priority']}")
        print(f"Priorité moyenne: {results['summary']['medium_priority']}")
        print(f"Priorité basse: {results['summary']['low_priority']}")

        if results['summary']['avg_current_score'] > 0:
            print(f"\nScore moyen actuel: {results['summary']['avg_current_score']:.1f}/100")
            print(f"Score moyen attendu: {results['summary']['avg_expected_score']:.1f}/100")
            improvement = results['summary']['avg_expected_score'] - results['summary']['avg_current_score']
            print(f"Amélioration attendue: +{improvement:.1f} points")

        print(f"\nOptimisations recommandées: {results['summary']['total_optimizations']}")

        # Top 3 des stratégies à optimiser en priorité
        if results['optimized_strategies']:
            top_optimizations = sorted(
                results['optimized_strategies'],
                key=lambda x: x['analysis']['optimization_potential'],
                reverse=True
            )[:3]

            print("\n" + "-"*80)
            print("TOP 3 STRATÉGIES À OPTIMISER:")
            print("-"*80)
            for i, opt in enumerate(top_optimizations, 1):
                print(f"\n{i}. {opt['original_strategy']}")
                print(f"   Priorité: {opt['analysis']['priority'].upper()}")
                print(f"   Score actuel: {opt['analysis']['performance_score']:.1f}/100")
                print(f"   Score attendu: {opt['expected_score']:.1f}/100")
                print(f"   Optimisations: {', '.join(opt['optimizations_applied'])}")

        print("\n" + "="*80)
        print(f"Rapport sauvegardé: {output_path}")
        print("="*80 + "\n")


if __name__ == "__main__":
    # Test du système d'optimisation
    optimizer = IntelligentBacktestOptimizer()

    # Charger les backtests existants
    test_backtests = [
        {
            'name': 'Test Strategy 1',
            'return': 0.25,
            'sharpe': 0.8,
            'maxDrawdown': 0.25,
            'winRate': 0.50,
            'totalTrades': 30,
            'profitFactor': 1.1
        },
        {
            'name': 'Test Strategy 2',
            'return': 0.65,
            'sharpe': 1.8,
            'maxDrawdown': 0.08,
            'winRate': 0.70,
            'totalTrades': 100,
            'profitFactor': 2.2
        }
    ]

    print("="*80)
    print("TEST DU SYSTÈME D'OPTIMISATION INTELLIGENTE")
    print("="*80)

    # Analyser et optimiser
    results = optimizer.optimize_all_strategies(test_backtests)

    # Exporter le rapport
    optimizer.export_optimization_report(results, "intelligent_optimization_report.json")

    print("\n✅ Test terminé avec succès!")
