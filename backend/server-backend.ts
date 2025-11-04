/**
 * NOVAQUOTE BACKEND SERVER - HyperLiquid Optimized
 * Port 7000 - APIs + WebSocket
 * Intégré avec les modules HyperLiquid optimisés
 */

import express, { Express, Request, Response, NextFunction } from 'express';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

// Types
interface Colors {
  reset: string;
  bright: string;
  dim: string;
  red: string;
  green: string;
  yellow: string;
  blue: string;
  magenta: string;
  cyan: string;
  white: string;
}

interface LogFunction {
  (msg: string, category?: string): void;
}

interface HyperliquidLogs {
  api: LogFunction;
  price: (symbol: string, price: number) => void;
  tokens: (count: number) => void;
  error: LogFunction;
}

interface TradingLogs {
  order: (symbol: string, side: string, size: string) => void;
  position: (symbol: string, action: string) => void;
  success: LogFunction;
  error: LogFunction;
}

interface ApiLogs {
  request: (method: string, path: string) => void;
  response: (path: string, status: number) => void;
  error: (path: string, error: string) => void;
}

interface AgentLogs {
  start: (type: string) => void;
  stop: (type: string) => void;
  status: (type: string, status: string) => void;
}

interface DataLogs {
  load: (source: string, count: number) => void;
  cache: (action: string, key: string) => void;
  error: (source: string, error: string) => void;
}

interface PerfLogs {
  start: (label: string) => void;
  end: (label: string) => void;
  log: (label: string, value: number) => void;
}

interface Logger {
  info: LogFunction;
  success: LogFunction;
  error: LogFunction;
  warn: LogFunction;
  hyperliquid: HyperliquidLogs;
  trading: TradingLogs;
  api: ApiLogs;
  agent: AgentLogs;
  data: DataLogs;
  perf: PerfLogs;
}

interface HealthStatus {
  status: string;
  timestamp: string;
  uptime: number;
  services: {
    api: boolean;
    websocket: boolean;
    hyperliquid: boolean;
  };
}

// 🚀 Logger Ultra-Efficace - HyperLiquid Optimized
const getTimestamp = (): string => {
  return new Date().toISOString().split('T')[1]!.replace('Z', '').slice(0, -1);
};

const colors: Colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
};

const log: Logger = {
  // 🎯 General Logs
  info: (msg: string, category: string = 'SYSTEM'): void => {
    const timestamp = getTimestamp();
    console.log(`[${timestamp}] [${colors.cyan}INFO${colors.reset}] [${colors.blue}${category}${colors.reset}] ℹ️  ${msg}`);
  },

  success: (msg: string, category: string = 'SYSTEM'): void => {
    const timestamp = getTimestamp();
    console.log(`[${timestamp}] [${colors.green}SUCCESS${colors.reset}] [${colors.blue}${category}${colors.reset}] ✅ ${msg}`);
  },

  error: (msg: string, category: string = 'ERROR'): void => {
    const timestamp = getTimestamp();
    console.log(`[${timestamp}] [${colors.red}ERROR${colors.reset}] [${colors.magenta}${category}${colors.reset}] ❌ ${msg}`);
  },

  warn: (msg: string, category: string = 'WARNING'): void => {
    const timestamp = getTimestamp();
    console.log(`[${timestamp}] [${colors.yellow}WARN${colors.reset}] [${colors.blue}${category}${colors.reset}] ⚠️  ${msg}`);
  },

  // 🚀 HyperLiquid Specific Logs
  hyperliquid: {
    api: (msg: string) => log.info(msg, 'HYPERLIQUID-API'),
    price: (symbol: string, price: number) => {
      log.success(`💰 ${symbol}: $${price.toLocaleString()}`, 'HYPERLIQUID-PRICE');
    },
    tokens: (count: number) => {
      log.success(`📊 Loaded ${count} tokens from HyperLiquid API`, 'HYPERLIQUID-TOKENS');
    },
    error: (msg: string) => log.error(msg, 'HYPERLIQUID-ERROR'),
  },

  // 📊 Trading Logs
  trading: {
    order: (symbol: string, side: string, size: string) => {
      log.info(`📈 ${side.toUpperCase()} ${size} ${symbol}`, 'TRADING-ORDER');
    },
    position: (symbol: string, action: string) => {
      log.info(`🎯 Position ${action}: ${symbol}`, 'TRADING-POSITION');
    },
    success: (msg: string) => log.success(msg, 'TRADING-SUCCESS'),
    error: (msg: string) => log.error(msg, 'TRADING-ERROR'),
  },

  // 💡 API Logs
  api: {
    request: (method: string, path: string) => {
      log.info(`${method} ${path}`, 'API-REQUEST');
    },
    response: (path: string, status: number) => {
      const color = status >= 200 && status < 300 ? colors.green : colors.red;
      console.log(`[${getTimestamp()}] [${color}RESPONSE${colors.reset}] [${colors.cyan}API${colors.reset}] ${path} → ${color}${status}${colors.reset}`);
    },
    error: (path: string, error: string) => {
      log.error(`${path}: ${error}`, 'API-ERROR');
    },
  },

  // 🤖 Agent Logs
  agent: {
    start: (type: string) => {
      log.success(`🚀 Starting ${type} agent`, 'AGENT-CONTROL');
    },
    stop: (type: string) => {
      log.warn(`🛑 Stopping ${type} agent`, 'AGENT-CONTROL');
    },
    status: (type: string, status: string) => {
      log.info(`📊 ${type} agent: ${status}`, 'AGENT-STATUS');
    },
  },

  // 📈 Data Logs
  data: {
    load: (source: string, count: number) => {
      log.success(`📦 Loaded ${count} items from ${source}`, 'DATA-LOAD');
    },
    cache: (action: string, key: string) => {
      log.info(`${action} cache: ${key}`, 'DATA-CACHE');
    },
    error: (source: string, error: string) => {
      log.error(`${source}: ${error}`, 'DATA-ERROR');
    },
  },

  // 🎨 Performance Logs
  perf: {
    start: (label: string) => {
      console.time(`[${getTimestamp()}] [${colors.magenta}PERF${colors.reset}] ${label}`);
    },
    end: (label: string) => {
      console.timeEnd(`[${getTimestamp()}] [${colors.magenta}PERF${colors.reset}] ${label}`);
    },
    log: (label: string, value: number) => {
      log.info(`${label}: ${value}ms`, 'PERFORMANCE');
    },
  },
};

