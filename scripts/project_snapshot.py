#!/usr/bin/env python3
"""
🌙 NOVAQUOTE PROJECT SNAPSHOT
Script de snapshot de l'arborescence du projet
Génère un arbre simple de la structure des fichiers et dossiers
"""

import os
from pathlib import Path

class ProjectSnapshot:
    """Classe pour créer un snapshot de l'arborescence du projet"""

    IGNORED_DIRS = {
        'node_modules', '.git', '__pycache__', '.pytest_cache',
        'venv', 'env', '.env', 'dist', 'build', '.next', '.nuxt',
        'target', 'bin', 'obj', '.vscode', '.idea', 'logs',
        'tmp', 'temp', 'cache', 'caches', '.DS_Store'
    }

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.ignored_found = set()

    def print_tree(self, dir_path: Path, prefix: str = "", is_last: bool = True):
        """Affiche l'arborescence de manière récursive"""
        try:
            items = sorted(dir_path.iterdir())
        except PermissionError:
            print(f"{prefix}└── [Permission denied]")
            return

        # Filtrer les éléments
        filtered_items = []
        for item in items:
            if item.name.startswith('.') and item.name not in ['.env_example', '.gitignore']:
                continue
            if item.is_dir() and item.name in self.IGNORED_DIRS:
                self.ignored_found.add(str(item.relative_to(self.root_path)))
                continue
            filtered_items.append(item)

        for i, item in enumerate(filtered_items):
            is_last_item = (i == len(filtered_items) - 1)
            connector = "└── " if is_last_item else "├── "

            if item.is_file():
                print(f"{prefix}{connector}{item.name}")
            elif item.is_dir():
                print(f"{prefix}{connector}{item.name}/")
                extension = "    " if is_last_item else "│   "
                self.print_tree(item, prefix + extension, is_last_item)

    def generate_tree(self):
        """Génère et affiche l'arborescence"""
        output_lines = []
        output_lines.append(f"{self.root_path.name}/")
        self.print_tree_to_list(self.root_path, output_lines)

        if self.ignored_found:
            output_lines.append("")
            output_lines.append("ignore:")
            for ignored in sorted(self.ignored_found):
                output_lines.append(f"  - {ignored}/")

        # Créer le dossier contexte s'il n'existe pas
        contexte_dir = self.root_path / "contexte"
        contexte_dir.mkdir(exist_ok=True)

        # Écrire dans le fichier arborescence.md dans le dossier contexte
        with open(contexte_dir / "arborescence.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        # Créer le fichier context_app.md avec des informations supplémentaires
        self.create_context_file(contexte_dir)

        # Créer le fichier de visualisation des agents
        self.create_agents_visualization_file()

        # Afficher aussi à l'écran
        print('\n'.join(output_lines))

        return output_lines

    def print_tree_to_list(self, dir_path: Path, output_lines: list, prefix: str = "", is_last: bool = True):
        """Affiche l'arborescence de manière récursive dans une liste"""
        try:
            items = sorted(dir_path.iterdir())
        except PermissionError:
            output_lines.append(f"{prefix}└── [Permission denied]")
            return

        # Filtrer les éléments
        filtered_items = []
        for item in items:
            if item.name.startswith('.') and item.name not in ['.env_example', '.gitignore']:
                continue
            if item.is_dir() and item.name in self.IGNORED_DIRS:
                self.ignored_found.add(str(item.relative_to(self.root_path)))
                continue
            filtered_items.append(item)

        for i, item in enumerate(filtered_items):
            is_last_item = (i == len(filtered_items) - 1)
            connector = "└── " if is_last_item else "├── "

            if item.is_file():
                output_lines.append(f"{prefix}{connector}{item.name}")
            elif item.is_dir():
                output_lines.append(f"{prefix}{connector}{item.name}/")
                extension = "    " if is_last_item else "│   "
                self.print_tree_to_list(item, output_lines, prefix + extension, is_last_item)

    def analyze_codebase(self):
        """Analyse réelle du code source pour identifier les agents IA et algorithmes"""
        agents_dir = self.root_path / "src" / "agents"
        models_dir = self.root_path / "src" / "models"
        frontend_dir = self.root_path / "frontend" / "public"
        docs_dir = self.root_path / "docs"

        analysis = {
            "agents_ia": [],
            "algorithmes": [],
            "modeles_ia": [],
            "pages_frontend": [],
            "docs_hyperliquid": [],
            "agent_master": None
        }

        # Analyser réellement les agents pour détecter les appels LLM
        if agents_dir.exists():
            py_files = list(agents_dir.glob("*.py"))

            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Détecter les vrais appels LLM (API externes)
                    has_llm_calls = any(keyword in content for keyword in [
                        'anthropic.Anthropic',
                        'openai.OpenAI',
                        'client.messages.create',
                        'chat.completions.create',
                        'deepseek_client',
                        'claude-3',
                        'gpt-4'
                    ])

                    if has_llm_calls and py_file.name.endswith('.py'):
                        analysis["agents_ia"].append(py_file.name)
                    else:
                        analysis["algorithmes"].append(py_file.name)

                except Exception as e:
                    print(f"Erreur lors de l'analyse de {py_file.name}: {e}")
                    # En cas d'erreur, considérer comme algorithme ordinaire
                    analysis["algorithmes"].append(py_file.name)

        # Analyser les modèles IA
        if models_dir.exists():
            analysis["modeles_ia"] = [f.name for f in models_dir.glob("*.py")]

        # Analyser les pages frontend
        if frontend_dir.exists():
            analysis["pages_frontend"] = [f.name for f in frontend_dir.glob("*.html")]

        # Analyser la documentation HyperLiquid
        if docs_dir.exists():
            analysis["docs_hyperliquid"] = [f.name for f in docs_dir.glob("*hyperliquid*.md")]

        return analysis

    def create_context_file(self, contexte_dir):
        """Crée un fichier context_app.md avec des informations détaillées et à jour"""
        analysis = self.analyze_codebase()

        context_lines = []
        context_lines.append("---")
        context_lines.append("name: deamon-dev-ai-trading-expert")
        context_lines.append("description: Expert du système Deamon Dev AI Trading - maîtrise l'architecture réelle : {} agents IA avec appels LLM, {}+ algorithmes de trading ordinaires, Model Factory, système de logging Winston, {} pages frontend, et trading HyperLiquid. Basé à 100% sur le code source réel avec distinction fondamentale Agent/Algorithme.".format(
            len(analysis["agents_ia"]), len(analysis["algorithmes"]), len(analysis["pages_frontend"])
        ))
        context_lines.append("---")
        context_lines.append("")
        context_lines.append("# 🧠 Expert Système NOVAQUOTE Trading (Version Réelle)")
        context_lines.append("")
        context_lines.append("## Définition Fondamentale")
        context_lines.append("")
        context_lines.append("🚨 **Distinction cruciale** :")
        context_lines.append("- **Agent** = Script Python qui fait des appels API à un LLM (ChatGPT, Claude, etc.)")
        context_lines.append("- **Algorithme** = Script Python ordinaire de trading/monitoring (sans IA)")
        context_lines.append("")
        context_lines.append("## Vue d'ensemble du système")
        context_lines.append("")
        context_lines.append("Le **NOVAQUOTE Trading System** est une plateforme composée de :")
        context_lines.append("")
        context_lines.append("- **{} agents IA véritables** (avec appels LLM directs)".format(len(analysis["agents_ia"])))
        context_lines.append("- **{}+ algorithmes de trading ordinaires** (scripts Python sans IA)".format(len(analysis["algorithmes"])))
        context_lines.append("- **Model Factory** pour gérer les {} modèles IA".format(len(analysis["modeles_ia"])))
        context_lines.append("- **Système de logging Winston** avec 7 loggers spécialisés")
        context_lines.append("- **{} pages frontend** pour la gestion et monitoring".format(len(analysis["pages_frontend"])))
        context_lines.append("- **exchanges** HyperLiquid")
        context_lines.append("- **Aucun mock ou simulation ou demonstration n'est permis, nous sommes en reel prod et en trading reel**")
        context_lines.append("")
        context_lines.append("## 🏗️ Architecture Technique Réelle")
        context_lines.append("")
        context_lines.append("### Structure du projet")
        context_lines.append("```")
        context_lines.append("projet trading/")
        context_lines.append("├── src/                    # Code source Python")
        context_lines.append("│   ├── agents/            # {}+ scripts ({} agents + {}+ algorithmes)".format(
            len(analysis["agents_ia"]) + len(analysis["algorithmes"]), len(analysis["agents_ia"]), len(analysis["algorithmes"])))
        context_lines.append("│   ├── models/            # Model Factory ({} modèles IA)".format(len(analysis["modeles_ia"])))
        context_lines.append("│   ├── data/              # Données, OHLCV, backtests")
        context_lines.append("│   ├── config.py          # Configuration centralisée")
        context_lines.append("│   ├── nice_funcs.py      # Fonctions utilitaires trading")
        context_lines.append("│   └── logger.js          # Système de logging Winston")
        context_lines.append("├── frontend/              # Frontend server + pages")
        context_lines.append("│   ├── server-frontend.js # Static server (Port 9000)")
        context_lines.append("│   └── public/            # {} pages HTML".format(len(analysis["pages_frontend"])))
        context_lines.append("├── backend/               # Backend server")
        context_lines.append("│   └── server-backend.js  # API + WebSocket (Port 7000)")
        context_lines.append("├── logs/                  # Logs système (7 types)")
        context_lines.append("├── database/              # Schema PostgreSQL")
        context_lines.append("└── docs/                  # Documentation")
        context_lines.append("```")
        context_lines.append("")
        context_lines.append("### Technologies utilisées")
        context_lines.append("- **Backend**: Node.js + Express + WebSocket (Port 7000)")
        context_lines.append("- **Frontend**: Node.js Static Server (Port 9000)")
        context_lines.append("- **Pages**: HTML5, CSS3, JavaScript (Vanilla)")
        context_lines.append("- **IA**: Model Factory avec Claude, GPT, DeepSeek, Grok, Gemini, Z.AI, Groq, Ollama")
        context_lines.append("- **Trading**: HyperLiquid API")
        context_lines.append("- **Base**: PostgreSQL")
        context_lines.append("- **Logging**: Winston (Node.js)")
        context_lines.append("")
        context_lines.append("## 🤖 Classification Fondamentale")
        context_lines.append("")
        context_lines.append("### 🧠 **Agents IA Véritables ({} scripts avec LLM)**".format(len(analysis["agents_ia"])))
        context_lines.append("Ces scripts font **réellement des appels API à des LLM** :")
        context_lines.append("")

        for i, agent in enumerate(sorted(analysis["agents_ia"]), 1):
            context_lines.append("{}. **`{}`** ✅".format(i, agent))
            context_lines.append("   - Appels LLM : Détectés automatiquement")
            context_lines.append("   - Fonction : Agent IA avec intégration LLM")
            context_lines.append("")

        context_lines.append("### ⚙️ **Algorithmes de Trading Ordinaires ({}+ scripts sans IA)**".format(len(analysis["algorithmes"])))
        context_lines.append("Ces scripts sont des **algorithmes purs** sans appels LLM :")
        context_lines.append("")

        # Grouper les algorithmes par catégories
        algo_categories = {
            "HyperLiquid": [a for a in analysis["algorithmes"] if "hyperliquid" in a.lower()],
            "Trading": [a for a in analysis["algorithmes"] if any(x in a.lower() for x in ["trading", "trade"])],
            "Monitoring": [a for a in analysis["algorithmes"] if any(x in a.lower() for x in ["monitor", "sentiment", "chart"])],
            "Utilitaires": [a for a in analysis["algorithmes"] if any(x in a.lower() for x in ["base", "api", "manager", "backtest"])],
            "Communication": [a for a in analysis["algorithmes"] if any(x in a.lower() for x in ["chat", "tweet", "focus"])],
            "RBI": [a for a in analysis["algorithmes"] if "rbi" in a.lower()],
            "Autres": []
        }

        # Les algorithmes non catégorisés vont dans "Autres"
        categorized = set()
        for category, algos in algo_categories.items():
            if category != "Autres":
                categorized.update(algos)

        algo_categories["Autres"] = [a for a in analysis["algorithmes"] if a not in categorized]

        for category, algos in algo_categories.items():
            if algos:
                context_lines.append("#### {} ({} scripts)".format(category, len(algos)))
                for algo in sorted(algos):
                    context_lines.append("- **`{}`** - Algorithme de trading ordinaire".format(algo))
                context_lines.append("")

        context_lines.append("## 🔧 **Configuration IA Centralisée - Model Factory**")
        context_lines.append("")
        context_lines.append("### Model Factory ✅")
        context_lines.append("Système centralisé pour les **{} agents IA** dans `src/models/model_factory.py` :".format(len(analysis["agents_ia"])))
        context_lines.append("")
        context_lines.append("```python")
        context_lines.append("# Configuration centralisée via config.py")
        context_lines.append("AI_MODEL = \"glm-4.6\"  # Par défaut")
        context_lines.append("AI_TEMPERATURE = 0.7")
        context_lines.append("AI_MAX_TOKENS = 1024")
        context_lines.append("")
        context_lines.append("# Utilisation SEULEMENT pour les {} agents IA".format(len(analysis["agents_ia"])))
        context_lines.append("from src.models import model_factory")
        context_lines.append("model = model_factory.get_model(model_type, config.AI_MODEL)")
        context_lines.append("```")
        context_lines.append("")
        context_lines.append("### Modèles Supportés (8 modèles)")
        context_lines.append("- **Claude**: claude-3-5-haiku-latest, claude-3-sonnet-20240229")
        context_lines.append("- **OpenAI**: gpt-4o")
        context_lines.append("- **Z.AI**: glm-4.6 (modèle par défaut)")
        context_lines.append("- **Google**: gemini-2.5-flash")
        context_lines.append("- **DeepSeek**: deepseek-reasoner")
        context_lines.append("- **xAI**: grok-4-fast-reasoning")
        context_lines.append("- **Groq**: mixtral-8x7b-32768")
        context_lines.append("- **Ollama**: llama3.2 (local)")
        context_lines.append("")
        context_lines.append("## 📊 **Systèmes de Backtest Réels**")
        context_lines.append("")
        context_lines.append("### Infrastructure de Backtest ✅")
        context_lines.append("Basée sur des **algorithmes purs** (pas d'IA) :")
        context_lines.append("")
        context_lines.append("1. **`rbi_agent_v3.py`** - Backtesting algorithmique pur")
        context_lines.append("2. **`rbi_batch_backtester.py`** - Testing en lot (boucles)")
        context_lines.append("3. **`src/data/execution_results/`** - Stockage résultats")
        context_lines.append("4. **`src/data/rbi_v3/`** - Données analyses")
        context_lines.append("")
        context_lines.append("### Pages Frontend pour Backtest ✅")
        context_lines.append("- **`backtest.html`** - Interface configuration backtests")
        context_lines.append("- **`backtest_fixed.html`** - Version corrigée")
        context_lines.append("")
        context_lines.append("## 🎨 **Pages Frontend Réelles ({} pages)**".format(len(analysis["pages_frontend"])))
        context_lines.append("")
        for i, page in enumerate(sorted(analysis["pages_frontend"]), 1):
            context_lines.append("### {}. `{}` ✅".format(i, page))
            if "index" in page.lower():
                context_lines.append("- Dashboard Principal")
                context_lines.append("- Monitoring des {} agents IA et {}+ algorithmes".format(len(analysis["agents_ia"]), len(analysis["algorithmes"])))
            elif "config" in page.lower():
                context_lines.append("- Configuration Système")
                context_lines.append("- Configuration des **{} agents IA** (modèles LLM)".format(len(analysis["agents_ia"])))
            elif "backtest" in page.lower():
                context_lines.append("- Interface Backtest")
                context_lines.append("- Configuration backtests algorithmiques")
            context_lines.append("")
        context_lines.append("## 📝 **Système de Logging Winston Réel**")
        context_lines.append("")
        context_lines.append("### Système Winston Enterprise-Grade ✅")
        context_lines.append("Logging pour **tous les scripts** (agents + algorithmes) :")
        context_lines.append("")
        context_lines.append("#### **Loggers disponibles** ✅")
        context_lines.append("- `apiLogger` - Appels API avec timing")
        context_lines.append("- `wsLogger` - Activité WebSocket")
        context_lines.append("- `agentsLogger` - Opérations **{} agents IA**".format(len(analysis["agents_ia"])))
        context_lines.append("- `backtestsLogger` - Backtests algorithmiques")
        context_lines.append("- `tradingLogger` - Opérations trading")
        context_lines.append("- `walletsLogger` - Authentification wallets")
        context_lines.append("- `systemLogger` - Surveillance système")
        context_lines.append("")
        context_lines.append("## ⚡ **Expertise Trading HyperLiquid**")
        context_lines.append("")
        context_lines.append("### Configuration Multi-Exchanges ✅")
        context_lines.append("```python")
        context_lines.append("# Configuration dans config.py")
        context_lines.append("EXCHANGE = \"hyperliquid\"  # Options: 'hyperliquid'")
        context_lines.append("")
        context_lines.append("MONITORED_TOKENS = [")
        context_lines.append("    \"So11111111111111111111111111111111111111112\",  # Wrapped SOL")
        context_lines.append("]")
        context_lines.append("")
        context_lines.append("HYPERLIQUID_SYMBOLS = [\"BTC\", \"ETH\", \"SOL\"]")
        context_lines.append("HYPERLIQUID_LEVERAGE = 5")
        context_lines.append("```")
        context_lines.append("")
        context_lines.append("## 🔧 **Instructions d'Utilisation Réelles**")
        context_lines.append("")
        context_lines.append("### Quand utiliser cette compétence")
        context_lines.append("- Travail sur les **{} agents IA** avec appels LLM".format(len(analysis["agents_ia"])))
        context_lines.append("- Développement des **{}+ algorithmes de trading**".format(len(analysis["algorithmes"])))
        context_lines.append("- Configuration **Model Factory** ({} modèles)".format(len(analysis["modeles_ia"])))
        context_lines.append("- Analyse des **logs Winston** (7 loggers)")
        context_lines.append("- Développement **{} pages frontend**".format(len(analysis["pages_frontend"])))
        context_lines.append("- Configuration **trading multi-exchanges**")
        context_lines.append("")
        context_lines.append("### Classification précise des fichiers")
        context_lines.append("- **Agents IA ({} scripts)** : {}".format(len(analysis["agents_ia"]), ", ".join(sorted(analysis["agents_ia"]))))
        context_lines.append("- **Algorithmes ({}+ scripts)** : Tous les autres `src/agents/*.py`".format(len(analysis["algorithmes"])))
        context_lines.append("- **Model Factory** : `src/models/model_factory.py` (uniquement pour les {} agents)".format(len(analysis["agents_ia"])))
        context_lines.append("- **Configuration** : `src/config.py` (pour tout le système)")
        context_lines.append("- **Logging** : `src/logger.js` (Winston, 7 loggers)")
        context_lines.append("")
        context_lines.append("## 📚 **Ressources Réelles du Projet**")
        context_lines.append("")
        context_lines.append("### Fichiers de configuration")
        context_lines.append("- **`src/config.py`** ✅ - Configuration IA et trading")
        context_lines.append("- **`src/models/model_factory.py`** ✅ - Model Factory ({} modèles)".format(len(analysis["modeles_ia"])))
        context_lines.append("- **`src/logger.js`** ✅ - Système Winston logging")
        context_lines.append("")
        context_lines.append("### Documentation")
        context_lines.append("- **`database/schema.sql`** ✅ - Structure base de données")
        if analysis["docs_hyperliquid"]:
            context_lines.append("- **`docs/{}`** ✅ - DOCUMENTATION API".format(analysis["docs_hyperliquid"][0]))
        context_lines.append("- **`docs/AGENTS_GRAPH_VISUALIZATION.md`** ✅ - GRAPHIQUE TECHNIQUE DES AGENTS IA")
        context_lines.append("")
        context_lines.append("## REST API Endpoints")
        context_lines.append("- **`get_all_mids()`** - Current prices")
        context_lines.append("- **`get_meta()`** - Exchange metadata")
        context_lines.append("- **`get_user_state()`** - Account information")
        context_lines.append("- **`place_order()`** - Submit orders with signatures")
        context_lines.append("- **`cancel_order()`** - Cancel orders")
        context_lines.append("- **`get_positions()`** - Current positions")
        context_lines.append("- **`get_open_orders()`** - Active orders")
        context_lines.append("")
        context_lines.append("### Architecture réelle")
        context_lines.append("- **{} agents IA** avec appels LLM".format(len(analysis["agents_ia"])))
        context_lines.append("- **{}+ algorithmes** purs de trading".format(len(analysis["algorithmes"])))
        context_lines.append("- **1 Model Factory** pour les agents")
        context_lines.append("- **1 système de trading** algorithmique")
        context_lines.append("")
        context_lines.append("Cette compétence fait de toi un **expert du système réel** avec la distinction fondamentale entre **{} agents IA** (avec LLM) et **{}+ algorithmes de trading ordinaires**.".format(len(analysis["agents_ia"]), len(analysis["algorithmes"])))
        context_lines.append("")
        context_lines.append("## 👑 **L'AGENT MASTER - LE \"CHEF\" DU SYSTÈME NOVAQUOTE**")
        context_lines.append("")
        context_lines.append("J'ai identifié et analysé le vrai \"Chef\" de votre système - l'Agent Master qui coordonne tous les agents.")
        context_lines.append("")
        context_lines.append("### 🎯 **L'AGENT MASTER - COORDINATEUR CENTRAL**")
        context_lines.append("**Fichier Principal** : `src/agents/manager.py`")
        context_lines.append("")
        context_lines.append("### Fonctionnement :")
        context_lines.append("- Gestionnaire principal de 30+ agents configurés")
        context_lines.append("- API REST complète pour contrôle dynamique")
        context_lines.append("- Monitoring temps réel avec métriques de performance")
        context_lines.append("- Process management avec psutil pour supervision")
        context_lines.append("- Interface CLI pour Node.js Bridge")
        context_lines.append("- Logging structuré avec Winston (7 loggers)")
        context_lines.append("")
        context_lines.append("### 🤖 **COMMENT IL CONTRÔLE LES 3 AGENTS PRINCIPAUX**")
        context_lines.append("")
        context_lines.append("#### 1. 🛡️ **RISK AGENT → Gestion par Agent Master**")
        context_lines.append("- **Appels LLM** : Claude + DeepSeek")
        context_lines.append("- **Contrôle Master** : Surveillance limites P&L, arrêt système si risque")
        context_lines.append("- **Coordination** : Premier agent exécuté pour sécurité")
        context_lines.append("")
        context_lines.append("#### 2. 💰 **FUNDING AGENT → Gestion par Agent Master**")
        context_lines.append("- **Appels LLM** : Claude + DeepSeek")
        context_lines.append("- **Contrôle Master** : Détection arbitrages, validation opportunités")
        context_lines.append("- **Coordination** : Exécuté après Risk pour vérifier sécurité")
        context_lines.append("")
        context_lines.append("#### 3. 📊 **STRATEGY AGENT → Gestion par Agent Master**")
        context_lines.append("- **Appels LLM** : Claude")
        context_lines.append("- **Contrôle Master** : Orchestration analyse 19 tokens")
        context_lines.append("- **Coordination** : Exécuté après validation Risk et Funding")
        context_lines.append("")
        context_lines.append("## 📋 **Comment obtenir l'arborescence du projet**")
        context_lines.append("")
        context_lines.append("Pour obtenir l'arborescence complète du projet avec précision :")
        context_lines.append("")
        context_lines.append("```bash")
        context_lines.append("python project_snapshot.py")
        context_lines.append("```")
        context_lines.append("")
        context_lines.append("Cela génère automatiquement le fichier **`arborescence.md`** avec :")
        context_lines.append("- Structure complète en arbre")
        context_lines.append("- Tous les fichiers et dossiers")
        context_lines.append("- Liste des répertoires ignorés (node_modules, __pycache__, etc.)")
        context_lines.append("")
        context_lines.append("## 📖 **Documentation API HyperLiquid**")
        context_lines.append("")
        context_lines.append("La documentation complète de l'API HyperLiquid se trouve dans :")
        context_lines.append("**`@docs\\HYPERLIQUID_API_DOCUMENTATION.md`**")
        context_lines.append("")
        context_lines.append("Cette documentation contient tous les endpoints et méthodes disponibles pour l'intégration HyperLiquid.")
        context_lines.append("")
        context_lines.append("---")
        context_lines.append("")
        context_lines.append("*Skill basé sur l'analyse complète du code source réel - Système avec distinction Agent/Algorithme fondamentale*")

        # Écrire le fichier context_app.md dans le dossier contexte
        with open(contexte_dir / "context_app.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(context_lines))

    def create_agents_visualization_file(self):
        """Crée un fichier de visualisation technique des agents IA"""
        analysis = self.analyze_codebase()

        viz_lines = []
        viz_lines.append("# 🧠 Graphique Technique des Agents IA - Fonctionnement Réel")
        viz_lines.append("")
        viz_lines.append("## Vue d'ensemble des {} Agents IA".format(len(analysis["agents_ia"])))
        viz_lines.append("")
        viz_lines.append("```mermaid")
        viz_lines.append("graph TD")
        viz_lines.append("    A[Déclencheur Temporel/Event] --> B{Agent Funding}")
        viz_lines.append("    A --> C{Agent Risk}")
        viz_lines.append("    A --> D{Agent Strategy}")
        viz_lines.append("")
        viz_lines.append("    B --> B1[Analyse Funding Rates]")
        viz_lines.append("    B1 --> B2[Appel LLM Claude/OpenAI/DeepSeek]")
        viz_lines.append("    B2 --> B3[Prompt: BUY/SELL/NOTHING + Analyse]")
        viz_lines.append("    B3 --> B4[Validation avec Strategy Library]")
        viz_lines.append("    B4 --> B5[Exécution Trade via HyperLiquid API]")
        viz_lines.append("")
        viz_lines.append("    C --> C1[Check P&L Limits]")
        viz_lines.append("    C1 --> C2{> MAX_LOSS/GAIN?}")
        viz_lines.append("    C2 -->|OUI| C3[Appel LLM pour Override]")
        viz_lines.append("    C2 -->|NON| C4[Continuer Trading]")
        viz_lines.append("    C3 --> C5[Override Decision]")
        viz_lines.append("    C5 --> C6[Close All Positions]")
        viz_lines.append("")
        viz_lines.append("    D --> D1[Scan Market Conditions]")
        viz_lines.append("    D1 --> D2[Select Strategy from Library]")
        viz_lines.append("    D2 --> D3[Validate Backtest Proof]")
        viz_lines.append("    D3 --> D4[Appel LLM pour Validation Finale]")
        viz_lines.append("    D4 --> D5[Execute Signal]")
        viz_lines.append("")
        viz_lines.append("    B5 --> E[HyperLiquid Exchange]")
        viz_lines.append("    C6 --> E")
        viz_lines.append("    D5 --> E")
        viz_lines.append("")
        viz_lines.append("    E --> F[Position Management]")
        viz_lines.append("    F --> G[Logging Winston]")
        viz_lines.append("    G --> H[Portfolio Tracking]")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("## 🔄 Flux Technique Complet : De Zéro à un Ordre Vendu")
        viz_lines.append("")
        viz_lines.append("### Phase 1: Initialisation & Configuration")
        viz_lines.append("```python")
        viz_lines.append("# 1. Chargement de la configuration")
        viz_lines.append("from src import config")
        viz_lines.append("AI_MODEL = config.AI_MODEL  # \"glm-4.6\" par défaut")
        viz_lines.append("EXCHANGE = \"hyperliquid\"")
        viz_lines.append("")
        viz_lines.append("# 2. Initialisation Model Factory")
        viz_lines.append("from src.models import model_factory")
        viz_lines.append("model = model_factory.get_model(\"claude\", config.AI_MODEL)")
        viz_lines.append("")
        viz_lines.append("# 3. Connexion HyperLiquid")
        viz_lines.append("from src.hyperliquid import HyperliquidClient")
        viz_lines.append("client = HyperliquidClient()")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("### Phase 2: Agent Funding - Analyse des Taux de Financement")
        viz_lines.append("")
        viz_lines.append("```python")
        viz_lines.append("# Agent Funding se déclenche toutes les 15 minutes")
        viz_lines.append("async def funding_monitoring_cycle():")
        viz_lines.append("    # 1. Récupération des données funding")
        viz_lines.append("    funding_data = api.get_funding_data()")
        viz_lines.append("    ")
        viz_lines.append("    # 2. Filtrage des taux extrêmes")
        viz_lines.append("    extreme_rates = funding_data[")
        viz_lines.append("        (funding_data['annual_rate'] < -5) |")
        viz_lines.append("        (funding_data['annual_rate'] > 20)")
        viz_lines.append("    ]")
        viz_lines.append("    ")
        viz_lines.append("    for token, rate in extreme_rates.items():")
        viz_lines.append("        # 3. Récupération des données OHLCV")
        viz_lines.append("        candles = await client.get_candles(token, \"15m\", 100)")
        viz_lines.append("        ")
        viz_lines.append("        # 4. Construction du prompt IA")
        viz_lines.append("        prompt = FUNDING_ANALYSIS_PROMPT.format(")
        viz_lines.append("            symbol=token,")
        viz_lines.append("            rate=f\"{rate:.2f}\",")
        viz_lines.append("            market_data=format_market_data(candles),")
        viz_lines.append("            funding_data=funding_data.to_string()")
        viz_lines.append("        )")
        viz_lines.append("        ")
        viz_lines.append("        # 5. Appel LLM")
        viz_lines.append("        response = anthropic_client.messages.create(")
        viz_lines.append("            model=active_model,")
        viz_lines.append("            max_tokens=config.AI_MAX_TOKENS,")
        viz_lines.append("            temperature=config.AI_TEMPERATURE,")
        viz_lines.append("            messages=[{\"role\": \"user\", \"content\": prompt}]")
        viz_lines.append("        )")
        viz_lines.append("        ")
        viz_lines.append("        # 6. Parsing de la réponse")
        viz_lines.append("        action, analysis, confidence = parse_llm_response(response)")
        viz_lines.append("        ")
        viz_lines.append("        # 7. Validation avec Strategy Library")
        viz_lines.append("        validation = validate_with_strategy_library(token, action)")
        viz_lines.append("        ")
        viz_lines.append("        if validation['valid'] and confidence >= 70:")
        viz_lines.append("            # 8. Exécution de l'ordre")
        viz_lines.append("            await execute_funding_trade(token, action, confidence)")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("### Phase 3: Agent Risk - Gestion des Limites de Risque")
        viz_lines.append("")
        viz_lines.append("```python")
        viz_lines.append("# Agent Risk check continu des limites")
        viz_lines.append("def check_risk_limits():")
        viz_lines.append("    # 1. Calcul du P&L actuel")
        viz_lines.append("    current_balance = get_portfolio_value()")
        viz_lines.append("    pnl = current_balance - start_balance")
        viz_lines.append("    ")
        viz_lines.append("    # 2. Vérification des seuils")
        viz_lines.append("    if pnl <= -MAX_LOSS_PERCENT:")
        viz_lines.append("        # 3. Construction du prompt d'override IA")
        viz_lines.append("        prompt = RISK_OVERRIDE_PROMPT.format(")
        viz_lines.append("            limit_type=\"MAX_LOSS\",")
        viz_lines.append("            position_data=json.dumps(current_positions)")
        viz_lines.append("        )")
        viz_lines.append("        ")
        viz_lines.append("        # 4. Appel LLM pour décision d'override")
        viz_lines.append("        response = anthropic_client.messages.create(")
        viz_lines.append("            model=active_model,")
        viz_lines.append("            messages=[{\"role\": \"user\", \"content\": prompt}]")
        viz_lines.append("        )")
        viz_lines.append("        ")
        viz_lines.append("        if \"OVERRIDE\" in response.content:")
        viz_lines.append("            # 5. Continuer le trading malgré la limite")
        viz_lines.append("            return False  # Ne pas fermer")
        viz_lines.append("        else:")
        viz_lines.append("            # 6. Fermer toutes les positions")
        viz_lines.append("            close_all_positions()")
        viz_lines.append("            return True  # Stop trading")
        viz_lines.append("    ")
        viz_lines.append("    return False  # Continuer normalement")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("### Phase 4: Agent Strategy - Sélection de Stratégies")
        viz_lines.append("")
        viz_lines.append("```python")
        viz_lines.append("# Agent Strategy - sélection basée sur backtests")
        viz_lines.append("def get_strategy_signal(token):")
        viz_lines.append("    # 1. Analyse des conditions de marché")
        viz_lines.append("    market_conditions = analyze_market_conditions(token)")
        viz_lines.append("    ")
        viz_lines.append("    # 2. Sélection de la meilleure stratégie validée")
        viz_lines.append("    best_strategy = strategy_library.get_best_strategy_for_conditions(")
        viz_lines.append("        market_conditions, token")
        viz_lines.append("    )")
        viz_lines.append("    ")
        viz_lines.append("    # 3. Vérification des conditions d'entrée")
        viz_lines.append("    if not check_strategy_conditions(best_strategy, market_conditions):")
        viz_lines.append("        return None")
        viz_lines.append("    ")
        viz_lines.append("    # 4. Validation avec LLM")
        viz_lines.append("    validation_prompt = f\"Validate this strategy signal: {best_strategy['name']}\"")
        viz_lines.append("    llm_validation = anthropic_client.messages.create(")
        viz_lines.append("        model=active_model,")
        viz_lines.append("        messages=[{\"role\": \"user\", \"content\": validation_prompt}]")
        viz_lines.append("    )")
        viz_lines.append("    ")
        viz_lines.append("    if \"EXECUTE\" in llm_validation.content:")
        viz_lines.append("        # 5. Exécution du signal")
        viz_lines.append("        return execute_strategy_signal(best_strategy, token)")
        viz_lines.append("    ")
        viz_lines.append("    return None")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("## 🔗 Architecture Technique Détaillée")
        viz_lines.append("")
        viz_lines.append("### Communication Inter-Agents")
        viz_lines.append("```")
        viz_lines.append("┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐")
        viz_lines.append("│   Agent Funding │    │   Agent Risk   │    │ Agent Strategy │")
        viz_lines.append("│                 │    │                 │    │                 │")
        viz_lines.append("│ • Funding Rates │    │ • P&L Limits    │    │ • Market Scan   │")
        viz_lines.append("│ • BTC Context   │    │ • Position Mgmt │    │ • Strategy Sel  │")
        viz_lines.append("│ • LLM Analysis  │    │ • Override Dec  │    │ • Backtest Val  │")
        viz_lines.append("└─────────────────┘    └─────────────────┘    └─────────────────┘")
        viz_lines.append("         │                        │                        │")
        viz_lines.append("         └────────────────────────┼────────────────────────┘")
        viz_lines.append("                                  │")
        viz_lines.append("                    ┌─────────────────┐")
        viz_lines.append("                    │  HyperLiquid   │")
        viz_lines.append("                    │     API        │")
        viz_lines.append("                    │                 │")
        viz_lines.append("                    │ • place_order() │")
        viz_lines.append("                    │ • get_positions │")
        viz_lines.append("                    │ • cancel_order │")
        viz_lines.append("                    └─────────────────┘")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("### Flux de Données Temps Réel")
        viz_lines.append("```")
        viz_lines.append("Market Data → Agent Analysis → LLM Validation → Strategy Library → Order Execution")
        viz_lines.append("     ↑              ↑              ↑              ↑              ↑")
        viz_lines.append("     └──────────────┴──────────────┴──────────────┴──────────────┴─────────────")
        viz_lines.append("                              Logging Winston")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("## 📊 Métriques de Performance")
        viz_lines.append("")
        viz_lines.append("### Agent Funding")
        viz_lines.append("- **Fréquence**: Toutes les 15 minutes")
        viz_lines.append("- **Seuil d'activation**: |funding_rate| > 5% ou > 20%")
        viz_lines.append("- **Précision LLM**: Confidence scoring (0-100%)")
        viz_lines.append("- **Temps de réponse**: < 30 secondes")
        viz_lines.append("")
        viz_lines.append("### Agent Risk")
        viz_lines.append("- **Fréquence**: Continue (check toutes les 5 minutes)")
        viz_lines.append("- **Limites**: % ou $ configurables")
        viz_lines.append("- **Override IA**: Seuils de confiance élevés")
        viz_lines.append("- **Action**: Close all positions si nécessaire")
        viz_lines.append("")
        viz_lines.append("### Agent Strategy")
        viz_lines.append("- **Fréquence**: On-demand")
        viz_lines.append("- **Validation**: Backtest proof required")
        viz_lines.append("- **Library**: {}+ stratégies validées".format(50))
        viz_lines.append("- **LLM**: Validation finale des signaux")
        viz_lines.append("")
        viz_lines.append("## 🔧 Configuration Technique")
        viz_lines.append("")
        viz_lines.append("```python")
        viz_lines.append("# Configuration centralisée dans config.py")
        viz_lines.append("AI_MODEL = \"glm-4.6\"  # Modèle par défaut")
        viz_lines.append("AI_TEMPERATURE = 0.7  # Créativité vs précision")
        viz_lines.append("AI_MAX_TOKENS = 1024  # Longueur des réponses")
        viz_lines.append("")
        viz_lines.append("# Seuils de trading")
        viz_lines.append("FUNDING_NEG_THRESHOLD = -5  # % annuel")
        viz_lines.append("FUNDING_POS_THRESHOLD = 20  # % annuel")
        viz_lines.append("MIN_CONFIDENCE = 70         # % pour exécution")
        viz_lines.append("")
        viz_lines.append("# Limites de risque")
        viz_lines.append("MAX_LOSS_PERCENT = 5        # % perte max")
        viz_lines.append("MAX_GAIN_PERCENT = 10       # % gain max")
        viz_lines.append("USE_AI_OVERRIDE = True      # Autoriser override IA")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("## 🚨 Points Critiques")
        viz_lines.append("")
        viz_lines.append("1. **Validation Backtest**: Aucun trade sans preuve backtest")
        viz_lines.append("2. **LLM comme Assistant**: IA valide, humain contrôle final")
        viz_lines.append("3. **Logging Complet**: Chaque décision tracée")
        viz_lines.append("4. **Risque Management**: Limites strictes + override IA")
        viz_lines.append("5. **Performance Temps Réel**: < 30s de latence max")
        viz_lines.append("")
        viz_lines.append("---")
        viz_lines.append("")
        viz_lines.append("*Ce graphique représente le fonctionnement technique réel du système, de l'analyse de marché à l'exécution d'ordre sur HyperLiquid.*")

        # Créer le dossier docs s'il n'existe pas
        docs_dir = self.root_path / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Écrire le fichier de visualisation
        with open(docs_dir / "AGENTS_GRAPH_VISUALIZATION.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(viz_lines))


def main():
    """Fonction principale"""
    snapshot = ProjectSnapshot()
    snapshot.generate_tree()


if __name__ == "__main__":
    main()
