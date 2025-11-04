/**
 * 🔄 WebSocket Manager Résilient
 * Gestion intelligente des connexions WebSocket avec retry et monitoring
 */

import { EventEmitter } from 'events';

export interface WebSocketConfig {
  maxRetries: number;
  retryDelay: number;
  backoffMultiplier: number;
  heartbeatInterval: number;
  connectionTimeout: number;
}

export interface WebSocketStatus {
  connected: boolean;
  lastConnected?: Date;
  lastDisconnected?: Date;
  retryCount: number;
  totalRetries: number;
  uptime: number;
}

export class ResilientWebSocket extends EventEmitter {
  private config: WebSocketConfig;
  private ws?: WebSocket;
  private retryTimer?: NodeJS.Timeout;
  private heartbeatTimer?: NodeJS.Timeout;
  private reconnectAttempts = 0;
  private connectionStartTime?: Date;
  private lastPingTime?: Date;
  private status: WebSocketStatus = {
    connected: false,
    retryCount: 0,
    totalRetries: 0,
    uptime: 0
  };

  constructor(
    private url: string,
    config: Partial<WebSocketConfig> = {}
  ) {
    super();

    this.config = {
      maxRetries: 10,
      retryDelay: 1000,
      backoffMultiplier: 2,
      heartbeatInterval: 30000,
      connectionTimeout: 10000,
      ...config
    };
  }

  /**
   * 🚀 Démarrer la connexion WebSocket
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.emit('connecting');
    this.connectionStartTime = new Date();

    try {
      this.ws = new WebSocket(this.url);
      this.setupWebSocketHandlers();

      // Timeout de connexion
      setTimeout(() => {
        if (this.ws?.readyState !== WebSocket.OPEN) {
          this.handleConnectionError(new Error('Connection timeout'));
        }
      }, this.config.connectionTimeout);

    } catch (error) {
      this.handleConnectionError(error as Error);
    }
  }

  /**
   * 🛑 Déconnecter proprement
   */
  disconnect(): void {
    this.clearTimers();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = undefined;
    }

    this.status.connected = false;
    this.status.lastDisconnected = new Date();
    this.emit('disconnected');
  }

  /**
   * 📤 Envoyer un message (avec retry si déconnecté)
   */
  send(data: string | ArrayBufferLike | Blob): boolean {
    if (!this.isReady()) {
      this.emit('sendError', new Error('WebSocket not connected'));
      return false;
    }

    try {
      this.ws!.send(data);
      return true;
    } catch (error) {
      this.emit('sendError', error);
      return false;
    }
  }

  /**
   * ✅ Vérifier si le WebSocket est prêt
   */
  isReady(): boolean {
    return this.ws?.readyState === WebSocket.OPEN && this.status.connected;
  }

  /**
   * 📊 Obtenir le statut actuel
   */
  getStatus(): WebSocketStatus {
    if (this.status.connected && this.connectionStartTime) {
      this.status.uptime = Date.now() - this.connectionStartTime.getTime();
    }

    return { ...this.status };
  }

  private setupWebSocketHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => this.handleOpen();
    this.ws.onclose = (event) => this.handleClose(event);
    this.ws.onerror = (error) => this.handleError(error);
    this.ws.onmessage = (event) => this.handleMessage(event);
  }

  private handleOpen(): void {
    this.status.connected = true;
    this.status.lastConnected = new Date();
    this.reconnectAttempts = 0;
    this.connectionStartTime = new Date();

    this.emit('connected');
    this.startHeartbeat();

    console.log(`[WebSocket] ✅ Connected to ${this.url}`);
  }

  private handleClose(event: CloseEvent): void {
    this.status.connected = false;
    this.status.lastDisconnected = new Date();
    this.clearTimers();

    console.log(`[WebSocket] 🔌 Disconnected: ${event.code} - ${event.reason}`);
    this.emit('disconnected', event);

    // Auto-reconnexion si non manuelle
    if (event.code !== 1000 && this.reconnectAttempts < this.config.maxRetries) {
      this.scheduleReconnect();
    }
  }

  private handleError(error: Event): void {
    console.error(`[WebSocket] ❌ Error:`, error);
    this.emit('error', error);
  }

  private handleMessage(event: MessageEvent): void {
    // Heartbeat PONG
    if (event.data === 'pong') {
      this.lastPingTime = new Date();
      return;
    }

    this.emit('message', event);
  }

  private handleConnectionError(error: Error): void {
    console.error(`[WebSocket] ❌ Connection failed:`, error);
    this.emit('error', error);

    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    this.clearTimers();

    const delay = this.calculateRetryDelay();
    this.reconnectAttempts++;
    this.status.retryCount = this.reconnectAttempts;
    this.status.totalRetries++;

    console.log(`[WebSocket] 🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.config.maxRetries})`);

    this.retryTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private calculateRetryDelay(): number {
    const baseDelay = this.config.retryDelay;
    const exponentialDelay = baseDelay * Math.pow(this.config.backoffMultiplier, this.reconnectAttempts - 1);
    const jitter = Math.random() * 1000; // Jitter pour éviter les cascades

    return Math.min(exponentialDelay + jitter, 30000); // Max 30s
  }

  private startHeartbeat(): void {
    this.clearTimers();

    this.heartbeatTimer = setInterval(() => {
      if (this.isReady()) {
        this.lastPingTime = new Date();
        this.send('ping');

        // Vérifier si le PONG a été reçu
        setTimeout(() => {
          if (this.lastPingTime && Date.now() - this.lastPingTime.getTime() > 25000) {
            console.warn('[WebSocket] ⚠️ Heartbeat timeout - reconnecting');
            this.handleConnectionError(new Error('Heartbeat timeout'));
          }
        }, 25000);
      }
    }, this.config.heartbeatInterval);
  }

  private clearTimers(): void {
    if (this.retryTimer) {
      clearTimeout(this.retryTimer);
      this.retryTimer = undefined;
    }

    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
  }
}

export default ResilientWebSocket;