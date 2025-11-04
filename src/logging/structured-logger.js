/**
 * 📊 Logs Structurés Avancés
 * Système de logging avec Winston, rotation de fichiers et formatage JSON
 */

const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

class StructuredLogger {
    constructor() {
        this.logger = this.createLogger();
        this.context = {};
    }

    /**
     * 🏭 Obtenir l'instance singleton du logger
     */
    static getInstance() {
        if (!StructuredLogger.instance) {
            StructuredLogger.instance = new StructuredLogger();
        }
        return StructuredLogger.instance;
    }

    /**
     * 🔧 Créer le logger Winston avec configuration complète
     */
    createLogger() {
        const logFormat = winston.format.combine(
            winston.format.timestamp(),
            winston.format.errors({ stack: true }),
            winston.format.json(),
            winston.format.printf(({ timestamp, level, message, ...meta }) => {
                const logEntry = {
                    timestamp,
                    level,
                    message,
                    ...meta
                };

                // Ajouter le contexte global
                if (Object.keys(this.context).length > 0) {
                    logEntry.context = { ...this.context, ...logEntry.context };
                }

                return JSON.stringify(logEntry);
            })
        );

        // Formater pour la console en développement
        const consoleFormat = winston.format.combine(
            winston.format.colorize(),
            winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
            winston.format.printf(({ timestamp, level, message, ...meta }) => {
                let msg = `${timestamp} [${level}]: ${message}`;

                if (Object.keys(meta).length > 0) {
                    msg += ` ${JSON.stringify(meta)}`;
                }

                return msg;
            })
        );

        // Transports de base
        const transports = [
            // Console pour développement
            new winston.transports.Console({
                level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
                format: process.env.NODE_ENV === 'production' ? logFormat : consoleFormat
            }),

            // Fichiers de logs avec rotation quotidienne
            new DailyRotateFile({
                filename: 'logs/application-%DATE%.log',
                datePattern: 'YYYY-MM-DD',
                maxSize: '50m',
                maxFiles: '30d',
                level: 'info',
                format: logFormat
            }),

            // Fichier d'erreurs séparé
            new DailyRotateFile({
                filename: 'logs/errors-%DATE%.log',
                datePattern: 'YYYY-MM-DD',
                maxSize: '20m',
                maxFiles: '30d',
                level: 'error',
                format: logFormat
            }),

            // Fichier de logs de trading
            new DailyRotateFile({
                filename: 'logs/trading-%DATE%.log',
                datePattern: 'YYYY-MM-DD',
                maxSize: '30m',
                maxFiles: '90d',
                level: 'info',
                format: logFormat,
                filter: (info) => {
                    return info.business?.symbol || info.component === 'trading';
                }
            }),

            // Fichier de logs de sécurité
            new DailyRotateFile({
                filename: 'logs/security-%DATE%.log',
                datePattern: 'YYYY-MM-DD',
                maxSize: '20m',
                maxFiles: '365d',
                level: 'warn',
                format: logFormat,
                filter: (info) => {
                    return info.security || info.component === 'security';
                }
            }),

            // Fichier de logs de performance
            new DailyRotateFile({
                filename: 'logs/performance-%DATE%.log',
                datePattern: 'YYYY-MM-DD',
                maxSize: '20m',
                maxFiles: '30d',
                level: 'info',
                format: logFormat,
                filter: (info) => {
                    return info.performance || info.component === 'performance';
                }
            })
        ];

        // Ajouter le transport pour les logs d'audit en production
        if (process.env.NODE_ENV === 'production') {
            transports.push(
                new DailyRotateFile({
                    filename: 'logs/audit-%DATE%.log',
                    datePattern: 'YYYY-MM-DD',
                    maxSize: '50m',
                    maxFiles: '2555d', // 7 ans de rétention pour l'audit
                    level: 'info',
                    format: logFormat,
                    filter: (info) => {
                        return info.audit || ['trading', 'auth', 'admin'].includes(info.component || '');
                    }
                })
            );
        }

        return winston.createLogger({
            level: process.env.LOG_LEVEL || 'info',
            format: logFormat,
            transports,
            // Gérer les exceptions non capturées
            exceptionHandlers: [
                new DailyRotateFile({
                    filename: 'logs/exceptions-%DATE%.log',
                    datePattern: 'YYYY-MM-DD',
                    maxSize: '20m',
                    maxFiles: '30d',
                    format: logFormat
                })
            ],
            // Gérer les rejets de promesses non capturés
            rejectionHandlers: [
                new DailyRotateFile({
                    filename: 'logs/rejections-%DATE%.log',
                    datePattern: 'YYYY-MM-DD',
                    maxSize: '20m',
                    maxFiles: '30d',
                    format: logFormat
                })
            ]
        });
    }