const app: Express = express();
const PORT: number = 7000;
const WS_PORT: number = 7002;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ============================================================================
// HYPERLIQUID INTEGRATION
// ============================================================================

// Import des vrais modules HyperLiquid
let HyperliquidAPI: any = null;
let HyperliquidWebSocket: any = null;

try {
  HyperliquidAPI = require('../src/hyperliquid/hyperliquid-api');
  HyperliquidWebSocket = require('../src/hyperliquid/hyperliquid-websocket');
  log.success('HyperLiquid modules loaded successfully');
} catch (error: any) {
  log.error(`Failed to load HyperLiquid modules: ${error.message}`);
}

// HyperLiquid API instance
let hlAPI: any = null;
let hlWS: any = null;

// Initialize HyperLiquid API
async function initializeHyperLiquid(): Promise<void> {
  try {
    if (HyperliquidAPI) {
      hlAPI = new HyperliquidAPI();
      await hlAPI.initialize();
      log.success('HyperLiquid API initialized');
    }
  } catch (error: any) {
    log.error(`Failed to initialize HyperLiquid API: ${error.message}`);
  }
}

// Initialize HyperLiquid WebSocket
function initializeHyperLiquidWS(): void {
  try {
    if (HyperliquidWebSocket) {
      hlWS = new HyperliquidWebSocket();
      hlWS.connect();
      log.success('HyperLiquid WebSocket connected');
    }
  } catch (error: any) {
    log.error(`Failed to initialize HyperLiquid WebSocket: ${error.message}`);
  }
}

// ============================================================================
// WEBSOCKET SERVER
// ============================================================================

const wss = new WebSocketServer({ port: WS_PORT });

wss.on('connection', (ws) => {
  log.info('New WebSocket connection established', 'WEBSOCKET');

  ws.send(JSON.stringify({
    type: 'connection',
    message: 'Connected to NOVAQUOTE Backend WebSocket',
    timestamp: new Date().toISOString()
  }));

  ws.on('message', (data: any) => {
    try {
      const message = JSON.parse(data.toString());
      log.info(`WebSocket message received: ${message.type}`, 'WEBSOCKET');

      // Handle different message types
      switch (message.type) {
        case 'ping':
          ws.send(JSON.stringify({
            type: 'pong',
            timestamp: new Date().toISOString()
          }));
          break;

        case 'subscribe':
          handleSubscription(ws, message);
          break;

        default:
          log.warn(`Unknown WebSocket message type: ${message.type}`, 'WEBSOCKET');
      }
    } catch (error: any) {
      log.error(`WebSocket message parsing error: ${error.message}`, 'WEBSOCKET');
    }
  });

  ws.on('close', () => {
    log.info('WebSocket connection closed', 'WEBSOCKET');
  });

  ws.on('error', (error: Error) => {
    log.error(`WebSocket error: ${error.message}`, 'WEBSOCKET');
  });
});

