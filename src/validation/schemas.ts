/**
 * 🔒 Schemas de Validation d'Input
 * Validation stricte pour toutes les entrées utilisateur avec Joi
 */

import Joi from 'joi';

// Symptôles supportés par HyperLiquid
export const SUPPORTED_SYMBOLS = ['BTC', 'ETH', 'SOL', 'ARB', 'APT', 'ADA', 'AVAX', 'BNB'];

// Schéma de base pour les requêtes
export const baseRequestSchema = Joi.object({
  timestamp: Joi.date().optional(),
  requestId: Joi.string().uuid().optional(),
});

// Schema pour les requêtes de prix
export const priceRequestSchema = Joi.object({
  symbol: Joi.string().valid(...SUPPORTED_SYMBOLS).required(),
  interval: Joi.string().valid('1m', '5m', '15m', '1h', '4h', '1d').default('1m'),
  limit: Joi.number().integer().min(1).max(1000).default(100),
});

// Schema pour les ordres de trading
export const tradeRequestSchema = Joi.object({
  symbol: Joi.string().valid(...SUPPORTED_SYMBOLS).required(),
  side: Joi.string().valid('buy', 'sell').required(),
  size: Joi.number().positive().max(100).required()
    .messages({
      'number.positive': 'Size must be positive',
      'number.max': 'Size cannot exceed 100',
      'any.required': 'Size is required'
    }),
  price: Joi.number().positive().when('type', {
    is: 'limit',
    then: Joi.required(),
    otherwise: Joi.forbidden()
  }),
  type: Joi.string().valid('market', 'limit').default('market'),
  leverage: Joi.number().integer().min(1).max(50).default(5),
  stopLoss: Joi.number().positive().optional(),
  takeProfit: Joi.number().positive().optional(),
  timeInForce: Joi.string().valid('GTC', 'IOC', 'FOK').default('GTC'),
  reduceOnly: Joi.boolean().default(false),
});

// Schema pour la fermeture de position
export const closePositionSchema = Joi.object({
  symbol: Joi.string().valid(...SUPPORTED_SYMBOLS).required(),
  size: Joi.number().positive().max(100).optional(),
  price: Joi.number().positive().optional(),
});

// Schema pour les positions
export const positionsRequestSchema = Joi.object({
  symbol: Joi.string().valid(...SUPPORTED_SYMBOLS).optional(),
  showPnl: Joi.boolean().default(true),
});

// Schema pour les bougies (candles)
export const candlesRequestSchema = Joi.object({
  symbol: Joi.string().valid(...SUPPORTED_SYMBOLS).required(),
  interval: Joi.string().valid('1m', '5m', '15m', '1h', '4h', '1d').required(),
  limit: Joi.number().integer().min(1).max(1000).default(500),
  startTime: Joi.date().optional(),
  endTime: Joi.date().optional(),
});

// Schema pour les agents
export const agentControlSchema = Joi.object({
  agentId: Joi.string().valid(
    'risk_agent',
    'strategy_agent',
    'funding_agent',
    'sentiment_analysis_agent'
  ).required(),
  action: Joi.string().valid('start', 'stop', 'restart', 'status').required(),
  config: Joi.object().optional(),
});

// Schema pour le backtesting
export const backtestRequestSchema = Joi.object({
  symbol: Joi.string().valid(...SUPPORTED_SYMBOLS).required(),
  strategy: Joi.string().required(),
  startDate: Joi.date().required(),
  endDate: Joi.date().required(),
  initialCapital: Joi.number().positive().min(100).required(),
  parameters: Joi.object().optional(),
});

// Schema pour les configurations système
export const configUpdateSchema = Joi.object({
  riskManagement: Joi.object({
    maxPositionSize: Joi.number().positive().max(100).optional(),
    maxLeverage: Joi.number().integer().min(1).max(50).optional(),
    stopLossPercentage: Joi.number().positive().max(1).optional(),
    takeProfitPercentage: Joi.number().positive().max(1).optional(),
  }).optional(),

  trading: Joi.object({
    defaultType: Joi.string().valid('market', 'limit').optional(),
    defaultLeverage: Joi.number().integer().min(1).max(50).optional(),
    slippageTolerance: Joi.number().positive().max(0.1).optional(),
  }).optional(),

  agents: Joi.object().optional(),
});

// Schema pour les filtres et pagination
export const paginationSchema = Joi.object({
  page: Joi.number().integer().min(1).default(1),
  limit: Joi.number().integer().min(1).max(100).default(20),
  sortBy: Joi.string().optional(),
  sortOrder: Joi.string().valid('asc', 'desc').default('desc'),
});

// Schema pour les requêtes WebSocket
export const websocketSubscriptionSchema = Joi.object({
  channel: Joi.string().valid(
    'trades',
    'orderbook',
    'quotes',
    'positions',
    'balance',
    'price'
  ).required(),
  symbol: Joi.string().valid(...SUPPORTED_SYMBOLS).when('channel', {
    is: 'balance',
    then: Joi.forbidden(),
    otherwise: Joi.required()
  }),
  interval: Joi.string().when('channel', {
    is: 'price',
    then: Joi.valid('1s', '5s', '10s', '30s').default('5s'),
    otherwise: Joi.forbidden()
  }),
});

// Utilitaires de validation
export class ValidationService {
  /**
   * ✅ Valider une requête
   */
  static validate<T>(schema: Joi.ObjectSchema<T>, data: any): { error?: string; value?: T } {
    const { error, value } = schema.validate(data, {
      abortEarly: false,
      stripUnknown: true,
      convert: true
    });

    if (error) {
      const details = error.details.map(detail => detail.message).join(', ');
      return { error: details };
    }

    return { value };
  }

  /**
   * ✅ Valider une requête avec middleware Express
   */
  static validateMiddleware(schema: Joi.ObjectSchema) {
    return (req: any, res: any, next: any) => {
      const { error, value } = schema.validate(req.body, {
        abortEarly: false,
        stripUnknown: true,
        convert: true
      });

      if (error) {
        const details = error.details.map(detail => ({
          field: detail.path?.join('.'),
          message: detail.message,
          value: detail.context?.value
        }));

        return res.status(400).json({
          error: 'Validation failed',
          details,
          timestamp: new Date().toISOString()
        });
      }

      req.validatedBody = value;
      next();
    };
  }

  /**
   * ✅ Valider les paramètres de requête (query params)
   */
  static validateQuery(schema: Joi.ObjectSchema) {
    return (req: any, res: any, next: any) => {
      const { error, value } = schema.validate(req.query, {
        abortEarly: false,
        stripUnknown: true,
        convert: true
      });

      if (error) {
        const details = error.details.map(detail => ({
          field: detail.path?.join('.'),
          message: detail.message,
          value: detail.context?.value
        }));

        return res.status(400).json({
          error: 'Query validation failed',
          details,
          timestamp: new Date().toISOString()
        });
      }

      req.validatedQuery = value;
      next();
    };
  }
}

// Export des schémas combinés
export const apiSchemas = {
  price: priceRequestSchema,
  trade: tradeRequestSchema,
  closePosition: closePositionSchema,
  positions: positionsRequestSchema,
  candles: candlesRequestSchema,
  agentControl: agentControlSchema,
  backtest: backtestRequestSchema,
  configUpdate: configUpdateSchema,
  pagination: paginationSchema,
  websocketSubscription: websocketSubscriptionSchema,
};

export default ValidationService;