# 🔄 GUIDE SYSTÈME CIRCULAIRE NOVAQUOTE

## 📋 Vue d'ensemble

Le **Système Circulaire NOVAQUOTE** est un système de trading automatisé qui orchestre 4 agents IA dans un cycle de 20 minutes avec backtests intégrés en temps réel.

### 🎯 Fonctionnement

```
┌─ CYCLE 20 MINUTES ─────────────────────────────────────┐
│                                                        │
│ 1️⃣ RISK AGENT (SÉCURITÉ)                             │
│ 2️⃣ STRATEGY AGENT (TECHNIQUE)                        │
│ 3️⃣ FUNDING AGENT (ARBITRAGE)                         │
│ 4️⃣ SENTIMENT AGENT (SOCIAL)                           │
│ 5️⃣ DÉCISION UNIFIÉE + BACKTESTS                      │
│                                                        │
│ ⏰ ATTENTE 20 MINUTES → REPEAT                         │
└────────────────────────────────────────────────────────┘
```

## 🚀 Démarrage Rapide

### 1. Lancer le Backend et Frontend

```bash
# Terminal 1: Backend + Frontend
node run.js start

# Ou séparément:
node backend/server-backend.js    # Port 7000
node frontend/server-frontend.js  # Port 9001
```

### 2. Tester le Système

```bash
# Test complet du système
python scripts/test_circular_system.py
```

### 3. Démarrer l'Agent Master

```bash
# Via API REST
curl -X POST http://localhost:7000/api/agents/master/start

# Ou via navigateur
http://localhost:9001  # Dashboard
```

## 📊 Dashboard Temps Réel

### URL Principales

- **Dashboard**: http://localhost:9001
- **API Dashboard**: http://localhost:7000/api/dashboard/real-time
- **Status Agent Master**: http://localhost:7000/api/agents/master/status

### Endpoints API

```bash
# Démarrer l'Agent Master
POST /api/agents/master/start

# Arrêter l'Agent Master
POST /api/agents/master/stop

# Status du système
GET /api/agents/master/status

# Données dashboard temps réel
GET /api/dashboard/real-time

# Validation backtests
GET /api/backtests/validate
```

## 🧪 Composants du Système

### 1. Agent Master (`src/agents/master_agent.py`)

**Rôle**: Coordinateur central

**Responsabilités**:
- Orchestration des 4 agents
- Prise de décision unifiée
- Validation backtests
- Mise à jour dashboard

**Cycle**:
```python
cycle_duration_seconds = 20 * 60  # 20 minutes
```

### 2. Backtester Temps Réel (`src/data/realtime_backtester.py`)

**Rôle**: Validation des décisions

**Fonctions**:
- Chargement backtests historiques
- Validation signaux vs historique
- Calcul score de validation
- Génération rapports

**Backtests chargés**:
- `src/data/production_backtests/*.json`
- `src/data/rbi_v3/10_23_2025/backtests_final/*.json`

### 3. Collecteur de Métriques (`src/data/metrics_collector.py`)

**Rôle**: Centralisation des métriques

**Métriques collectées**:
- Performance agents
- Statistiques cycles
- Tendances
- Alertes

### 4. Agents IA (4 agents)

#### 🛡️ Risk Agent
- **Fichier**: `src/agents/risk_agent.py`
- **IA**: Claude + DeepSeek
- **Fonction**: Contrôle risque, limites

#### 📊 Strategy Agent
- **Fichier**: `src/agents/strategy_agent.py`
- **IA**: Claude
- **Fonction**: Signaux techniques

#### 💰 Funding Agent
- **Fichier**: `src/agents/funding_agent.py`
- **IA**: Claude + DeepSeek
- **Fonction**: Arbitrage funding

#### 🎭 Sentiment Agent
- **Fichier**: `src/agents/sentiment_analysis_agent.py`
- **IA**: OpenAI TTS
- **Fonction**: Analyse sentiment

