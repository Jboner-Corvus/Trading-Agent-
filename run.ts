#!/usr/bin/env node
/**
 * 🚀 NOVAQUOTE HYPERLIQUID TRADING SYSTEM - Launcher v8.0
 * Specialized for HyperLiquid Perpetuals Trading Only
 *
 * Architecture:
 * - Backend: Node.js + Express + WebSocket (port 7000)
 * - Frontend: Node.js + Static Files + Proxy (port 9001)
 * - Focus: HyperLiquid trading with AI agents
 * - WebSocket: Real-time market data integration
 */

import { spawn, ChildProcess, execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { createServer as createNetServer, Server as NetServer } from 'net';
import { request as httpRequest } from 'http';

// Types
interface HyperLiquidConfig {
  exchange: string;
  symbols: string[];
  leverage: number;
  maxLeverage: number;
}

interface ServerConfig {
  name: string;
  description: string;
  file: string;
  port: number;
}

interface Architecture {
  backend: ServerConfig;
  frontend: ServerConfig;
}

interface Logger {
  info: (msg: string) => void;
  success: (msg: string) => void;
  error: (msg: string) => void;
  warn: (msg: string) => void;
  debug?: (msg: string) => void;
}

interface Colors {
  green: string;
  yellow: string;
  red: string;
  blue: string;
  cyan: string;
  magenta: string;
  reset: string;
  bright: string;
}

interface ServerProcess {
  config: ServerConfig;
  process: ChildProcess | undefined;
}

interface DiagnosticResult {
  issues: string[];
  warnings: string[];
}

// Configuration HyperLiquid Trading System
const HYPERLIQUID_CONFIG: HyperLiquidConfig = {
  exchange: 'HyperLiquid',
  symbols: ['BTC', 'ETH', 'SOL', 'ARB', 'APT', 'ADA', 'AVAX', 'BNB'],
  leverage: 5,
  maxLeverage: 50,
};

const ARCHITECTURE: Architecture = {
  backend: {
    name: 'HyperLiquid Backend',
    description: 'API + WebSocket + Trading Logic',
    file: 'backend/server-backend.ts',
    port: 7000,
  },
  frontend: {
    name: 'Trading Dashboard',
    description: 'HyperLiquid Trading Interface',
    file: 'frontend/server-frontend.ts',
    port: 9001,
  },
};

// Logger avec Winston si disponible
let winston: any = null;
try {
  winston = require('./src/logger');
} catch (error) {
  console.log('[INFO] Winston not available, using console logger');
  winston = null;
}

const logger: Logger = {
  info: (msg: string) => {
    if (winston && winston.loggers && winston.loggers.main) {
      winston.loggers.main.info(msg);
    } else {
      console.log(`[INFO] ${msg}`);
    }
  },
  success: (msg: string) => {
    if (winston && winston.loggingHelpers && winston.loggers && winston.loggers.main) {
      winston.loggingHelpers.success(winston.loggers.main, msg);
    } else {
      console.log(`[SUCCESS] ${msg}`);
    }
  },
  error: (msg: string) => {
    if (winston && winston.loggers && winston.loggers.main) {
      winston.loggers.main.error(msg);
    } else {
      console.log(`[ERROR] ${msg}`);
    }
  },
  warn: (msg: string) => {
    if (winston && winston.loggers && winston.loggers.main) {
      winston.loggers.main.warn(msg);
    } else {
      console.log(`[WARN] ${msg}`);
    }
  },
  debug: (msg: string) => {
    if (winston && winston.loggers && winston.loggers.main) {
      winston.loggers.main.debug(msg);
    } else {
      console.log(`[DEBUG] ${msg}`);
    }
  },
};

// Couleurs pour console (fallback si Winston indisponible)
const colors: Colors = {
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
  reset: '\x1b[0m',
  bright: '\x1b[1m',
};

function colorPrint(color: keyof Colors, text: string): void {
  console.log(`${colors[color]}${text}${colors.reset}`);
}

// Arguments parsing
const args: string[] = process.argv.slice(2);
const action: string = args[0] || 'start';
const verbose: boolean = args.includes('--verbose') || args.includes('-v');
const debug: boolean = args.includes('--debug') || args.includes('-d');

// Affichage aide
if (args.includes('--help') || args.includes('-h')) {
  showHelp();
  process.exit(0);
}

if (args.includes('--version')) {
  console.log('🚀 NOVAQUOTE HyperLiquid Launcher v8.0');
  console.log('Focus: HyperLiquid Perpetuals Trading');
  process.exit(0);
}

if (action === 'test' || args.includes('--test')) {
  console.log('🧪 Running HyperLiquid System Test...');
  try {
    spawn('node', ['test-system.js'], {
      stdio: 'inherit',
      cwd: process.cwd()
    });
    process.exit(0);
  } catch (error: any) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Diagnostic spécialisé HyperLiquid
async function systemDiagnostic(): Promise<void> {
  logger.info('🔍 Running HyperLiquid system diagnostic...');

  const diagnostic: DiagnosticResult = {
    issues: [],
    warnings: []
  };

  // 1. Vérifier les fichiers serveur
  logger.info('📁 Checking HyperLiquid server files...');
  if (fs.existsSync(ARCHITECTURE.backend.file)) {
    logger.success(`✅ Found: ${ARCHITECTURE.backend.file}`);
  } else {
    diagnostic.issues.push(`❌ Missing: ${ARCHITECTURE.backend.file}`);
  }

  if (fs.existsSync(ARCHITECTURE.frontend.file)) {
    logger.success(`✅ Found: ${ARCHITECTURE.frontend.file}`);
  } else {
    diagnostic.issues.push(`❌ Missing: ${ARCHITECTURE.frontend.file}`);
  }

  // 2. Vérifier les dépendances Node.js pour HyperLiquid
  logger.info('📦 Checking HyperLiquid dependencies...');
  try {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    const requiredDeps = ['express', 'ws', 'cors', 'winston', 'axios'];

    for (const dep of requiredDeps) {
      if (packageJson.dependencies && packageJson.dependencies[dep]) {
        logger.success(`✅ ${dep} found`);
      } else {
        diagnostic.warnings.push(`⚠️  Missing ${dep}`);
      }
    }
  } catch (error) {
    diagnostic.issues.push('❌ Could not read package.json');
  }

  // 3. Vérifier le répertoire de logs
  logger.info('📝 Checking logs directory...');
  if (fs.existsSync('logs')) {
    logger.success('✅ Logs directory exists');
  } else {
    diagnostic.warnings.push('⚠️  Logs directory missing - will be created automatically');
  }

  // 4. Vérifier les ports (async pour éviter les blocages)
  logger.info('🌐 Checking port availability...');
  const ports = [ARCHITECTURE.backend.port, ARCHITECTURE.frontend.port];
  for (const port of ports) {
    try {
      const portCheck = new Promise<boolean>((resolve) => {
        const server: NetServer = createNetServer();

        server.listen(port, () => {
          server.close(() => {
            logger.success(`✅ Port ${port} is available`);
            resolve(true);
          });
        });

        server.on('error', () => {
          diagnostic.issues.push(`❌ Port ${port} is already in use`);
          resolve(false);
        });

        // Timeout pour éviter le blocage
        setTimeout(() => {
          server.close();
          resolve(false);
        }, 1000);
      });

      await portCheck;
    } catch (error: any) {
      diagnostic.issues.push(`❌ Could not check port ${port}: ${error.message}`);
    }
  }

  // 5. Vérifier les fichiers frontend
  logger.info('🌍 Checking frontend files...');
  const frontendFiles = [
    'frontend/public/index.html',
    'frontend/public/backtest.html',
    'frontend/public/config.html'
  ];

  for (const file of frontendFiles) {
    if (fs.existsSync(file)) {
      logger.success(`✅ Found: ${file}`);
    } else {
      diagnostic.warnings.push(`⚠️  Missing frontend file: ${file}`);
    }
  }

  // 6. Vérifier Python et les agents HyperLiquid
  logger.info('🐍 Checking Python AI agents...');
  try {
    const pythonVersion = execSync('python --version 2>&1', { encoding: 'utf8' }).trim();
    logger.success(`✅ Python: ${pythonVersion}`);

    // Vérifier les agents HyperLiquid
    const hyperliquidAgents = [
      'src/algorithms/hyperliquid_agent.py',
      'src/algorithms/hyperliquid_mainnet_agent.py',
      'src/algorithms/risk_agent.py',
      'src/algorithms/funding_agent.py'
    ];

    let agentsFound = 0;
    for (const agent of hyperliquidAgents) {
      if (fs.existsSync(agent)) {
        agentsFound++;
        logger.success(`✅ Found: ${path.basename(agent)}`);
      } else {
        diagnostic.warnings.push(`⚠️  Missing agent: ${agent}`);
      }
    }

    logger.info(`🤖 ${agentsFound}/${hyperliquidAgents.length} AI agents found`);
  } catch (error) {
    diagnostic.warnings.push('⚠️  Python not found - AI agents unavailable');
  }

  // 7. Résumé du diagnostic HyperLiquid
  console.log('\n' + '='.repeat(70));
  colorPrint('cyan', '🚀 HYPERLIQUID TRADING SYSTEM DIAGNOSTIC');
  console.log('='.repeat(70));

  if (diagnostic.issues.length === 0 && diagnostic.warnings.length === 0) {
    colorPrint('green', '🎉 HYPERLIQUID SYSTEM: ALL CHECKS PASSED');
    console.log(`✅ Ready to trade on ${HYPERLIQUID_CONFIG.symbols.length} symbols`);
  } else {
    if (diagnostic.issues.length > 0) {
      colorPrint('red', '🚨 CRITICAL ISSUES:');
      diagnostic.issues.forEach(issue => console.log(`  ${issue}`));
    }

    if (diagnostic.warnings.length > 0) {
      colorPrint('yellow', '⚠️  WARNINGS:');
      diagnostic.warnings.forEach(warning => console.log(`  ${warning}`));
    }
  }
  console.log('='.repeat(70) + '\n');

  // Arrêter si des problèmes critiques
  if (diagnostic.issues.length > 0) {
    logger.error('❌ HyperLiquid system diagnostic failed - cannot start');
    process.exit(1);
  }
}

// Vérifier les fichiers (fonction conservée pour compatibilité)
async function checkFiles(): Promise<void> {
  await systemDiagnostic();
}

// Nettoyer les processus sur les ports
async function cleanupPorts(): Promise<void> {
  const ports = [ARCHITECTURE.backend.port, ARCHITECTURE.frontend.port];

  logger.info('Cleaning up ports...');

  for (const port of ports) {
    try {
      // Tenter avec netstat (Windows/Linux compatible)
      try {
        const cmd = process.platform === 'win32'
          ? `powershell "Get-NetTCPConnection -LocalPort ${port} -ErrorAction SilentlyContinue | Select-Object OwningProcess"`
          : `netstat -tlnp | grep :${port}`;

        const output = execSync(cmd, { encoding: 'utf8', stdio: 'pipe' });

        if (process.platform === 'win32') {
          const lines = output.split('\n').slice(3); // Skip headers
          for (const line of lines) {
            if (line.trim()) {
              const match = line.trim().match(/\d+/);
              if (match) {
                const pid = parseInt(match[0]);
                if (pid > 0) {
                  try {
                    execSync(`powershell "Stop-Process -Id ${pid} -Force -ErrorAction SilentlyContinue"`, { stdio: 'ignore' });
                    logger.success(`Killed process ${pid} on port ${port}`);
                  } catch (killError: any) {
                    logger.warn(`Could not kill process ${pid}: ${killError.message}`);
                  }
                }
              }
            }
          }
        } else {
          // Linux/Unix handling
          const lines = output.split('\n');
          for (const line of lines) {
            const match = line.match(/:(\d+)\s+.*?(\d+)\//);
            if (match && parseInt(match[1]) === port) {
              const pid = parseInt(match[2]);
              if (pid > 0) {
                try {
                  execSync(`kill -9 ${pid}`, { stdio: 'ignore' });
                  logger.success(`Killed process ${pid} on port ${port}`);
                } catch (killError: any) {
                  logger.warn(`Could not kill process ${pid}: ${killError.message}`);
                }
              }
            }
          }
        }
      } catch (error) {
        // Port libre ou commande non disponible
        logger.debug?.(`Port ${port} appears to be free`);
      }
    } catch (error: any) {
      logger.warn(`Error cleaning port ${port}: ${error.message}`);
    }
  }

  await new Promise(resolve => setTimeout(resolve, 2000));
}

// Démarrer un serveur
function startServer(serverConfig: ServerConfig & { type: string }): Promise<ChildProcess | undefined> {
  return new Promise((resolve, reject) => {
    const logPrefix = `[${serverConfig.type.toUpperCase()}]`;
    logger.info(`${logPrefix} Starting ${serverConfig.file}...`);

    // Vérifier si le fichier existe
    if (!fs.existsSync(serverConfig.file)) {
      const error = new Error(`Server file not found: ${serverConfig.file}`);
      logger.error(`${logPrefix} ${error.message}`);
      reject(error);
      return;
    }

    // Déterminer si c'est un fichier TypeScript
    const isTypeScript = serverConfig.file.endsWith('.ts');
    const command = isTypeScript ? 'ts-node' : 'node';

    const proc = spawn(command, [serverConfig.file], {
      stdio: verbose ? 'inherit' : ['pipe', 'pipe', 'pipe'],
      detached: false,
      env: { ...process.env, NODE_ENV: 'development' },
      shell: process.platform === 'win32' // Utiliser shell sur Windows
    });

    // Gérer stdout
    if (proc.stdout) {
      proc.stdout.on('data', (data: Buffer) => {
        const output = data.toString().trim();
        if (output) {
          if (verbose || debug) {
            console.log(`${logPrefix} ${output}`);
          }
          logger.info(`${logPrefix} ${output}`);
        }
      });
    }

    // Gérer stderr
    if (proc.stderr) {
      proc.stderr.on('data', (data: Buffer) => {
        const output = data.toString().trim();
        if (output) {
          if (verbose || debug || output.includes('Error') || output.includes('error') || output.includes('Error:')) {
            console.log(`${logPrefix} ERROR: ${output}`);
          }
          logger.error(`${logPrefix} ${output}`);
        }
      });
    }

    proc.on('error', (error: Error) => {
      logger.error(`${logPrefix} Failed to start: ${error.message}`);
      reject(error);
    });

    proc.on('exit', (code: number | null, signal: string | null) => {
      if (signal) {
        logger.warn(`${logPrefix} Process killed with signal ${signal}`);
      } else {
        logger.warn(`${logPrefix} Process exited with code ${code}`);
      }
      resolve(undefined);
    });

    // Timeout plus long pour donner le temps au serveur de démarrer
    setTimeout(() => {
      if (!proc.killed) {
        logger.success(`${logPrefix} Process started successfully (PID: ${proc.pid})`);
        resolve(proc);
      }
    }, 5000);
  });
}

// Afficher le message de bienvenue spécialisé HyperLiquid
function showWelcome(): void {
  console.log('\n' + '='.repeat(80));
  colorPrint('bright', '🚀 NOVAQUOTE HYPERLIQUID TRADING SYSTEM v8.0');
  console.log('='.repeat(80));

  console.log(`\n${colors.cyan}🎯 TRADING FOCUS: ${colors.reset}`);
  colorPrint('green', `  ✓ HyperLiquid Perpetuals Trading`);
  console.log(`  • ${HYPERLIQUID_CONFIG.symbols.length} supported symbols`);
  console.log(`  • Up to ${HYPERLIQUID_CONFIG.maxLeverage}x leverage`);
  console.log(`  • AI-powered trading agents`);

  console.log(`\n${colors.cyan}🌐 ARCHITECTURE:${colors.reset}`);
  colorPrint(
    'blue',
    `  • Backend (Port ${ARCHITECTURE.backend.port}) - Trading API + WebSocket`
  );
  colorPrint(
    'blue',
    `  • Frontend (Port ${ARCHITECTURE.frontend.port}) - Trading Dashboard`
  );

  console.log(`\n${colors.cyan}📊 SYMBOLS:${colors.reset}`);
  console.log(`  • ${HYPERLIQUID_CONFIG.symbols.join(', ')} (Perpetuals)`);
  console.log(`  • Default leverage: ${HYPERLIQUID_CONFIG.leverage}x`);

  console.log(`\n${colors.cyan}📄 PAGES:${colors.reset}`);
  console.log(
    `  • ${colors.blue}http://localhost:${ARCHITECTURE.frontend.port}/${colors.reset} (Trading Dashboard)`
  );
  console.log(
    `  • ${colors.blue}http://localhost:${ARCHITECTURE.frontend.port}/backtest.html${colors.reset} (Strategy Backtests)`
  );
  console.log(
    `  • ${colors.blue}http://localhost:${ARCHITECTURE.frontend.port}/config.html${colors.reset} (Trading Config)`
  );
  console.log(
    `  • ${colors.blue}http://localhost:${ARCHITECTURE.backend.port}/api/health${colors.reset} (System Status)`
  );

  console.log(`\n${colors.cyan}🤖 AI AGENTS:${colors.reset}`);
  console.log(`  • Risk Agent - Position management`);
  console.log(`  • Funding Agent - Rate arbitrage`);
  console.log(`  • Strategy Agent - Technical signals`);
  console.log(`  • HyperLiquid Agent - Trading execution`);

  console.log(`\n${colors.cyan}🔧 OPTIONS:${colors.reset}`);
  console.log(`  • ${colors.yellow}--verbose${colors.reset} - Detailed logs`);
  console.log(`  • ${colors.yellow}--debug${colors.reset} - Debug mode`);

  console.log('\n' + '='.repeat(80) + '\n');
}

// Fonction principale
async function main(): Promise<void> {
  try {
    if (action === 'stop') {
      logger.info('🛑 Stopping HyperLiquid Trading System...');
      await cleanupPorts();
      logger.success('✅ System stopped successfully');
      process.exit(0);
    }

    if (action === 'restart') {
      logger.info('🔄 Restarting HyperLiquid Trading System...');
      await cleanupPorts();
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Vérifier l'architecture
    showWelcome();

    // Créer les répertoires nécessaires
    ensureDirectories();

    // Diagnostic complet du système
    await checkFiles();

    // Nettoyer les ports
    await cleanupPorts();

    // Démarrer les serveurs HyperLiquid
    logger.info('🚀 Starting HyperLiquid Trading System...');
    const servers: ServerProcess[] = [];

    // Démarrer Backend (Trading APIs + WebSocket)
    try {
      const backendProcess = await startServer({
        ...ARCHITECTURE.backend,
        type: 'backend',
      });
      servers.push({
        config: ARCHITECTURE.backend,
        process: backendProcess,
      });
      logger.success(`✅ HyperLiquid Backend started successfully`);
    } catch (error) {
      logger.error(`❌ Failed to start ${ARCHITECTURE.backend.file}`);
      throw error;
    }

    // Attendre que le backend démarre
    logger.info('Waiting for backend to start...');
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Vérifier que le backend est bien démarré
    try {
      const options = {
        hostname: 'localhost',
        port: ARCHITECTURE.backend.port,
        path: '/api/health',
        method: 'GET',
        timeout: 2000
      };

      const healthCheck = (): Promise<void> => {
        return new Promise((checkResolve, checkReject) => {
          const req = httpRequest(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
              if (res.statusCode === 200) {
                logger.success('✅ Backend health check passed');
                checkResolve(undefined);
              } else {
                checkReject(new Error(`Backend returned status ${res.statusCode}`));
              }
            });
          });

          req.on('error', checkReject);
          req.on('timeout', () => {
            req.destroy();
            checkReject(new Error('Backend health check timeout'));
          });

          req.end();
        });
      };

      // Tenter le health check avec retries
      let backendHealthy = false;
      for (let i = 0; i < 5; i++) {
        try {
          await healthCheck();
          backendHealthy = true;
          break;
        } catch (error: any) {
          logger.warn(`Backend health check attempt ${i + 1}/5 failed: ${error.message}`);
          if (i < 4) {
            await new Promise(resolve => setTimeout(resolve, 2000));
          }
        }
      }

      if (!backendHealthy) {
        logger.warn('Backend health check failed, but continuing with frontend startup...');
      }
    } catch (error: any) {
      logger.warn(`Could not verify backend health: ${error.message}`);
    }

    // Démarrer Frontend (Trading Dashboard)
    try {
      const frontendProcess = await startServer({
        ...ARCHITECTURE.frontend,
        type: 'frontend',
      });
      servers.push({
        config: ARCHITECTURE.frontend,
        process: frontendProcess,
      });
      logger.success(`✅ Trading Dashboard started successfully`);
    } catch (error) {
      logger.error(`❌ Failed to start ${ARCHITECTURE.frontend.file}`);
      throw error;
    }

    // Message de succès HyperLiquid
    console.log('\n' + '='.repeat(80));
    colorPrint('bright', '🎉 HYPERLIQUID TRADING SYSTEM STARTED!');
    console.log('='.repeat(80));

    colorPrint('green', '\n✅ ALL SERVICES RUNNING:');
    for (const server of servers) {
      colorPrint('cyan', `  • ${server.config.name} (PID: ${server.process?.pid || 'unknown'})`);
    }

    colorPrint('green', '\n🌐 TRADING INTERFACE:');
    console.log(
      `  • Dashboard:     ${colors.blue}http://localhost:${ARCHITECTURE.frontend.port}/${colors.reset}`
    );
    console.log(
      `  • Backtests:     ${colors.blue}http://localhost:${ARCHITECTURE.frontend.port}/backtest.html${colors.reset}`
    );
    console.log(
      `  • Config:        ${colors.blue}http://localhost:${ARCHITECTURE.frontend.port}/config.html${colors.reset}`
    );
    console.log(
      `  • System Status: ${colors.cyan}http://localhost:${ARCHITECTURE.backend.port}/api/health${colors.reset}`
    );

    colorPrint('magenta', '\n🚀 HYPERLIQUID READY:');
    console.log(`  • Exchange: ${HYPERLIQUID_CONFIG.exchange}`);
    console.log(`  • Symbols:  ${HYPERLIQUID_CONFIG.symbols.join(', ')}`);
    console.log(`  • Leverage: Up to ${HYPERLIQUID_CONFIG.maxLeverage}x`);
    console.log(`  • WebSocket: ws://localhost:7001`);

    console.log(`\n${colors.yellow}💡 TRADING TIPS:${colors.reset}`);
    console.log(`  • ${colors.red}Ctrl+C${colors.reset} to stop all services`);
    console.log(`  • ${colors.yellow}--verbose${colors.reset} for detailed trading logs`);
    console.log(`  • Configure API keys in .env file`);
    console.log(`  • Start with paper trading mode`);

    console.log('\n' + '='.repeat(80) + '\n');

    // Attendre les processus
    process.on('SIGINT', async () => {
      console.log('\n\n🛑 Shutdown requested...');
      logger.info('🔄 Stopping HyperLiquid Trading System...');

      for (const server of servers) {
        if (server.process && !server.process.killed) {
          try {
            logger.info(`Stopping ${server.config.name} (PID: ${server.process.pid})...`);

            // Tenter d'arrêter gracieusement
            if (process.platform === 'win32') {
              // Sur Windows, utiliser taskkill
              execSync(`taskkill /PID ${server.process.pid} /F`, { stdio: 'ignore' });
            } else {
              // Sur Unix-like, envoyer SIGTERM puis SIGKILL si nécessaire
              server.process.kill('SIGTERM');

              // Attendre un peu
              await new Promise(resolve => setTimeout(resolve, 2000));

              if (!server.process.killed) {
                server.process.kill('SIGKILL');
              }
            }

            logger.success(`✅ Stopped ${server.config.name}`);
          } catch (error: any) {
            logger.warn(`Error stopping ${server.config.name}: ${error.message}`);
          }
        }
      }

      // Nettoyer les ports une dernière fois
      try {
        await cleanupPorts();
      } catch (error: any) {
        logger.warn(`Error during final cleanup: ${error.message}`);
      }

      console.log('\n👋 Thanks for using NOVAQUOTE HyperLiquid Trading!');
      console.log('='.repeat(80) + '\n');
      process.exit(0);
    });

    process.on('SIGTERM', async () => {
      logger.info('Received SIGTERM, shutting down...');

      for (const server of servers) {
        if (server.process && !server.process.killed) {
          try {
            server.process.kill('SIGTERM');
            logger.success(`✅ Stopped ${server.config.file}`);
          } catch (error: any) {
            logger.warn(`Error stopping ${server.config.file}: ${error.message}`);
          }
        }
      }

      process.exit(0);
    });

    // Gérer les erreurs non capturées
    process.on('uncaughtException', (error: Error) => {
      logger.error(`Uncaught Exception: ${error.message}`);
      if (verbose || debug) {
        console.error(error.stack);
      }
      process.exit(1);
    });

    process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
      logger.error(`Unhandled Rejection: ${reason}`);
      if (verbose || debug) {
        console.error('Promise:', promise);
      }
      process.exit(1);
    });
  } catch (error: any) {
    logger.error(`💥 Fatal error: ${error.message}`);
    if (verbose || debug) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

function showHelp(): void {
  console.log(`
${colors.bright}🚀 NOVAQUOTE HYPERLIQUID TRADING SYSTEM - LAUNCHER v8.0${colors.reset}

${colors.cyan}DESCRIPTION:${colors.reset}
  Specialized HyperLiquid Perpetuals Trading System
  AI-powered trading agents with real-time risk management

${colors.cyan}USAGE:${colors.reset}
  ts-node run.ts [action] [options]

${colors.cyan}ACTIONS:${colors.reset}
  start                    Start HyperLiquid trading system
  stop                     Stop all trading services
  restart                  Restart the system
  test                     Run system diagnostics

${colors.cyan}OPTIONS:${colors.reset}
  -h, --help              Show this help message
  -v, --verbose           Enable detailed trading logs
  -d, --debug             Enable debug mode
  --version               Show version and exit
  --test                  Run system test

${colors.cyan}HYPERLIQUID FEATURES:${colors.reset}
  • Trading: BTC, ETH, SOL, ARB, APT, ADA, AVAX, BNB
  • Leverage: Up to 50x (default 5x)
  • AI Agents: Risk Management, Strategy, Funding Arbitrage
  • Real-time: WebSocket market data integration

${colors.cyan}REQUIREMENTS:${colors.reset}
  • HYPER_LIQUID_KEY (Ethereum private key)
  • ANTHROPIC_KEY (AI risk management)
  • Optional: OPENAI_KEY, DEEPSEEK_KEY

${colors.cyan}EXAMPLES:${colors.reset}
  ts-node run.ts start                    # Start trading system
  ts-node run.ts start --verbose          # Start with detailed logs
  ts-node run.ts test                     # Run diagnostics
  ts-node run.ts stop                     # Stop all services
  ts-node run.ts restart                  # Restart system

${colors.cyan}TRADING INTERFACE:${colors.reset}
  Frontend (Port 9001):
    • Dashboard:  http://localhost:9001/
    • Backtests:  http://localhost:9001/backtest.html
    • Config:     http://localhost:9001/config.html

  Backend (Port 7000):
    • API:        http://localhost:7000/api/health
    • WebSocket:  ws://localhost:7001

${colors.cyan}SAFETY TIPS:${colors.reset}
  • Always start with paper trading mode
  • Use small position sizes initially
  • Monitor AI agent recommendations
  • Keep API keys secure and rotate regularly
`);
}

// Créer les répertoires nécessaires au démarrage
function ensureDirectories(): void {
  const directories = ['logs', 'logs/archive'];

  for (const dir of directories) {
    if (!fs.existsSync(dir)) {
      try {
        fs.mkdirSync(dir, { recursive: true });
        logger.success(`✅ Created directory: ${dir}`);
      } catch (error: any) {
        logger.warn(`⚠️  Could not create directory ${dir}: ${error.message}`);
      }
    }
  }
}

// Lancer l'application
main();