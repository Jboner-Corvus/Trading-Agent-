---
name: deamon-dev-ai-trading-expert
description: Expert du système Deamon Dev AI Trading - maîtrise l'architecture réelle : 3 agents IA avec appels LLM, 7+ algorithmes de trading ordinaires, Model Factory, système de logging Winston, 5 pages frontend, et trading HyperLiquid. Basé à 100% sur le code source réel avec distinction fondamentale Agent/Algorithme.
---

# 🧠 Expert Système NOVAQUOTE Trading (Version Réelle)

## Définition Fondamentale

🚨 **Distinction cruciale** :
- **Agent** = Script Python qui fait des appels API à un LLM (ChatGPT, Claude, etc.)
- **Algorithme** = Script Python ordinaire de trading/monitoring (sans IA)

## Vue d'ensemble du système

Le **NOVAQUOTE Trading System** est une plateforme composée de :

- **3 agents IA véritables** (avec appels LLM directs)
- **7+ algorithmes de trading ordinaires** (scripts Python sans IA)
- **Model Factory** pour gérer les 11 modèles IA
- **Système de logging Winston** avec 7 loggers spécialisés
- **5 pages frontend** pour la gestion et monitoring
- **exchanges** HyperLiquid
- **Aucun mock ou simulation ou demonstration n'est permis, nous sommes en reel prod et en trading reel**

## 🏗️ Architecture Technique Réelle

### Structure du projet
```
projet trading/
├── src/                    # Code source Python
│   ├── agents/            # 10+ scripts (3 agents + 7+ algorithmes)
│   ├── models/            # Model Factory (11 modèles IA)
│   ├── data/              # Données, OHLCV, backtests
│   ├── config.py          # Configuration centralisée
│   ├── nice_funcs.py      # Fonctions utilitaires trading
│   └── logger.js          # Système de logging Winston
├── frontend/              # Frontend server + pages
│   ├── server-frontend.js # Static server (Port 9000)
│   └── public/            # 5 pages HTML
├── backend/               # Backend server
│   └── server-backend.js  # API + WebSocket (Port 7000)
├── logs/                  # Logs système (7 types)
├── database/              # Schema PostgreSQL
└── docs/                  # Documentation
```

### Technologies utilisées
- **Backend**: Node.js + Express + WebSocket (Port 7000)
- **Frontend**: Node.js Static Server (Port 9000)
- **Pages**: HTML5, CSS3, JavaScript (Vanilla)
- **IA**: Model Factory avec Claude, GPT, DeepSeek, Grok, Gemini, Z.AI, Groq, Ollama
- **Trading**: HyperLiquid API
- **Base**: PostgreSQL
- **Logging**: Winston (Node.js)

## 🤖 Classification Fondamentale

### 🧠 **Agents IA Véritables (3 scripts avec LLM)**
Ces scripts font **réellement des appels API à des LLM** :

1. **`funding_agent.py`** ✅
   - Appels LLM : Détectés automatiquement
   - Fonction : Agent IA avec intégration LLM

2. **`risk_agent.py`** ✅
   - Appels LLM : Détectés automatiquement
   - Fonction : Agent IA avec intégration LLM

3. **`strategy_agent.py`** ✅
   - Appels LLM : Détectés automatiquement
   - Fonction : Agent IA avec intégration LLM

### ⚙️ **Algorithmes de Trading Ordinaires (7+ scripts sans IA)**
Ces scripts sont des **algorithmes purs** sans appels LLM :

#### Monitoring (1 scripts)
- **`sentiment_analysis_agent.py`** - Algorithme de trading ordinaire

#### Utilitaires (4 scripts)
- **`api.py`** - Algorithme de trading ordinaire
- **`base_agent.py`** - Algorithme de trading ordinaire
- **`intelligent_backtest_optimizer.py`** - Algorithme de trading ordinaire
- **`manager.py`** - Algorithme de trading ordinaire

