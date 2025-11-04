/**
 * 💾 Memory Cache Simple
 * Cache en mémoire avec TTL et LRU eviction
 */

export interface CacheEntry<T> {
  value: T;
  expires: number;
  hits: number;
  lastAccessed: number;
}

export interface CacheStats {
  size: number;
  maxSize: number;
  hits: number;
  misses: number;
  hitRate: number;
  evictions: number;
  totalEntries: number;
}

export interface CacheConfig {
  maxSize: number;
  defaultTTL: number; // en millisecondes
  cleanupInterval: number;
  checkInterval: number;
}

export class MemoryCache {
  private cache = new Map<string, CacheEntry<any>>();
  private config: CacheConfig;
  private cleanupTimer?: NodeJS.Timeout;
  private stats: CacheStats = {
    size: 0,
    maxSize: 0,
    hits: 0,
    misses: 0,
    hitRate: 0,
    evictions: 0,
    totalEntries: 0
  };

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxSize: 1000,
      defaultTTL: 300000, // 5 minutes
      cleanupInterval: 60000, // 1 minute
      checkInterval: 10000, // 10 secondes
      ...config
    };

    this.stats.maxSize = this.config.maxSize;
    this.startCleanupTimer();
  }

  /**
   * 💾 Mettre en cache une valeur
   */
  set<T>(key: string, value: T, ttl?: number): void {
    const expires = Date.now() + (ttl || this.config.defaultTTL);

    // Si le cache est plein, nettoyer les entrées expirées
    if (this.cache.size >= this.config.maxSize) {
      this.evictExpired();
      if (this.cache.size >= this.config.maxSize) {
        this.evictLRU();
      }
    }

    const entry: CacheEntry<T> = {
      value,
      expires,
      hits: 0,
      lastAccessed: Date.now()
    };

    this.cache.set(key, entry);
    this.stats.size = this.cache.size;
    this.stats.totalEntries++;
  }

  /**
   * 🔍 Récupérer une valeur du cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      this.updateHitRate();
      return null;
    }

    // Vérifier si l'entrée est expirée
    if (Date.now() > entry.expires) {
      this.cache.delete(key);
      this.stats.size = this.cache.size;
      this.stats.misses++;
      this.updateHitRate();
      return null;
    }

    // Mettre à jour les stats
    entry.hits++;
    entry.lastAccessed = Date.now();
    this.stats.hits++;
    this.updateHitRate();

    return entry.value;
  }

  /**
   * 🔍 Vérifier si une clé existe
   */
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    // Vérifier l'expiration
    if (Date.now() > entry.expires) {
      this.cache.delete(key);
      this.stats.size = this.cache.size;
      return false;
    }

    return true;
  }

  /**
   * 🗑️ Supprimer une valeur du cache
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    if (deleted) {
      this.stats.size = this.cache.size;
    }
    return deleted;
  }

  /**
   * 🧹 Vider le cache
   */
  clear(): void {
    const oldSize = this.cache.size;
    this.cache.clear();
    this.stats.size = 0;
    this.stats.totalEntries += oldSize;
  }

  /**
   * 🔑 Obtenir les clés du cache
   */
  keys(): string[] {
    return Array.from(this.cache.keys());
  }

  /**
   * 📊 Obtenir les statistiques du cache
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * 🗑️ Supprimer les entrées expirées
   */
  evictExpired(): number {
    const now = Date.now();
    let evicted = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expires) {
        this.cache.delete(key);
        evicted++;
      }
    }

    this.stats.size = this.cache.size;
    this.stats.evictions += evicted;

    return evicted;
  }

  /**
   * 🔄 Supprimer les entrées les moins récemment utilisées (LRU)
   */
  evictLRU(): number {
    if (this.cache.size === 0) return 0;

    // Trier par lastAccessed (plus ancien en premier)
    const entries = Array.from(this.cache.entries())
      .sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);

    const toEvict = Math.ceil(this.config.maxSize * 0.2); // Éviter 20%
    const evicted = Math.min(toEvict, entries.length);

    for (let i = 0; i < evicted; i++) {
      this.cache.delete(entries[i][0]);
    }

    this.stats.size = this.cache.size;
    this.stats.evictions += evicted;

    return evicted;
  }

  /**
   * 🧹 Nettoyer automatiquement les entrées expirées
   */
  private startCleanupTimer(): void {
    this.cleanupTimer = setInterval(() => {
      const evicted = this.evictExpired();
      if (evicted > 0) {
        console.log(`[MemoryCache] 🧹 Cleaned up ${evicted} expired entries`);
      }
    }, this.config.cleanupInterval);
  }

  /**
   * 📈 Mettre à jour le hit rate
   */
  private updateHitRate(): void {
    const total = this.stats.hits + this.stats.misses;
    this.stats.hitRate = total > 0 ? this.stats.hits / total : 0;
  }

  /**
   * 🔄 Récupérer ou générer une valeur avec cache-aside pattern
   */
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    const value = await factory();
    this.set(key, value, ttl);
    return value;
  }

  /**
   * 🎯 Récupérer plusieurs valeurs en une fois
   */
  mget<T>(keys: string[]): Map<string, T | null> {
    const result = new Map<string, T | null>();

    for (const key of keys) {
      result.set(key, this.get<T>(key));
    }

    return result;
  }

  /**
   * 💾 Mettre plusieurs valeurs en cache en une fois
   */
  mset<T>(entries: Array<[string, T]>, ttl?: number): void {
    for (const [key, value] of entries) {
      this.set(key, value, ttl);
    }
  }

  /**
   * 🔍 Récupérer toutes les valeurs correspondant à un pattern
   */
  getValuesByPattern<T>(pattern: RegExp): Map<string, T> {
    const result = new Map<string, T>();

    for (const [key, entry] of this.cache.entries()) {
      if (pattern.test(key) && Date.now() <= entry.expires) {
        entry.hits++;
        entry.lastAccessed = Date.now();
        result.set(key, entry.value);
      }
    }

    return result;
  }

  /**
   * 🗑️ Supprimer toutes les valeurs correspondant à un pattern
   */
  deleteByPattern(pattern: RegExp): number {
    let deleted = 0;

    for (const [key] of this.cache.entries()) {
      if (pattern.test(key)) {
        this.cache.delete(key);
        deleted++;
      }
    }

    this.stats.size = this.cache.size;
    return deleted;
  }

  /**
   * 📊 Obtenir des statistiques détaillées
   */
  getDetailedStats(): {
    entries: Array<{
      key: string;
      size: number;
      age: number;
      hits: number;
      ttl: number;
    }>;
    size: number;
    maxSize: number;
    hits: number;
    misses: number;
    hitRate: number;
    evictions: number;
    totalEntries: number;
  } {
    const now = Date.now();
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      size: JSON.stringify(entry.value).length,
      age: now - (entry.expires - (this.config.defaultTTL)),
      hits: entry.hits,
      ttl: entry.expires - now
    }));

    return {
      entries,
      size: this.stats.size,
      maxSize: this.stats.maxSize,
      hits: this.stats.hits,
      misses: this.stats.misses,
      hitRate: this.stats.hitRate,
      evictions: this.stats.evictions,
      totalEntries: this.stats.totalEntries
    };
  }

  /**
   * 🛑 Détruire le cache et arrêter le nettoyage
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = undefined;
    }
    this.clear();
  }
}

export default MemoryCache;