## 📈 Données et Fichiers

### Structure des Répertoires

```
src/
├── agents/
│   ├── master_agent.py          # Coordinator
│   ├── risk_agent.py            # Risk management
│   ├── strategy_agent.py        # Technical analysis
│   ├── funding_agent.py         # Funding arbitrage
│   └── sentiment_analysis_agent.py  # Social sentiment
│
├── data/
│   ├── production_backtests/    # Historical backtests
│   ├── realtime_backtester.py   # Real-time validation
│   ├── metrics_collector.py     # Metrics centralization
│   └── metrics/                 # Stored metrics
│
└── models/
    └── model_factory.py         # 8 AI models

backend/
└── dashboard_data.json          # Dashboard real-time data
```

### Fichiers Générés

```
backend/
├── dashboard_data.json          # Live dashboard data
└── validation_reports/          # Validation reports

src/data/
├── metrics/                     # Historical metrics
├── cycles/                      # Cycle history
└── validation_reports/          # Backtest reports
```

## 🔍 Monitoring et Logs

### Logs Winston (7 loggers)

```javascript
// Logs disponibles
apiLogger       // Appels API
wsLogger        // WebSocket
agentsLogger    // Opérations agents
backtestsLogger // Backtests
tradingLogger   // Trading
walletsLogger   // Wallets
systemLogger    // Surveillance
```

### Fichiers de Logs

```
logs/
├── app-YYYY-MM-DD.log          # Logs généraux
├── error-YYYY-MM-DD.log        # Erreurs
├── agents-YYYY-MM-DD.log       # Agents
├── backtests-YYYY-MM-DD.log    # Backtests
├── trading-YYYY-MM-DD.log      # Trading
├── websocket-YYYY-MM-DD.log    # WebSocket
└── api-YYYY-MM-DD.log          // API
```

### Métriques Temps Réel

```json
{
  "timestamp": "2025-11-04T10:00:00Z",
  "current_cycle": "2025-11-04_10:00",
  "system_status": "EXCELLENT",
  "agents_active": {
    "risk_agent": {
      "status": "SUCCESS",
      "confidence": 0.85,
      "llm_calls": 2
    },
    "strategy_agent": {
      "status": "SUCCESS",
      "confidence": 0.92,
      "llm_calls": 1
    }
  },
  "current_decision": {
    "decision": "EXECUTER_BUY_SIGNALS",
    "confidence": 0.89
  },
  "performance_stats": {
    "total_cycles": 15,
    "success_rate": 0.87,
    "average_confidence": 0.84
  }
}
```

## ⚙️ Configuration

### Variables d'Environnement (`.env`)

```env
# API Keys (obligatoires)
ANTHROPIC_KEY=sk-ant-xxx...
OPENAI_KEY=sk-xxx...
DEEPSEEK_KEY=sk-xxx...
ZAI_KEY=sk-zai-xxx...

# Trading
HYPERLIQUID_PRIVATE_KEY=0x...
SOLANA_PRIVATE_KEY=...
```

### Configuration Agent Master

```python
# src/agents/master_agent.py
self.cycle_duration_seconds = 20 * 60  # 20 minutes
self.is_running = False
self.cycle_count = 0
```

### Seuils de Validation

```python
# backtester.py
BACKTEST_SUCCESS_THRESHOLD = 0.6  # 60% win rate minimum
PERFORMANCE_BONUS = 0.1           # 10% bonus max
```

## 🚨 Troubleshooting

### Problème: Agent Master ne démarre pas

```bash
# Vérifier Python
python --version

# Vérifier les dépendances
pip install -r requirements.txt

# Test manuel
python src/agents/master_agent.py
```

### Problème: Pas de données dashboard

```bash
# Vérifier que les agents tournent
curl http://localhost:7000/api/agents/master/status

# Vérifier le fichier dashboard_data.json
ls -la backend/dashboard_data.json
```

### Problème: Backtests non chargés