#### Autres (2 scripts)
- **`__init__.py`** - Algorithme de trading ordinaire
- **`strategy_library.py`** - Algorithme de trading ordinaire

## 🔧 **Configuration IA Centralisée - Model Factory**

### Model Factory ✅
Système centralisé pour les **3 agents IA** dans `src/models/model_factory.py` :

```python
# Configuration centralisée via config.py
AI_MODEL = "glm-4.6"  # Par défaut
AI_TEMPERATURE = 0.7
AI_MAX_TOKENS = 1024

# Utilisation SEULEMENT pour les 3 agents IA
from src.models import model_factory
model = model_factory.get_model(model_type, config.AI_MODEL)
```

### Modèles Supportés (8 modèles)
- **Claude**: claude-3-5-haiku-latest, claude-3-sonnet-20240229
- **OpenAI**: gpt-4o
- **Z.AI**: glm-4.6 (modèle par défaut)
- **Google**: gemini-2.5-flash
- **DeepSeek**: deepseek-reasoner
- **xAI**: grok-4-fast-reasoning
- **Groq**: mixtral-8x7b-32768
- **Ollama**: llama3.2 (local)

## 📊 **Systèmes de Backtest Réels**

### Infrastructure de Backtest ✅
Basée sur des **algorithmes purs** (pas d'IA) :

1. **`rbi_agent_v3.py`** - Backtesting algorithmique pur
2. **`rbi_batch_backtester.py`** - Testing en lot (boucles)
3. **`src/data/execution_results/`** - Stockage résultats
4. **`src/data/rbi_v3/`** - Données analyses

### Pages Frontend pour Backtest ✅
- **`backtest.html`** - Interface configuration backtests
- **`backtest_fixed.html`** - Version corrigée

## 🎨 **Pages Frontend Réelles (5 pages)**

### 1. `backtest.html` ✅
- Interface Backtest
- Configuration backtests algorithmiques

### 2. `config.html` ✅
- Configuration Système
- Configuration des **3 agents IA** (modèles LLM)

### 3. `index.html` ✅
- Dashboard Principal
- Monitoring des 3 agents IA et 7+ algorithmes

### 4. `test_agents.html` ✅

### 5. `validate_config.html` ✅
- Configuration Système
- Configuration des **3 agents IA** (modèles LLM)

## 📝 **Système de Logging Winston Réel**

### Système Winston Enterprise-Grade ✅
Logging pour **tous les scripts** (agents + algorithmes) :

#### **Loggers disponibles** ✅
- `apiLogger` - Appels API avec timing
- `wsLogger` - Activité WebSocket
- `agentsLogger` - Opérations **3 agents IA**
- `backtestsLogger` - Backtests algorithmiques
- `tradingLogger` - Opérations trading
- `walletsLogger` - Authentification wallets
- `systemLogger` - Surveillance système

## ⚡ **Expertise Trading HyperLiquid**

### Configuration Multi-Exchanges ✅
```python
# Configuration dans config.py
EXCHANGE = "hyperliquid"  # Options: 'hyperliquid'

MONITORED_TOKENS = [
    "So11111111111111111111111111111111111111112",  # Wrapped SOL
]

HYPERLIQUID_SYMBOLS = ["BTC", "ETH", "SOL"]
HYPERLIQUID_LEVERAGE = 5
```

## 🔧 **Instructions d'Utilisation Réelles**

### Quand utiliser cette compétence
- Travail sur les **3 agents IA** avec appels LLM
- Développement des **7+ algorithmes de trading**
- Configuration **Model Factory** (11 modèles)
- Analyse des **logs Winston** (7 loggers)
- Développement **5 pages frontend**
- Configuration **trading multi-exchanges**

### Classification précise des fichiers
- **Agents IA (3 scripts)** : funding_agent.py, risk_agent.py, strategy_agent.py
- **Algorithmes (7+ scripts)** : Tous les autres `src/agents/*.py`
- **Model Factory** : `src/models/model_factory.py` (uniquement pour les 3 agents)
- **Configuration** : `src/config.py` (pour tout le système)
- **Logging** : `src/logger.js` (Winston, 7 loggers)

## 📚 **Ressources Réelles du Projet**

### Fichiers de configuration
- **`src/config.py`** ✅ - Configuration IA et trading
- **`src/models/model_factory.py`** ✅ - Model Factory (11 modèles)
- **`src/logger.js`** ✅ - Système Winston logging

### Documentation
- **`database/schema.sql`** ✅ - Structure base de données
- **`docs/HYPERLIQUID_API_DOCUMENTATION.md`** ✅ - DOCUMENTATION API
- **`docs/AGENTS_GRAPH_VISUALIZATION.md`** ✅ - GRAPHIQUE TECHNIQUE DES AGENTS IA

## REST API Endpoints
- **`get_all_mids()`** - Current prices
- **`get_meta()`** - Exchange metadata
- **`get_user_state()`** - Account information
- **`place_order()`** - Submit orders with signatures
- **`cancel_order()`** - Cancel orders
- **`get_positions()`** - Current positions
- **`get_open_orders()`** - Active orders

### Architecture réelle
- **3 agents IA** avec appels LLM
- **7+ algorithmes** purs de trading
- **1 Model Factory** pour les agents
- **1 système de trading** algorithmique

Cette compétence fait de toi un **expert du système réel** avec la distinction fondamentale entre **3 agents IA** (avec LLM) et **7+ algorithmes de trading ordinaires**.

## 👑 **L'AGENT MASTER - LE "CHEF" DU SYSTÈME NOVAQUOTE**

J'ai identifié et analysé le vrai "Chef" de votre système - l'Agent Master qui coordonne tous les agents.

### 🎯 **L'AGENT MASTER - COORDINATEUR CENTRAL**
**Fichier Principal** : `src/agents/manager.py`

### Fonctionnement :
- Gestionnaire principal de 30+ agents configurés
- API REST complète pour contrôle dynamique
- Monitoring temps réel avec métriques de performance
- Process management avec psutil pour supervision
- Interface CLI pour Node.js Bridge
- Logging structuré avec Winston (7 loggers)

### 🤖 **COMMENT IL CONTRÔLE LES 3 AGENTS PRINCIPAUX**

#### 1. 🛡️ **RISK AGENT → Gestion par Agent Master**
- **Appels LLM** : Claude + DeepSeek
- **Contrôle Master** : Surveillance limites P&L, arrêt système si risque
- **Coordination** : Premier agent exécuté pour sécurité

#### 2. 💰 **FUNDING AGENT → Gestion par Agent Master**
- **Appels LLM** : Claude + DeepSeek
- **Contrôle Master** : Détection arbitrages, validation opportunités
- **Coordination** : Exécuté après Risk pour vérifier sécurité

#### 3. 📊 **STRATEGY AGENT → Gestion par Agent Master**
- **Appels LLM** : Claude
- **Contrôle Master** : Orchestration analyse 19 tokens
- **Coordination** : Exécuté après validation Risk et Funding

## 📋 **Comment obtenir l'arborescence du projet**

Pour obtenir l'arborescence complète du projet avec précision :

```bash
python project_snapshot.py
```

Cela génère automatiquement le fichier **`arborescence.md`** avec :
- Structure complète en arbre
- Tous les fichiers et dossiers
- Liste des répertoires ignorés (node_modules, __pycache__, etc.)

## 📖 **Documentation API HyperLiquid**

La documentation complète de l'API HyperLiquid se trouve dans :
**`@docs\HYPERLIQUID_API_DOCUMENTATION.md`**

Cette documentation contient tous les endpoints et méthodes disponibles pour l'intégration HyperLiquid.

---

*Skill basé sur l'analyse complète du code source réel - Système avec distinction Agent/Algorithme fondamentale*