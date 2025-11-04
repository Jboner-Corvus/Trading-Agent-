projet trading/
├── backend/
│   ├── backtest_validator.js
│   ├── server-backend.js
│   └── server-backend.ts
├── contexte/
│   ├── arborescence.md
│   └── context_app.md
├── docs/
│   ├── AGENTS_GRAPH_VISUALIZATION.md
│   ├── HYPERLIQUID_API_DOCUMENTATION.md
│   └── LOG_SYSTEM_DOCUMENTATION.md
├── frontend/
│   ├── public/
│   │   ├── assets/
│   │   │   └── novaquote.css
│   │   ├── backtest.html
│   │   ├── config.html
│   │   ├── index.html
│   │   ├── test_agents.html
│   │   └── validate_config.html
│   ├── server-frontend.js
│   └── server-frontend.ts
├── package-lock.json
├── package.json
├── README.md
├── requirements.txt
├── run.js
├── run.ts
├── scripts/
│   ├── lint-format-py.py
│   ├── optimize_all_strategies.py
│   └── project_snapshot.py
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── base_agent.py
│   │   ├── funding_agent.py
│   │   ├── intelligent_backtest_optimizer.py
│   │   ├── manager.py
│   │   ├── risk_agent.py
│   │   ├── sentiment_analysis_agent.py
│   │   ├── strategy_agent.py
│   │   └── strategy_library.py
│   ├── config.py
│   ├── data/
│   │   └── production_backtests/
│   │       ├── BB_Squeeze_62_PRO_FINAL_results.json
│   │       ├── BTCDominance_FINAL.py
│   │       ├── DivergentVolReversal_FINAL.py
│   │       ├── Fear_Contrarian_73_PRO_FINAL_results.json
│   │       ├── FractalCascade_FINAL.py
│   │       ├── Funding_Arbitrage_85_PRO_FINAL_results.json
│   │       ├── GoldenCrossover_FINAL.py
│   │       ├── MACD_Crossover_65_PRO_FINAL_results.json
│   │       ├── README.md
│   │       ├── RSI_Oversold_68_PRO_FINAL_results.json
│   │       ├── Twitter_Sentiment_69_PRO_FINAL_results.json
│   │       ├── VolatilityEngulfing_FINAL.py
│   │       └── Volume_Breakout_71_PRO_FINAL_results.json
│   ├── hyperliquid/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── hyperliquid-api.js
│   │   ├── hyperliquid-signature.js
│   │   ├── hyperliquid-websocket.js
│   │   ├── signing.py
│   │   ├── types.py
│   │   └── websocket.py
│   ├── logger.js
│   ├── metamask_integration_example.js
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── claude_model.py
│   │   ├── deepseek_model.py
│   │   ├── gemini_model.py
│   │   ├── groq_model.py
│   │   ├── model_factory.py
│   │   ├── ollama_model.py
│   │   ├── openai_model.py
│   │   ├── README.md
│   │   ├── xai_model.py
│   │   └── zai_model.py
│   ├── nice_funcs.py
│   ├── nice_funcs_hyperliquid.py
│   └── wallet/
│       ├── __init__.py
│       ├── api_wallet_manager.py
│       ├── permission_controller.py
│       ├── signature_engine.py
│       └── wallet_registry.py
├── test/
│   └── test_system.js
└── tsconfig.json

ignore:
  - logs/
  - node_modules/
  - src\hyperliquid\__pycache__/
  - src\wallet\__pycache__/