function handleSubscription(ws: any, message: any): void {
  const { channel, symbol } = message;

  log.info(`Subscription request: ${channel} for ${symbol}`, 'WEBSOCKET');

  // Here you would implement actual subscription logic
  ws.send(JSON.stringify({
    type: 'subscription',
    channel,
    symbol,
    status: 'subscribed',
    timestamp: new Date().toISOString()
  }));
}

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Request logging middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  log.api.request(req.method, req.path);
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    log.api.response(req.path, res.statusCode);
    log.perf.log(`${req.method} ${req.path}`, duration);
  });

  next();
});

// Error handling middleware
app.use((error: Error, req: Request, res: Response, _next: NextFunction) => {
  log.api.error(req.path, error.message);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env['NODE_ENV'] === 'development' ? error.message : 'Something went wrong'
  });
});

// ============================================================================
// API ROUTES
// ============================================================================

// Health check endpoint
app.get('/api/health', (req: Request, res: Response) => {
  const health: HealthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    services: {
      api: true,
      websocket: wss.clients.size > 0,
      hyperliquid: hlAPI !== null
    }
  };

  res.json(health);
});

// HyperLiquid endpoints
app.get('/api/hyperliquid/tokens', async (req: Request, res: Response) => {
  try {
    if (!hlAPI) {
      return res.status(503).json({ error: 'HyperLiquid API not available' });
    }

    const tokens = await hlAPI.getAllTokens();
    log.hyperliquid.tokens(tokens.length);
    res.json({ tokens });
  } catch (error: any) {
    log.hyperliquid.error(error.message);
    res.status(500).json({ error: 'Failed to fetch tokens' });
  }
});

app.get('/api/hyperliquid/price/:symbol', async (req: Request, res: Response) => {
  try {
    const { symbol } = req.params;

    if (!hlAPI) {
      return res.status(503).json({ error: 'HyperLiquid API not available' });
    }

    const price = await hlAPI.getTokenPrice(symbol);
    log.hyperliquid.price(symbol, price);
    res.json({ symbol, price });
  } catch (error: any) {
    log.hyperliquid.error(error.message);
    res.status(500).json({ error: 'Failed to fetch price' });
  }
});

// Trading endpoints
app.post('/api/trading/order', async (req: Request, res: Response) => {
  try {
    const { symbol, side, size, price } = req.body;

    if (!hlAPI) {
      return res.status(503).json({ error: 'HyperLiquid API not available' });
    }

    log.trading.order(symbol, side, size);

    // Execute order logic here
    const result = await hlAPI.placeOrder({
      symbol,
      side,
      size,
      price
    });

    log.trading.success(`Order placed: ${result.orderId}`);
    res.json({ success: true, orderId: result.orderId });
  } catch (error: any) {
    log.trading.error(error.message);
    res.status(500).json({ error: 'Failed to place order' });
  }
});

// Agent management endpoints
app.get('/api/agents', (req: Request, res: Response) => {
  const agents = [
    { id: 'risk', name: 'Risk Agent', status: 'active' },
    { id: 'strategy', name: 'Strategy Agent', status: 'active' },
    { id: 'funding', name: 'Funding Agent', status: 'inactive' }
  ];

  res.json({ agents });
});

app.post('/api/agents/:agentId/start', (req: Request, res: Response) => {
  const { agentId } = req.params;
  log.agent.start(agentId);
  res.json({ success: true, message: `${agentId} agent started` });
});

app.post('/api/agents/:agentId/stop', (req: Request, res: Response) => {
  const { agentId } = req.params;
  log.agent.stop(agentId);
  res.json({ success: true, message: `${agentId} agent stopped` });
});

// Data endpoints
app.get('/api/data/backtest', async (req: Request, res: Response) => {
  try {
    const { symbol, strategy } = req.query;

    // Mock backtest data
    const backtestData = {
      symbol,
      strategy,
      results: {
        totalReturn: 15.5,
        winRate: 0.65,
        maxDrawdown: -8.2,
        sharpeRatio: 1.8
      }
    };

    log.data.load('backtest', 1);
    res.json(backtestData);
  } catch (error: any) {
    log.data.error('backtest', error.message);
    res.status(500).json({ error: 'Failed to load backtest data' });
  }
});

