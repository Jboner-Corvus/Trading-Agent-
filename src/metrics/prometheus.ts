/**
 * 📊 Métriques Prometheus
 * Monitoring des performances et métriques business
 */

import { register, Counter, Histogram, Gauge } from 'prom-client';

// Compteurs HTTP
export const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code', 'user_agent']
});

export const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
});

export const httpResponseSize = new Histogram({
  name: 'http_response_size_bytes',
  help: 'Size of HTTP responses in bytes',
  labelNames: ['method', 'route'],
  buckets: [100, 500, 1000, 5000, 10000, 50000, 100000, 500000]
});

// Métriques WebSocket
export const websocketConnectionsActive = new Gauge({
  name: 'websocket_connections_active',
  help: 'Number of active WebSocket connections'
});

export const websocketConnectionsTotal = new Counter({
  name: 'websocket_connections_total',
  help: 'Total number of WebSocket connections',
  labelNames: ['status'] // connected, disconnected, error
});

export const websocketMessagesTotal = new Counter({
  name: 'websocket_messages_total',
  help: 'Total number of WebSocket messages',
  labelNames: ['type'] // sent, received, error
});

export const websocketMessageDuration = new Histogram({
  name: 'websocket_message_duration_seconds',
  help: 'Duration of WebSocket message processing',
  labelNames: ['message_type'],
  buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
});

// Métriques Trading
export const tradesTotal = new Counter({
  name: 'trades_total',
  help: 'Total number of trades executed',
  labelNames: ['symbol', 'side', 'status', 'user_id']
});

export const tradeVolume = new Counter({
  name: 'trade_volume_usd',
  help: 'Total trading volume in USD',
  labelNames: ['symbol', 'side']
});

export const tradeSuccessRate = new Gauge({
  name: 'trade_success_rate',
  help: 'Success rate of trades (0-1)',
  labelNames: ['symbol', 'timeframe']
});

export const activePositions = new Gauge({
  name: 'active_positions',
  help: 'Number of active positions',
  labelNames: ['symbol', 'side']
});

export const totalPnL = new Gauge({
  name: 'total_pnl_usd',
  help: 'Total P&L in USD',
  labelNames: ['symbol', 'type'] // realized, unrealized
});

// Métriques API HyperLiquid
export const hyperliquidApiRequests = new Counter({
  name: 'hyperliquid_api_requests_total',
  help: 'Total number of HyperLiquid API requests',
  labelNames: ['endpoint', 'method', 'status']
});

export const hyperliquidApiDuration = new Histogram({
  name: 'hyperliquid_api_duration_seconds',
  help: 'Duration of HyperLiquid API requests',
  labelNames: ['endpoint'],
  buckets: [0.1, 0.25, 0.5, 1, 2, 5, 10, 15, 30]
});

export const hyperliquidApiErrors = new Counter({
  name: 'hyperliquid_api_errors_total',
  help: 'Total number of HyperLiquid API errors',
  labelNames: ['endpoint', 'error_type', 'http_status']
});

// Métriques Agents IA
export const agentsActive = new Gauge({
  name: 'agents_active',
  help: 'Number of active AI agents',
  labelNames: ['agent_type']
});

export const agentExecutions = new Counter({
  name: 'agent_executions_total',
  help: 'Total number of agent executions',
  labelNames: ['agent_type', 'status', 'decision']
});

export const agentDecisionTime = new Histogram({
  name: 'agent_decision_duration_seconds',
  help: 'Time taken for agent decision making',
  labelNames: ['agent_type'],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60]
});

// Métriques Système
export const systemMemoryUsage = new Gauge({
  name: 'system_memory_usage_bytes',
  help: 'Memory usage in bytes',
  labelNames: ['type'] // used, available, total
});

export const systemCpuUsage = new Gauge({
  name: 'system_cpu_usage_percentage',
  help: 'CPU usage percentage'
});

export const processUptime = new Gauge({
  name: 'process_uptime_seconds',
  help: 'Process uptime in seconds'
});

export const eventLoopLag = new Histogram({
  name: 'eventloop_lag_seconds',
  help: 'Event loop lag in seconds',
  buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]
});

// Métriques Erreurs
export const errorsTotal = new Counter({
  name: 'errors_total',
  help: 'Total number of errors',
  labelNames: ['type', 'severity', 'component']
});

export const circuitBreakerState = new Gauge({
  name: 'circuit_breaker_state',
  help: 'Circuit breaker state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)',
  labelNames: ['service', 'operation']
});

export const retryAttempts = new Counter({
  name: 'retry_attempts_total',
  help: 'Total number of retry attempts',
  labelNames: ['operation', 'attempt_number']
});

// Métriques Cache
export const cacheHits = new Counter({
  name: 'cache_hits_total',
  help: 'Total number of cache hits',
  labelNames: ['cache_type', 'key_prefix']
});

export const cacheMisses = new Counter({
  name: 'cache_misses_total',
  help: 'Total number of cache misses',
  labelNames: ['cache_type', 'key_prefix']
});

export const cacheSize = new Gauge({
  name: 'cache_size_bytes',
  help: 'Cache size in bytes',
  labelNames: ['cache_type']
});

// Export du registre pour l'exposition
export const prometheusRegister = register;

