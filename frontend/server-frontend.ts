/**
 * NOVAQUOTE FRONTEND SERVER - Architecture Séparée
 * Port 9001 - Fichiers statiques avec proxy
 * Responsable: Servir HTML, CSS, JS + Proxy API
 */

import express, { Express, Request, Response } from 'express';
import path from 'path';

// Types
interface LogFunction {
  (msg: string): void;
}

interface Logger {
  info: LogFunction;
  success: LogFunction;
  error: LogFunction;
}

const app: Express = express();
const PORT: number = 9001;

// Logger simple
const log: Logger = {
  info: (msg: string): void => console.log(`[FRONTEND] ℹ️  ${msg}`),
  success: (msg: string): void => console.log(`[FRONTEND] ✅ ${msg}`),
  error: (msg: string): void => console.log(`[FRONTEND] ❌ ${msg}`),
};

// Proxy API requests simple et direct
app.use('/api*', async (req: Request, res: Response): Promise<void> => {
  try {
    const targetUrl = `http://127.0.0.1:7000${req.originalUrl}`;
    log.info(`🔄 PROXY: ${req.method} ${req.originalUrl} → ${targetUrl}`);

    // Filtrer les headers pour éviter les problèmes
    const filteredHeaders: { [key: string]: any } = {};
    Object.keys(req.headers).forEach((key: string) => {
      if (!key.includes('append') && key !== 'host' && key !== 'connection') {
        filteredHeaders[key] = req.headers[key];
      }
    });

    // Préserver le corps de la requête
    let body: string | null = null;
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      body = JSON.stringify(req.body);
    }

    const requestOptions: any = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...filteredHeaders,
      },
    };

    if (body) {
      requestOptions.body = body;
    }

    const response = await fetch(targetUrl, requestOptions);

    const data = await response.text();
    log.info(`✅ BACKEND: ${response.status} for ${req.originalUrl}`);

    res.status(response.status);

    // Filtrer les headers de réponse aussi
    response.headers.forEach((value: string, key: string) => {
      if (!key.includes('append') && key !== 'connection') {
        res.set(key, value);
      }
    });

    // Essayer de parser en JSON si possible
    try {
      const jsonData = JSON.parse(data);
      res.json(jsonData);
    } catch {
      // Si ce n'est pas du JSON, envoyer comme texte
      res.send(data);
    }
  } catch (error: any) {
    log.error(`❌ Proxy error for ${req.originalUrl}: ${error.message}`);
    res.status(500).json({
      error: 'Proxy error',
      message: error.message,
      url: req.originalUrl,
      target: 'http://127.0.0.1:7000',
    });
  }
});

// Servir les fichiers statiques APRÈS le proxy
app.use(express.static(path.join(__dirname, 'public')));

// Redirects
app.get('/backtest', (_req: Request, res: Response): void => {
  res.redirect(301, '/backtest.html');
});

app.get('/config', (_req: Request, res: Response): void => {
  res.redirect(301, '/config.html');
});

// Page d'accueil par défaut
app.get('/', (_req: Request, res: Response): void => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/index.html', (_req: Request, res: Response): void => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/backtest.html', (_req: Request, res: Response): void => {
  res.sendFile(path.join(__dirname, 'public', 'backtest.html'));
});

app.get('/config.html', (_req: Request, res: Response): void => {
  res.sendFile(path.join(__dirname, 'public', 'config.html'));
});

// ==================== START SERVER ====================
app.listen(PORT, '127.0.0.1', (): void => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║                 🚀 NOVAQUOTE FRONTEND SERVER                 ║
║                      Architecture Séparée                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🌐 Frontend URL: http://localhost:${PORT}                                       ║
║                                                                              ║
║  📄 Pages disponibles:                                                        ║
║     • http://localhost:${PORT}/                    (Dashboard)                ║
║     • http://localhost:${PORT}/backtest.html      (Backtests)                ║
║     • http://localhost:${PORT}/config.html        (Configuration)             ║
║                                                                              ║
║  🔗 Backend API: http://localhost:7000                                     ║
║  🌊 WebSocket: ws://localhost:7000                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════╝
  `);

  log.success(`Frontend server running on http://localhost:${PORT}`);
  log.info(`Serving static files from: ${path.join(__dirname, 'public')}`);
});

// Graceful shutdown
process.on('SIGINT', (): void => {
  console.log('\n[FRONTEND] Shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', (): void => {
  console.log('\n[FRONTEND] Received SIGTERM, shutting down...');
  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error: Error): void => {
  log.error(`Uncaught Exception: ${error.message}`);
  console.error(error.stack);
  process.exit(1);
});

process.on('unhandledRejection', (reason: any, promise: Promise<any>): void => {
  log.error(`Unhandled Rejection: ${reason}`);
  console.error('Promise:', promise);
  process.exit(1);
});

export default app;