    /**
     * 📝 Logger un message avec contexte
     */
    log(level, message, meta = {}) {
        this.logger.log(level, message, meta);
    }

    /**
     * 🔍 Logger au niveau debug
     */
    debug(message, context = {}) {
        this.log('debug', message, { context });
    }

    /**
     * ℹ️ Logger au niveau info
     */
    info(message, context = {}) {
        this.log('info', message, { context });
    }

    /**
     * ⚠️ Logger au niveau warn
     */
    warn(message, context = {}) {
        this.log('warn', message, { context });
    }

    /**
     * ❌ Logger au niveau error
     */
    error(message, error, context = {}) {
        const meta = { context };

        if (error) {
            meta.error = {
                name: error.name,
                message: error.message,
                stack: error.stack,
                code: error.code
            };
        }

        this.log('error', message, meta);
    }

    /**
     * 📊 Logger les métriques de performance
     */
    performance(operation, duration, context = {}) {
        const memUsage = process.memoryUsage();

        this.log('info', `Performance: ${operation}`, {
            context,
            component: 'performance',
            performance: {
                duration,
                memoryUsage: memUsage.heapUsed,
                cpuUsage: process.cpuUsage().user
            }
        });
    }

    /**
     * 💰 Logger les activités de trading
     */
    trading(action, context = {}) {
        this.log('info', `Trading: ${action}`, {
            context,
            component: 'trading',
            business: {
                symbol: context.symbol,
                side: context.side,
                size: context.size,
                price: context.price,
                orderId: context.orderId,
                tradeId: context.tradeId
            },
            audit: true
        });
    }

    /**
     * 🔐 Logger les événements de sécurité
     */
    security(event, context = {}) {
        this.log('warn', `Security: ${event}`, {
            context,
            component: 'security',
            security: {
                threat: context.threat,
                source: context.source,
                blocked: context.blocked
            },
            audit: true
        });
    }

    /**
     * 🤖 Logger les activités d'agents IA
     */
    agent(agentId, action, context = {}) {
        this.log('info', `Agent ${agentId}: ${action}`, {
            context: { ...context, agentId },
            component: 'agent'
        });
    }

    /**
     * 🔌 Logger les activités WebSocket
     */
    websocket(event, context = {}) {
        this.log('info', `WebSocket: ${event}`, {
            context,
            component: 'websocket'
        });
    }

    /**
     * 🏥 Logger les health checks
     */
    health(service, status, context = {}) {
        this.log('info', `Health Check: ${service} - ${status}`, {
            context,
            component: 'health'
        });
    }

    /**
     * 📈 Logger les métriques Prometheus
     */
    metric(metric, value, context = {}) {
        this.log('debug', `Metric: ${metric} = ${value}`, {
            context,
            component: 'metrics'
        });
    }

    /**
     * 🎯 Définir le contexte global pour tous les logs suivants
     */
    setContext(context) {
        this.context = { ...this.context, ...context };
    }

    /**
     * 🧹 Nettoyer le contexte
     */
    clearContext() {
        this.context = {};
    }
}

// Export des utilitaires
const logger = StructuredLogger.getInstance();

// Export des middlewares
const requestLogger = (req, res, next) => {
    const startTime = Date.now();
    const requestId = req.headers['x-request-id'] ||
                     `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Créer un logger avec contexte de requête
    logger.setContext({
        requestId,
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        method: req.method,
        url: req.url
    });

    // Logger le début de la requête
    logger.info(`Request started: ${req.method} ${req.url}`, {
        method: req.method,
        url: req.url,
        ip: req.ip,
        userAgent: req.get('User-Agent')
    });

    // Intercepter la fin de la réponse
    res.on('finish', () => {
        const duration = Date.now() - startTime;

        logger.info(`Request completed: ${req.method} ${req.url}`, {
            method: req.method,
            url: req.url,
            statusCode: res.statusCode,
            duration,
            requestId
        });

        // Logger les performances pour les requêtes lentes
        if (duration > 1000) {
            logger.performance(`${req.method} ${req.url}`, duration, {
                method: req.method,
                url: req.url,
                statusCode: res.statusCode
            });
        }

        // Nettoyer le contexte
        logger.clearContext();
    });

    next();
};

const errorLogger = (error, req, res, next) => {
    logger.error(`Request error: ${req.method} ${req.url}`, error, {
        method: req.method,
        url: req.url,
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        statusCode: res.statusCode
    });

    next(error);
};

module.exports = {
    StructuredLogger,
    logger,
    requestLogger,
    errorLogger
};