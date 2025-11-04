/**
 * 🛡️ Security Headers Avancés
 * Configuration des headers de sécurité avec Helmet et personnalisations
 */

import helmet, { HelmetOptions } from 'helmet';
import { Request, Response, NextFunction } from 'express';

export interface SecurityConfig {
  contentSecurityPolicy?: {
    directives?: any;
    reportOnly?: boolean;
  };
  crossOriginEmbedderPolicy?: boolean;
  crossOriginOpenerPolicy?: boolean;
  crossOriginResourcePolicy?: any;
  dnsPrefetchControl?: boolean;
  frameguard?: any;
  hidePoweredBy?: boolean;
  hsts?: any;
  ieNoOpen?: boolean;
  noSniff?: boolean;
  originAgentCluster?: boolean;
  permittedCrossDomainPolicies?: boolean;
  referrerPolicy?: any;
  xssFilter?: boolean;
  customHeaders?: Array<{
    name: string;
    value: string;
  }>;
}

export class SecurityHeadersService {
  private static config: SecurityConfig = {
    // Politique de sécurité de contenu stricte
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: [
          "'self'",
          "'unsafe-inline'",
          "https://fonts.googleapis.com",
          "https://cdnjs.cloudflare.com"
        ],
        scriptSrc: [
          "'self'",
          "'unsafe-eval'", // Pour React/TypeScript développement
          "https://cdnjs.cloudflare.com"
        ],
        imgSrc: [
          "'self'",
          "data:",
          "https:",
          "blob:"
        ],
        connectSrc: [
          "'self'",
          "ws:",
          "wss:",
          "https://api.hyperliquid.xyz",
          "http://localhost:7000",
          "http://localhost:7002"
        ],
        fontSrc: [
          "'self'",
          "https://fonts.gstatic.com",
          "data:"
        ],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
        childSrc: ["'none'"],
        workerSrc: ["'self'", "blob:"],
        manifestSrc: ["'self'"],
        upgradeInsecureRequests: []
      },
      reportOnly: false
    },

    // Protection contre l'embedding cross-origin
    crossOriginEmbedderPolicy: false, // Désactivé pour compatibilité

    // Politique d'ouverture cross-origin
    crossOriginOpenerPolicy: {
      policy: "same-origin"
    },

    // Politique de ressource cross-origin
    crossOriginResourcePolicy: {
      policy: "cross-origin"
    },

    // Contrôle du DNS prefetching
    dnsPrefetchControl: {
      allow: false
    },

    // Protection contre le clickjacking
    frameguard: {
      action: 'deny'
    },

    // Cacher le header X-Powered-By
    hidePoweredBy: true,

    // HTTP Strict Transport Security
    hsts: {
      maxAge: 31536000, // 1 an
      includeSubDomains: true,
      preload: true
    },

    // Protection contre l'ouverture de fichiers IE
    ieNoOpen: true,

    // Protection contre le MIME type sniffing
    noSniff: true,

    // Isolation d'origine
    originAgentCluster: true,

    // Politiques de domaine cross-domain
    permittedCrossDomainPolicies: false,

    // Politique de référent
    referrerPolicy: {
      policy: ["no-referrer", "strict-origin-when-cross-origin"]
    },

    // Filtre XSS
    xssFilter: true,

    // Headers personnalisés supplémentaires
    customHeaders: [
      {
        name: 'X-Content-Type-Options',
        value: 'nosniff'
      },
      {
        name: 'X-Download-Options',
        value: 'noopen'
      },
      {
        name: 'X-Permitted-Cross-Domain-Policies',
        value: 'none'
      },
      {
        name: 'X-XSS-Protection',
        value: '1; mode=block'
      },
      {
        name: 'Permissions-Policy',
        value: 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()'
      },
      {
        name: 'Clear-Site-Data',
        value: '"cache", "cookies", "storage", "executionContexts"'
      }
    ]
  };

  /**
   * 🛡️ Créer le middleware Helmet avec configuration complète
   */
  static createHelmet(config: Partial<SecurityConfig> = {}) {
    const finalConfig = { ...this.config, ...config };

    const helmetOptions: HelmetOptions = {
      contentSecurityPolicy: finalConfig.contentSecurityPolicy,
      crossOriginEmbedderPolicy: finalConfig.crossOriginEmbedderPolicy,
      crossOriginOpenerPolicy: finalConfig.crossOriginOpenerPolicy,
      crossOriginResourcePolicy: finalConfig.crossOriginResourcePolicy,
      dnsPrefetchControl: finalConfig.dnsPrefetchControl,
      frameguard: finalConfig.frameguard,
      hidePoweredBy: finalConfig.hidePoweredBy,
      hsts: finalConfig.hsts,
      ieNoOpen: finalConfig.ieNoOpen,
      noSniff: finalConfig.noSniff,
      originAgentCluster: finalConfig.originAgentCluster,
      permittedCrossDomainPolicies: finalConfig.permittedCrossDomainPolicies,
      referrerPolicy: finalConfig.referrerPolicy,
      xssFilter: finalConfig.xssFilter
    };

    return helmet(helmetOptions);
  }

  /**
   * 🔧 Créer un middleware pour les headers personnalisés
   */
  static createCustomHeaders(customHeaders?: Array<{ name: string; value: string }>) {
    const headers = customHeaders || this.config.customHeaders || [];

    return (req: Request, res: Response, next: NextFunction) => {
      headers.forEach(header => {
        res.setHeader(header.name, header.value);
      });
      next();
    };
  }

  /**
   * 🚀 Créer un middleware de sécurité complet
   */
  static createSecurityMiddleware(config: Partial<SecurityConfig> = {}) {
    const helmetMiddleware = this.createHelmet(config);
    const customHeadersMiddleware = this.createCustomHeaders(config.customHeaders);

    return [helmetMiddleware, customHeadersMiddleware];
  }

  /**
   * 🔒 Configuration pour environnement de développement
   */
  static getDevelopmentConfig(): SecurityConfig {
    return {
      ...this.config,
      contentSecurityPolicy: {
        ...this.config.contentSecurityPolicy,
        directives: {
          ...this.config.contentSecurityPolicy!.directives,
          scriptSrc: [
            "'self'",
            "'unsafe-eval'",
            "'unsafe-inline'", // Pour le développement
            "https://cdnjs.cloudflare.com"
          ],
          styleSrc: [
            "'self'",
            "'unsafe-inline'",
            "https://fonts.googleapis.com",
            "https://cdnjs.cloudflare.com"
          ]
        }
      },
      hsts: {
        maxAge: 3600, // 1 heure pour le développement
        includeSubDomains: false,
        preload: false
      }
    };
  }

  /**
   * 🏭 Configuration pour environnement de production
   */
  static getProductionConfig(): SecurityConfig {
    return {
      ...this.config,
      contentSecurityPolicy: {
        ...this.config.contentSecurityPolicy,
        directives: {
          ...this.config.contentSecurityPolicy!.directives,
          scriptSrc: [
            "'self'",
            "https://cdnjs.cloudflare.com"
          ],
          styleSrc: [
            "'self'",
            "https://fonts.googleapis.com",
            "https://cdnjs.cloudflare.com"
          ]
        }
      },
      crossOriginEmbedderPolicy: true, // Activé en production
      customHeaders: [
        ...this.config.customHeaders!,
        {
          name: 'Expect-CT',
          value: 'max-age=86400, enforce'
        },
        {
          name: 'NEL',
          value: '{"report_to":"default","max_age":31536000,"include_subdomains":true}'
        }
      ]
    };
  }

  /**
   * 🔧 Configuration pour environnement de test
   */
  static getTestConfig(): SecurityConfig {
    return {
      ...this.config,
      contentSecurityPolicy: false, // Désactivé pour les tests
      hsts: false,
      frameguard: { action: 'sameorigin' } // Moins strict pour les tests
    };
  }

  /**
   * 🎯 Obtenir la configuration appropriée selon l'environnement
   */
  static getConfigForEnvironment(env: string = process.env.NODE_ENV || 'development'): SecurityConfig {
    switch (env.toLowerCase()) {
      case 'production':
        return this.getProductionConfig();
      case 'test':
        return this.getTestConfig();
      case 'development':
      default:
        return this.getDevelopmentConfig();
    }
  }

  /**
   * 🛡️ Middleware pour détecter les attaques courantes
   */
  static createSecurityMonitor() {
    return (req: Request, res: Response, next: NextFunction) => {
      // Détecter les patterns suspects dans les headers
      const suspiciousPatterns = [
        /<script/i,
        /javascript:/i,
        /on\w+\s*=/i,
        /data:text\/html/i
      ];

      const checkString = (str: string): boolean => {
        return suspiciousPatterns.some(pattern => pattern.test(str));
      };

      // Vérifier les headers courants
      const headersToCheck = ['user-agent', 'referer', 'x-forwarded-for'];
      for (const header of headersToCheck) {
        const value = req.get(header);
        if (value && checkString(value)) {
          console.warn(`[Security] Suspicious pattern detected in ${header}:`, value);
          // En production, on pourrait logger plus détaillé ou bloquer
        }
      }

      // Vérifier les paramètres de requête
      for (const [key, value] of Object.entries(req.query)) {
        if (typeof value === 'string' && checkString(value)) {
          console.warn(`[Security] Suspicious pattern detected in query param ${key}:`, value);
        }
      }

      next();
    };
  }

  /**
   * 🔒 Middleware pour validation CORS avancée
   */
  static createAdvancedCORS() {
    return (req: Request, res: Response, next: NextFunction) => {
      const origin = req.get('Origin');
      const allowedOrigins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'https://yourdomain.com' // Ajouter vos domaines de production
      ];

      // En développement, autoriser localhost avec n'importe quel port
      const isDevelopment = process.env.NODE_ENV === 'development';
      const isAllowedOrigin = isDevelopment && origin?.startsWith('http://localhost:') ||
                            allowedOrigins.includes(origin || '');

      if (isAllowedOrigin) {
        res.setHeader('Access-Control-Allow-Origin', origin || '');
      }

      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers',
        'Content-Type, Authorization, X-Requested-With, Accept, Origin'
      );
      res.setHeader('Access-Control-Allow-Credentials', 'true');
      res.setHeader('Access-Control-Max-Age', '86400'); // 24 heures

      // Gérer les requêtes preflight
      if (req.method === 'OPTIONS') {
        return res.status(200).end();
      }

      next();
    };
  }

  /**
   * 📊 Middleware pour logging des requêtes de sécurité
   */
  static createSecurityLogger() {
    return (req: Request, res: Response, next: NextFunction) => {
      const start = Date.now();

      // Logger les informations de requête
      const logData = {
        timestamp: new Date().toISOString(),
        method: req.method,
        url: req.url,
        ip: req.ip || req.connection.remoteAddress,
        userAgent: req.get('User-Agent'),
        referer: req.get('Referer'),
        contentType: req.get('Content-Type')
      };

      console.log('[Security] Request:', logData);

      // Logger la réponse
      res.on('finish', () => {
        const duration = Date.now() - start;
        console.log('[Security] Response:', {
          ...logData,
          statusCode: res.statusCode,
          duration: `${duration}ms`
        });
      });

      next();
    };
  }

  /**
   * 🎯 Créer un middleware de sécurité complet et intégré
   */
  static createCompleteSecuritySuite(env?: string) {
    const config = this.getConfigForEnvironment(env);
    const securityMiddleware = this.createSecurityMiddleware(config);
    const corsMiddleware = this.createAdvancedCORS();
    const securityMonitor = this.createSecurityMonitor();
    const securityLogger = this.createSecurityLogger();

    return [
      securityLogger,
      corsMiddleware,
      securityMonitor,
      ...securityMiddleware
    ];
  }
}

export default SecurityHeadersService;