// ============================================================================
// PYTHON INTEGRATION
// ============================================================================

/**
 * Fonction utilitaire pour exécuter du code Python HyperLiquid
 */
function executePythonScript(scriptPath: string, args: string[] = []): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [scriptPath, ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout?.on('data', (data: Buffer) => {
      stdout += data.toString();
    });

    pythonProcess.stderr?.on('data', (data: Buffer) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code: number | null) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          resolve({ output: stdout });
        }
      } else {
        reject(new Error(`Python script failed with code ${code}: ${stderr}`));
      }
    });

    pythonProcess.on('error', (error: Error) => {
      reject(error);
    });
  });
}

// Python execution endpoint
app.post('/api/python/execute', async (req: Request, res: Response) => {
  try {
    const { script, args = [] } = req.body;

    if (!script) {
      return res.status(400).json({ error: 'Script path is required' });
    }

    const result = await executePythonScript(script, args);
    res.json({ success: true, result });
  } catch (error: any) {
    log.error(`Python execution error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// AGENT MASTER DASHBOARD - TEMPS RÉEL
// ============================================================================

/**
 * 📊 Dashboard data endpoint - Temps réel des agents
 */
app.get('/api/dashboard/real-time', async (req: Request, res: Response) => {
  try {
    const dashboardFile = path.join(__dirname, '../backend/dashboard_data.json');

    if (fs.existsSync(dashboardFile)) {
      const dashboardData = fs.readFileSync(dashboardFile, 'utf8');
      const data = JSON.parse(dashboardData);

      log.api.request('GET', '/api/dashboard/real-time');
      log.info('📊 Dashboard data fetched successfully', 'DASHBOARD');

      res.json({
        success: true,
        data: data,
        timestamp: new Date().toISOString()
      });
    } else {
      // Mock data for testing dashboard
      const now = new Date();
      const currentCycle = `2025-11-04_${now.getHours().toString().padStart(2, '0')}:${Math.floor(now.getMinutes() / 20) * 20}`;

      const mockData = {
        timestamp: new Date().toISOString(),
        current_cycle: currentCycle,
        next_cycle: new Date(now.getTime() + 20 * 60 * 1000).toISOString().substring(11, 16),
        system_status: 'EXCELLENT',
        active_agents: {
          'risk_agent': {
            status: 'SUCCESS',
            confidence: 0.85,
            llm_calls: 2,
            last_update: new Date().toISOString(),
            execution_time_ms: 150
          },
          'strategy_agent': {
            status: 'SUCCESS',
            confidence: 0.92,
            signals: 3,
            last_update: new Date().toISOString(),
            execution_time_ms: 230
          },
          'funding_agent': {
            status: 'SUCCESS',
            confidence: 0.78,
            arbitrage: 1,
            last_update: new Date().toISOString(),
            execution_time_ms: 180
          },
          'sentiment_agent': {
            status: 'SUCCESS',
            confidence: 0.67,
            mood: 'Bullish 65%',
            last_update: new Date().toISOString(),
            execution_time_ms: 120
          }
        },
        current_decision: {
          decision: 'EXECUTER_BUY_SIGNALS',
          confidence: 0.89,
          expected_roi: 0.0023,
          summary: {
            buy_signals: 3,
            sell_signals: 0,
            avg_confidence: 0.82,
            agents_status: {
              'risk_agent': 'SUCCESS',
              'strategy_agent': 'SUCCESS',
              'funding_agent': 'SUCCESS',
              'sentiment_agent': 'SUCCESS'
            }
          },
          timestamp: new Date().toISOString()
        },
        performance_stats: {
          total_cycles: 72,
          success_rate: 0.875,
          average_confidence: 0.84,
          net_profit: 1247,
          recent_cycles: []
        },
        recent_cycles: [],
        alerts: []
      };

      log.api.request('GET', '/api/dashboard/real-time');
      log.info('📊 Mock dashboard data sent (Master Agent not running)', 'DASHBOARD');

      res.json({
        success: true,
        data: mockData,
        timestamp: new Date().toISOString(),
        note: 'Mock data - Master Agent not running'
      });
    }
  } catch (error: any) {
    log.error(`Dashboard fetch error: ${error.message}`, 'DASHBOARD-ERROR');
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * 🚀 Start Agent Master endpoint
 */
app.post('/api/agents/master/start', async (req: Request, res: Response) => {
  try {
    log.api.request('POST', '/api/agents/master/start');
    log.agent.start('MASTER_AGENT');

    const masterAgentScript = path.join(__dirname, '../src/agents/master_agent.py');
    const env = { ...process.env, PYTHONPATH: path.join(__dirname, '..') };

    // Start the master agent in background
    const masterProcess = spawn('python', [masterAgentScript], {
      detached: false,
      stdio: 'pipe',
      env: env
    });

    let outputBuffer = '';
    masterProcess.stdout?.on('data', (data: Buffer) => {
      outputBuffer += data.toString();
      // Log agent output
      log.info(`[MASTER_AGENT] ${data.toString().trim()}`, 'AGENT-OUTPUT');
    });

    masterProcess.stderr?.on('data', (data: Buffer) => {
      log.error(`[MASTER_AGENT ERROR] ${data.toString().trim()}`, 'AGENT-ERROR');
    });

    masterProcess.on('error', (error: Error) => {
      log.error(`Master agent failed to start: ${error.message}`, 'AGENT-ERROR');
    });

    masterProcess.on('exit', (code: number | null) => {
      if (code !== 0) {
        log.error(`Master agent exited with code ${code}`, 'AGENT-EXIT');
      } else {
        log.warn('Master agent exited normally', 'AGENT-EXIT');
      }
    });

    log.success('🚀 Agent Master started successfully', 'AGENT-MASTER');
    log.trading.success(`PID: ${masterProcess.pid}`);

    res.json({
      success: true,
      message: 'Agent Master started successfully',
      pid: masterProcess.pid,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    log.error(`Failed to start Agent Master: ${error.message}`, 'AGENT-MASTER-ERROR');
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * 🛑 Stop Agent Master endpoint
 */
app.post('/api/agents/master/stop', async (req: Request, res: Response) => {
  try {
    log.api.request('POST', '/api/agents/master/stop');
    log.agent.stop('MASTER_AGENT');

    // Find and kill master agent processes
    const { execSync } = require('child_process');

    try {
      // Kill Python processes running master_agent.py
      if (process.platform === 'win32') {
        execSync(`powershell "Get-Process | Where-Object {$_.ProcessName -like '*python*' -and $_.CommandLine -like '*master_agent*'} | Stop-Process -Force"`, {
          stdio: 'ignore'
        });
      } else {
        execSync(`pkill -f master_agent.py`, { stdio: 'ignore' });
      }

      log.success('Agent Master stopped successfully', 'AGENT-MASTER');
    } catch (killError) {
      log.warn(`Could not stop Agent Master: ${killError.message}`, 'AGENT-MASTER-WARNING');
    }

    res.json({
      success: true,
      message: 'Agent Master stop request sent',
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    log.error(`Failed to stop Agent Master: ${error.message}`, 'AGENT-MASTER-ERROR');
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * 📊 Get Agent Master status
 */
app.get('/api/agents/master/status', async (req: Request, res: Response) => {
  try {
    log.api.request('GET', '/api/agents/master/status');

    const { execSync } = require('child_process');

    let isRunning = false;
    let pid = null;

    try {
      if (process.platform === 'win32') {
        const result = execSync(`powershell "Get-Process | Where-Object {$_.ProcessName -like '*python*' -and $_.CommandLine -like '*master_agent*'} | Select-Object -First 1 -ExpandProperty Id"`, {
          encoding: 'utf8',
          stdio: ['pipe', 'pipe', 'pipe']
        });
        if (result.trim()) {
          isRunning = true;
          pid = parseInt(result.trim());
        }
      } else {
        const result = execSync(`pgrep -f master_agent.py`, {
          encoding: 'utf8',
          stdio: ['pipe', 'pipe', 'pipe']
        });
        if (result.trim()) {
          isRunning = true;
          pid = parseInt(result.trim().split('\n')[0]);
        }
      }
    } catch (error) {
      // Process not found - not running
      isRunning = false;
    }

    // Check if dashboard data exists
    const dashboardFile = path.join(__dirname, '../backend/dashboard_data.json');
    const hasDashboardData = fs.existsSync(dashboardFile);

    if (hasDashboardData) {
      const dashboardData = JSON.parse(fs.readFileSync(dashboardFile, 'utf8'));
      const lastUpdate = dashboardData.timestamp || null;

      res.json({
        success: true,
        status: isRunning ? 'RUNNING' : 'STOPPED',
        pid: pid,
        has_dashboard_data: hasDashboardData,
        last_update: lastUpdate,
        system_status: dashboardData.system_status || 'UNKNOWN',
        current_cycle: dashboardData.current_cycle || null,
        timestamp: new Date().toISOString()
      });
    } else {
      res.json({
        success: true,
        status: isRunning ? 'RUNNING' : 'STOPPED',
        pid: pid,
        has_dashboard_data: false,
        message: 'Agent Master may be starting up...',
        timestamp: new Date().toISOString()
      });
    }

  } catch (error: any) {
    log.error(`Failed to get Agent Master status: ${error.message}`, 'AGENT-MASTER-STATUS-ERROR');
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * 🧪 Backtest validation endpoint
 */
app.get('/api/backtests/validate', async (req: Request, res: Response) => {
  try {
    log.api.request('GET', '/api/backtests/validate');
    log.perf.start('BACKTEST_VALIDATION');

    // Execute real-time backtester
    const backtesterScript = path.join(__dirname, '../src/data/realtime_backtester.py');
    const env = { ...process.env, PYTHONPATH: path.join(__dirname, '..') };

    const backtesterProcess = spawn('python', [backtesterScript], {
      cwd: path.join(__dirname, '..'),
      stdio: ['pipe', 'pipe', 'pipe'],
      env: env
    });

    let output = '';
    let error = '';

    backtesterProcess.stdout?.on('data', (data: Buffer) => {
      output += data.toString();
      log.info(`[BACKTESTER] ${data.toString().trim()}`, 'BACKTESTER');
    });

    backtesterProcess.stderr?.on('data', (data: Buffer) => {
      error += data.toString();
      log.error(`[BACKTESTER ERROR] ${data.toString().trim()}`, 'BACKTESTER-ERROR');
    });

    backtesterProcess.on('close', (code: number | null) => {
      if (code === 0) {
        log.success('Backtest validation completed', 'BACKTESTER');
      } else {
        log.error(`Backtest validation failed with code ${code}`, 'BACKTESTER-ERROR');
      }
    });

    // Wait for completion (with timeout)
    await new Promise((resolve, reject) => {
      backtesterProcess.on('close', resolve);
      setTimeout(() => reject(new Error('Backtest validation timeout')), 30000);
    });

    log.perf.end('BACKTEST_VALIDATION');
    log.api.response('/api/backtests/validate', 200);

    res.json({
      success: true,
      message: 'Backtest validation completed',
      output: output,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    log.perf.end('BACKTEST_VALIDATION');
    log.error(`Backtest validation error: ${error.message}`, 'BACKTEST-VALIDATION-ERROR');
    log.api.error('/api/backtests/validate', error.message);
    log.api.response('/api/backtests/validate', 500);

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// ============================================================================
// START SERVER
// ============================================================================

async function startServer(): Promise<void> {
  try {
    // Initialize HyperLiquid connections
    await initializeHyperLiquid();
    initializeHyperLiquidWS();

    // Start HTTP server
    app.listen(PORT, () => {
      console.log('\n' + '='.repeat(80));
      console.log(`${colors.green}🚀 NOVAQUOTE BACKEND SERVER STARTED${colors.reset}`);
      console.log('='.repeat(80));
      console.log(`${colors.cyan}📡 HTTP Server:${colors.reset} http://localhost:${PORT}`);
      console.log(`${colors.cyan}🔌 WebSocket Server:${colors.reset} ws://localhost:${WS_PORT}`);
      console.log(`${colors.cyan}🔗 Health Check:${colors.reset} http://localhost:${PORT}/api/health`);
      console.log('='.repeat(80) + '\n');

      log.success(`Backend server started on port ${PORT}`);
      log.success(`WebSocket server started on port ${WS_PORT}`);
    });

  } catch (error: any) {
    log.error(`Failed to start server: ${error.message}`);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', () => {
  log.warn('Received SIGINT, shutting down gracefully...');

  if (hlWS) {
    hlWS.disconnect();
  }

  wss.close(() => {
    log.success('WebSocket server closed');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  log.warn('Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error: Error) => {
  log.error(`Uncaught Exception: ${error.message}`);
  console.error(error.stack);
  process.exit(1);
});

process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
  log.error(`Unhandled Rejection: ${reason}`);
  console.error('Promise:', promise);
  process.exit(1);
});

// Start the server
startServer();