```bash
# Vérifier les fichiers
ls -la src/data/production_backtests/
ls -la src/data/rbi_v3/10_23_2025/backtests_final/

# Test backtester
python src/data/realtime_backtester.py
```

### Problème: Erreurs LLM

```bash
# Vérifier les clés API
grep -r "API_KEY" .env

# Tester connexion
curl -X POST http://localhost:7000/api/debug/hyperliquid
```

## 📚 Documentation API

### Response Types

#### Dashboard Data
```typescript
interface DashboardData {
  timestamp: string;
  current_cycle: string | null;
  next_cycle: string | null;
  system_status: 'INIT' | 'RUNNING' | 'STOPPED';
  active_agents: Record<string, AgentStatus>;
  current_decision: Decision | null;
  performance_stats: PerformanceStats;
  recent_cycles: Cycle[];
  alerts: Alert[];
}
```

#### Agent Status
```typescript
interface AgentStatus {
  status: 'SUCCESS' | 'WARNING' | 'ERROR' | 'CRITICAL';
  confidence: number;
  llm_calls: number;
  last_update: string;
  execution_time_ms: number;
}
```

## 🎓 Exemples d'Utilisation

### 1. Démarrage Manuel Complet

```bash
# 1. Lancer backend
node backend/server-backend.js &

# 2. Lancer frontend
node frontend/server-frontend.js &

# 3. Démarrer agents
curl -X POST http://localhost:7000/api/agents/master/start

# 4. Vérifier status
curl http://localhost:7000/api/agents/master/status
```

### 2. Monitoring Dashboard

```bash
# Watch dashboard en continu
watch -n 5 curl -s http://localhost:7000/api/dashboard/real-time | jq '.data'

# Monitor logs agents
tail -f logs/agents-$(date +%Y-%m-%d).log
```

### 3. Test de Performance

```bash
# Test complet
python scripts/test_circular_system.py

# Test backtester uniquement
python src/data/realtime_backtester.py

# Test collecteur métriques
python src/data/metrics_collector.py
```

## 🔧 Maintenance

### Sauvegarde

```bash
# Sauvegarder métriques
python -c "from src.data.metrics_collector import MetricsCollector; import asyncio; asyncio.run(MetricsCollector().export_metrics())"

# Sauvegarder cycles
cp -r src/data/cycles/ backups/cycles_$(date +%Y%m%d)/

# Sauvegarder logs
cp -r logs/ backups/logs_$(date +%Y%m%d)/
```

### Nettoyage

```bash
# Nettoyer anciens logs (>30 jours)
find logs/ -name "*.log" -mtime +30 -delete

# Nettoyer anciens cycles (>100)
ls -t src/data/cycles/ | tail -n +101 | xargs -r rm

# Réinitialiser dashboard_data.json
rm backend/dashboard_data.json
```

## 📞 Support

### Logs d'Erreur

Vérifier ces fichiers en cas de problème:
1. `logs/error-YYYY-MM-DD.log` - Erreurs système
2. `logs/agents-YYYY-MM-DD.log` - Erreurs agents
3. `backend/dashboard_data.json` - État dashboard

### Commandes de Diagnostic

```bash
# Status système
ps aux | grep -E "python|node" | grep -v grep

# Ports utilisés
netstat -tlnp | grep -E "7000|9001"

# Espace disque
df -h

# Mémoire
free -h
```

---

## 🎉 Résumé

Le Système Circulaire NOVAQUOTE est maintenant **opérationnel** avec :

- ✅ 4 agents IA coordonnés
- ✅ Cycle de 20 minutes automatisé
- ✅ Backtests en temps réel
- ✅ Dashboard temps réel
- ✅ Métriques centralisées
- ✅ Logging complet

**Pour commencer**: `node run.js start` puis `curl -X POST http://localhost:7000/api/agents/master/start`

**Dashboard**: http://localhost:9001

**API Documentation**: Voir section "Documentation API" ci-dessus