// Service de métriques
export class MetricsService {
  /**
   * 🎯 Enregistrer une requête HTTP
   */
  static recordHttpRequest(method: string, route: string, statusCode: number, duration: number, responseSize: number, userAgent?: string): void {
    const labels = {
      method,
      route: route || 'unknown',
      status_code: statusCode.toString(),
      user_agent: userAgent || 'unknown'
    };

    httpRequestsTotal.inc(labels);
    httpRequestDuration.observe(labels, duration / 1000);
    httpResponseSize.observe(labels, responseSize);
  }

  /**
   * 🔄 Enregistrer une connexion WebSocket
   */
  static recordWebSocketConnection(status: 'connected' | 'disconnected' | 'error'): void {
    if (status === 'connected') {
      websocketConnectionsActive.inc();
    } else {
      websocketConnectionsActive.dec();
    }
    websocketConnectionsTotal.inc({ status });
  }

  /**
   * 💰 Enregistrer un trade
   */
  static recordTrade(symbol: string, side: string, status: 'success' | 'failed', volume: number, userId?: string): void {
    tradesTotal.inc({
      symbol,
      side,
      status,
      user_id: userId || 'anonymous'
    });
    tradeVolume.inc({ symbol, side }, volume);

    if (status === 'success') {
      this.updateTradeSuccessRate(symbol, true);
    } else {
      this.updateTradeSuccessRate(symbol, false);
    }
  }

  /**
   * 📈 Mettre à jour le taux de réussite des trades
   */
  private static updateTradeSuccessRate(symbol: string, success: boolean): void {
    // Cette méthode nécessite de suivre les stats globales
    // Pour simplifier, on utilise une approximation
    const currentRate = tradeSuccessRate.get({ symbol, timeframe: '5m' }) || 0;
    const alpha = 0.1; // Facteur de lissage
    const newRate = alpha * (success ? 1 : 0) + (1 - alpha) * currentRate;
    tradeSuccessRate.set({ symbol, timeframe: '5m' }, newRate);
  }

  /**
   * 🤖 Enregistrer une exécution d'agent
   */
  static recordAgentExecution(agentType: string, status: string, decision: string, duration: number): void {
    agentExecutions.inc({
      agent_type: agentType,
      status,
      decision
    });
    agentDecisionTime.observe({ agent_type: agentType }, duration / 1000);
  }

  /**
   * ⚡ Enregistrer une requête API HyperLiquid
   */
  static recordHyperliquidApiRequest(endpoint: string, method: string, status: number, duration: number): void {
    hyperliquidApiRequests.inc({
      endpoint,
      method,
      status: status.toString()
    });
    hyperliquidApiDuration.observe({ endpoint }, duration / 1000);

    if (status >= 400) {
      hyperliquidApiErrors.inc({
        endpoint,
        error_type: status >= 500 ? 'server_error' : 'client_error',
        http_status: status.toString()
      });
    }
  }

  /**
   * 🔌 Mettre à jour les connexions WebSocket actives
   */
  static updateActiveWebSocketConnections(count: number): void {
    websocketConnectionsActive.set(count);
  }

  /**
   * 📊 Mettre à jour les positions actives
   */
  static updateActivePositions(positions: Array<{ symbol: string; side: string }>): void {
    // Reset all positions first
    register.clear();

    positions.forEach(pos => {
      activePositions.inc({
        symbol: pos.symbol,
        side: pos.side
      });
    });
  }

  /**
   * 💰 Mettre à jour le P&L total
   */
  static updateTotalPnL(symbol: string, realized: number, unrealized: number): void {
    totalPnL.set({ symbol, type: 'realized' }, realized);
    totalPnL.set({ symbol, type: 'unrealized' }, unrealized);
  }

  /**
   * 🤖 Mettre à jour les agents actifs
   */
  static updateActiveAgents(agents: Array<{ type: string }>): void {
    // Reset first
    agentsActive.reset();

    // Count by type
    const agentCounts: { [key: string]: number } = {};
    agents.forEach(agent => {
      agentCounts[agent.type] = (agentCounts[agent.type] || 0) + 1;
    });

    Object.entries(agentCounts).forEach(([type, count]) => {
      agentsActive.set({ agent_type: type }, count);
    });
  }

  /**
   * ❌ Enregistrer une erreur
   */
  static recordError(type: string, severity: string, component: string): void {
    errorsTotal.inc({
      type,
      severity,
      component
    });
  }

  /**
   * 🔄 Mettre à jour l'état du circuit breaker
   */
  static updateCircuitBreakerState(service: string, operation: string, state: 'CLOSED' | 'HALF_OPEN' | 'OPEN'): void {
    const stateValue = state === 'CLOSED' ? 0 : state === 'HALF_OPEN' ? 1 : 2;
    circuitBreakerState.set({ service, operation }, stateValue);
  }

  /**
   * 📈 Démarrer le monitoring des métriques système
   */
  static startSystemMonitoring(): void {
    // Monitoring mémoire
    setInterval(() => {
      const memUsage = process.memoryUsage();
      systemMemoryUsage.set({ type: 'used' }, memUsage.heapUsed);
      systemMemoryUsage.set({ type: 'available' }, memUsage.heapTotal - memUsage.heapUsed);
      systemMemoryUsage.set({ type: 'total' }, memUsage.heapTotal);
    }, 5000);

    // Monitoring uptime
    setInterval(() => {
      processUptime.set(process.uptime());
    }, 10000);

    // Monitoring Event Loop Lag
    setInterval(() => {
      const start = process.hrtime.bigint();
      setImmediate(() => {
        const lag = Number(process.hrtime.bigint() - start) / 1e9;
        eventLoopLag.observe(lag);
      });
    }, 1000);
  }
}

export default MetricsService;