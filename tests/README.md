# 🧪 Tests NOVAQUOTE Trading System

Ce dossier contient tous les tests du système de trading NOVAQUOTE.

## 📁 Structure des tests

```
tests/
├── README.md                    # Documentation des tests
├── run-all-tests.js            # Lanceur de tous les tests
├── test-system.js              # Tests de santé du système
└── test-structured-logger.js   # Tests du logging structuré
```

## 🚀 Exécution des tests

### Exécuter tous les tests
```bash
node tests/run-all-tests.js
```

### Exécuter un test spécifique

#### Tests système (backend/frontend/API)
```bash
node tests/test-system.js
```

#### Tests du système de logging
```bash
node tests/test-structured-logger.js
```

## 📋 Description des tests

### 1. System Health Tests (`test-system.js`)
- ✅ Test de santé du backend (port 7000)
- ✅ Test de santé du frontend (port 9001)
- ✅ Test des API backtests
- ✅ Vérification des processus Node.js actifs

**Prérequis :** Les serveurs doivent être démarrés avec `node run.js start`

### 2. Structured Logging Tests (`test-structured-logger.js`)
- ✅ Tests des logs basiques (info, debug, warn, error)
- ✅ Tests des logs de performance
- ✅ Tests des logs de trading
- ✅ Tests des logs de sécurité
- ✅ Tests des logs d'agents IA
- ✅ Tests des logs WebSocket
- ✅ Tests des health checks
- ✅ Tests des métriques
- ✅ Tests du contexte global
- ✅ Vérification de la rotation des fichiers

**Fichiers générés :** Les logs sont créés dans le dossier `logs/` avec rotation automatique.

## 📊 Résultats des tests

Les tests retournent :
- `0` si tous les tests passent ✅
- `1` si un ou plusieurs tests échouent ❌

## 🔧 Maintenance

Pour ajouter un nouveau test :

1. Créer le fichier `test-xxx.js` dans ce dossier
2. Ajouter le test dans `run-all-tests.js`
3. Documenter le test dans ce README

## 📝 Notes importantes

- Les tests sont conçus pour être exécutés dans un environnement de développement
- Les tests système nécessitent que les serveurs soient en cours d'exécution
- Les tests de logging génèrent des fichiers dans `logs/`
- Le système de logging utilise Winston avec rotation automatique des fichiers

## 🚨 Dépannage

### Erreur "Connection refused"
- Assurez-vous que les serveurs sont démarrés : `node run.js start`
- Vérifiez que les ports 7000 et 9001 sont disponibles

### Erreur "Module not found"
- Vérifiez que toutes les dépendances sont installées : `npm install`
- Assurez-vous que les chemins dans les fichiers de test sont corrects

### Problèmes avec les logs
- Vérifiez que le dossier `logs/` existe et est accessible en écriture
- Vérifiez que Winston est correctement installé : `npm install winston winston-daily-rotate-file`