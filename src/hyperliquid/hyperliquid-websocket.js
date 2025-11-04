/**
 * 🌐 HyperLiquid WebSocket Client - Données en temps réel
 * Connexion WebSocket pour les prix, ordres et positions en direct
 */

const WebSocket = require('ws');
const EventEmitter = require('events');

class HyperliquidWebSocket extends EventEmitter {
    constructor(useTestnet = false) {
        super();
        this.wsUrl = useTestnet ? 'wss://api.hyperliquid-testnet.xyz/ws' : 'wss://api.hyperliquid.xyz/ws';
        this.ws = null;
        this.subscriptions = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnecting = false;
        this.isConnected = false;
    }

    /**
     * Connexion au WebSocket
     */
    connect() {
        if (this.isConnecting || this.isConnected) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            this.isConnecting = true;

            try {
                this.ws = new WebSocket(this.wsUrl);

                this.ws.on('open', () => {
                    console.log('✅ WebSocket HyperLiquid connecté');
                    this.isConnecting = false;
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.emit('connected');
                    resolve();
                });

                this.ws.on('message', (data) => {
                    try {
                        const message = JSON.parse(data.toString());
                        this.handleMessage(message);
                    } catch (error) {
                        console.error('Erreur parsing message WebSocket:', error);
                    }
                });

                this.ws.on('error', (error) => {
                    console.error('❌ Erreur WebSocket:', error);
                    this.isConnecting = false;
                    this.emit('error', error);
                    reject(error);
                });

                this.ws.on('close', (code, reason) => {
                    console.log(`🔌 WebSocket déconnecté: ${code} - ${reason}`);
                    this.isConnected = false;
                    this.isConnecting = false;
                    this.emit('disconnected', { code, reason });

                    // Reconnexion automatique
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnect();
                    }
                });

            } catch (error) {
                this.isConnecting = false;
                reject(error);
            }
        });
    }

    /**
     * Reconnexion automatique
     */
    reconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`🔄 Tentative de reconnexion ${this.reconnectAttempts}/${this.maxReconnectAttempts} dans ${delay}ms`);

        setTimeout(() => {
            this.connect().catch(error => {
                console.error('Échec reconnexion:', error);
            });
        }, delay);
    }

    /**
     * Déconnexion
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.isConnecting = false;
    }

    /**
     * S'abonner aux prix de tous les marchés
     */
    subscribeAllMids() {
        if (!this.isConnected) {
            throw new Error('WebSocket non connecté');
        }

        const subscription = {
            method: 'subscribe',
            subscription: {
                type: 'allMids'
            }
        };

        this.ws.send(JSON.stringify(subscription));
        this.subscriptions.set('allMids', subscription);
    }

    /**
     * S'abonner aux trades d'un marché spécifique
     */
    subscribeTrades(coin) {
        if (!this.isConnected) {
            throw new Error('WebSocket non connecté');
        }

        const subscription = {
            method: 'subscribe',
            subscription: {
                type: 'trades',
                coin: coin
            }
        };

        this.ws.send(JSON.stringify(subscription));
        const key = `trades_${coin}`;
        this.subscriptions.set(key, subscription);
    }

    /**
     * S'abonner à l'order book L2 d'un marché
     */
    subscribeL2Book(coin) {
        if (!this.isConnected) {
            throw new Error('WebSocket non connecté');
        }

        const subscription = {
            method: 'subscribe',
            subscription: {
                type: 'l2Book',
                coin: coin
            }
        };

        this.ws.send(JSON.stringify(subscription));
        const key = `l2Book_${coin}`;
        this.subscriptions.set(key, subscription);
    }

    /**
     * S'abonner aux notifications d'utilisateur
     */
    subscribeUserNotifications(userAddress) {
        if (!this.isConnected) {
            throw new Error('WebSocket non connecté');
        }

        const subscription = {
            method: 'subscribe',
            subscription: {
                type: 'notification',
                user: userAddress.toLowerCase()
            }
        };

        this.ws.send(JSON.stringify(subscription));
        const key = `notifications_${userAddress}`;
        this.subscriptions.set(key, subscription);
    }

    /**
     * S'abonner aux mises à jour d'ordres d'un utilisateur
     */
    subscribeOrderUpdates(userAddress) {
        if (!this.isConnected) {
            throw new Error('WebSocket non connecté');
        }

        const subscription = {
            method: 'subscribe',
            subscription: {
                type: 'orderUpdates',
                user: userAddress.toLowerCase()
            }
        };

        this.ws.send(JSON.stringify(subscription));
        const key = `orderUpdates_${userAddress}`;
        this.subscriptions.set(key, subscription);
    }

    /**
     * S'abonner aux mises à jour de positions d'un utilisateur
     */
    subscribePositionUpdates(userAddress) {
        if (!this.isConnected) {
            throw new Error('WebSocket non connecté');
        }

        const subscription = {
            method: 'subscribe',
            subscription: {
                type: 'positionUpdates',
                user: userAddress.toLowerCase()
            }
        };

        this.ws.send(JSON.stringify(subscription));
        const key = `positionUpdates_${userAddress}`;
        this.subscriptions.set(key, subscription);
    }

    /**
     * Se désabonner d'une souscription
     */
    unsubscribe(subscriptionKey) {
        if (!this.isConnected || !this.subscriptions.has(subscriptionKey)) {
            return;
        }

        const unsubscription = {
            method: 'unsubscribe',
            subscription: this.subscriptions.get(subscriptionKey).subscription
        };

        this.ws.send(JSON.stringify(unsubscription));
        this.subscriptions.delete(subscriptionKey);
    }

    /**
     * Traiter les messages reçus
     */
    handleMessage(message) {
        // Message de souscription
        if (message.subscription) {
            this.emit('subscribed', message.subscription);
            return;
        }

        // Message de données
        if (message.data) {
            const data = message.data;

            // Prix du milieu
            if (data.allMids) {
                this.emit('allMids', data.allMids);
                return;
            }

            // Trades
            if (data.trades) {
                this.emit('trades', {
                    coin: data.coin,
                    trades: data.trades
                });
                return;
            }

            // Order book L2
            if (data.l2Book) {
                this.emit('l2Book', {
                    coin: data.coin,
                    book: data.l2Book
                });
                return;
            }

            // Notifications utilisateur
            if (data.notification) {
                this.emit('notification', data.notification);
                return;
            }

            // Mises à jour d'ordres
            if (data.orderUpdates) {
                this.emit('orderUpdates', data.orderUpdates);
                return;
            }

            // Mises à jour de positions
            if (data.positionUpdates) {
                this.emit('positionUpdates', data.positionUpdates);
                return;
            }
        }

        // Message d'erreur
        if (message.error) {
            this.emit('error', message.error);
            return;
        }
    }

    /**
     * Envoyer un ping pour maintenir la connexion
     */
    ping() {
        if (this.isConnected && this.ws) {
            this.ws.ping();
        }
    }

    /**
     * Obtenir le statut de la connexion
     */
    getStatus() {
        return {
            isConnected: this.isConnected,
            isConnecting: this.isConnecting,
            subscriptions: Array.from(this.subscriptions.keys()),
            reconnectAttempts: this.reconnectAttempts
        };
    }

    /**
     * S'abonner à tous les flux de données pour un utilisateur
     */
    subscribeUserData(userAddress, coins = ['BTC', 'ETH', 'SOL']) {
        // S'abonner aux notifications utilisateur
        this.subscribeUserNotifications(userAddress);

        // S'abonner aux mises à jour d'ordres
        this.subscribeOrderUpdates(userAddress);

        // S'abonner aux mises à jour de positions
        this.subscribePositionUpdates(userAddress);

        // S'abonner aux trades et order books pour les coins spécifiés
        coins.forEach(coin => {
            this.subscribeTrades(coin);
            this.subscribeL2Book(coin);
        });

        // S'abonner à tous les prix
        this.subscribeAllMids();
    }

    /**
     * Configurer le ping automatique
     */
    startPingInterval(interval = 30000) {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }

        this.pingInterval = setInterval(() => {
            this.ping();
        }, interval);
    }

    /**
     * Arrêter le ping automatique
     */
    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }
}

module.exports = HyperliquidWebSocket;