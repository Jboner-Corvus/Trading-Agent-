/**
 * 🚀 HyperLiquid API Client - Implementation complète
 * Tous les appels API réels pour le trading sur HyperLiquid
 */

const axios = require('axios');
const HyperliquidSignature = require('./hyperliquid-signature');

class HyperliquidAPI {
    constructor(privateKey = null, useTestnet = false) {
        this.baseUrl = useTestnet ? 'https://api.hyperliquid-testnet.xyz' : 'https://api.hyperliquid.xyz';
        this.wsUrl = useTestnet ? 'wss://api.hyperliquid-testnet.xyz/ws' : 'wss://api.hyperliquid.xyz/ws';
        this.signature = new HyperliquidSignature();
        this.privateKey = privateKey;
        this.address = null;

        // Mapping des assets
        this.assetMapping = {
            'BTC': 0,
            'ETH': 1,
            'SOL': 2,
            'ARB': 3,
            'OP': 4,
            'MNT': 5,
            'BLUR': 6,
            'SUI': 7,
            'APT': 8,
            'DYDX': 9,
            'LDO': 10,
            'INJ': 11,
            'AAVE': 12,
            'LINK': 13,
            'UNI': 14,
            'FXS': 15,
            'GALA': 16,
            'APE': 17,
            'SAND': 18,
            'MANA': 19,
            'STG': 20,
            'RDNT': 21,
            'CFX': 22,
            'IMX': 23,
            'FTM': 24,
            'PEPE': 25,
            'AR': 26,
            'MAGIC': 27,
            'CRV': 28,
            'TRB': 29,
            'SYN': 30,
            'LOOKS': 31,
            'JUP': 32,
            'W': 33,
            'BONK': 34,
            'SEI': 35,
            'TIA': 36,
            'PYTH': 37,
            'ATOM': 38,
            'OSMO': 39,
            'DYM': 40,
            'JTO': 41,
            'STRK': 42,
            'ENA': 43,
            'ALT': 44,
            'ETHFI': 45,
            'ZK': 46,
            'PORTAL': 47,
            'RENDER': 48,
            'TAO': 49,
            'WIF': 50,
            'BOME': 51,
            'NOT': 52,
            'POPCAT': 53,
            'HMSTR': 54,
            'ME': 55,
            'NEIRO': 56,
            'GOAT': 57,
            'CHAOS': 58,
            'ZENT': 59,
            'HYPE': 107  // Spot HYPE
        };

        if (privateKey) {
            this.setPrivateKey(privateKey);
        }
    }

    /**
     * Définir la clé privée
     */
    setPrivateKey(privateKey) {
        this.privateKey = privateKey;
        const wallet = new (require('ethers')).Wallet(privateKey);
        this.address = wallet.address.toLowerCase();
    }

    /**
     * Récupérer tous les prix du milieu
     */
    async getAllMids() {
        try {
            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'allMids'
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getAllMids:', error);
            throw error;
        }
    }

    /**
     * Récupérer les métadonnées des perpétuels
     */
    async getMeta() {
        try {
            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'meta'
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getMeta:', error);
            throw error;
        }
    }

    /**
     * Récupérer les métadonnées des tokens spot
     */
    async getSpotMeta() {
        try {
            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'spotMeta'
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getSpotMeta:', error);
            throw error;
        }
    }

    /**
     * Récupérer les ordres ouverts d'un utilisateur
     */
    async getOpenOrders(userAddress = null) {
        try {
            const address = userAddress || this.address;
            if (!address) throw new Error('Adresse utilisateur requise');

            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'openOrders',
                user: address
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getOpenOrders:', error);
            throw error;
        }
    }

    /**
     * Récupérer les positions d'un utilisateur
     */
    async getUserPosition(userAddress = null) {
        try {
            const address = userAddress || this.address;
            if (!address) throw new Error('Adresse utilisateur requise');

            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'clearinghouseState',
                user: address
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getUserPosition:', error);
            throw error;
        }
    }

    /**
     * Récupérer l'historique des trades
     */
    async getUserFills(userAddress = null) {
        try {
            const address = userAddress || this.address;
            if (!address) throw new Error('Adresse utilisateur requise');

            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'userFills',
                user: address
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getUserFills:', error);
            throw error;
        }
    }

    /**
     * Récupérer le order book L2
     */
    async getL2Book(coin) {
        try {
            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'l2Book',
                coin: coin
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getL2Book:', error);
            throw error;
        }
    }

    /**
     * Récupérer l'historique des bougies
     */
    async getCandles(coin, interval, startTime, endTime) {
        try {
            const response = await axios.post(`${this.baseUrl}/info`, {
                type: 'candleSnapshot',
                req: {
                    coin: coin,
                    interval: interval,
                    startTime: startTime,
                    endTime: endTime
                }
            });
            return response.data;
        } catch (error) {
            console.error('Erreur getCandles:', error);
            throw error;
        }
    }

    /**
     * Placer un ordre (fonction principale)
     */
    async placeOrder(asset, isBuy, price, size, reduceOnly = false, timeInForce = 'Gtc') {
        try {
            if (!this.privateKey) throw new Error('Clé privée requise');

            const orderData = this.signature.createOrder(asset, isBuy, price, size, reduceOnly, timeInForce);
            const signedOrder = await this.signature.signOrder(this.privateKey, orderData);

            const response = await axios.post(`${this.baseUrl}/exchange`, {
                action: signedOrder.action,
                nonce: signedOrder.nonce,
                signature: signedOrder.signature
            });

            return response.data;
        } catch (error) {
            console.error('Erreur placeOrder:', error);
            throw error;
        }
    }

    /**
     * Placer un ordre de marché
     */
    async placeMarketOrder(asset, isBuy, size, reduceOnly = false) {
        try {
            if (!this.privateKey) throw new Error('Clé privée requise');

            const orderData = this.signature.createMarketOrder(asset, isBuy, size, reduceOnly);
            const signedOrder = await this.signature.signOrder(this.privateKey, orderData);

            const response = await axios.post(`${this.baseUrl}/exchange`, {
                action: signedOrder.action,
                nonce: signedOrder.nonce,
                signature: signedOrder.signature
            });

            return response.data;
        } catch (error) {
            console.error('Erreur placeMarketOrder:', error);
            throw error;
        }
    }

    /**
     * Annuler un ordre
     */
    async cancelOrder(asset, orderId) {
        try {
            if (!this.privateKey) throw new Error('Clé privée requise');

            const cancelData = {
                type: 'cancel',
                cancels: [{
                    a: asset,
                    o: orderId
                }]
            };

            const signedCancel = await this.signature.signOrder(this.privateKey, cancelData);

            const response = await axios.post(`${this.baseUrl}/exchange`, {
                action: signedCancel.action,
                nonce: signedCancel.nonce,
                signature: signedCancel.signature
            });

            return response.data;
        } catch (error) {
            console.error('Erreur cancelOrder:', error);
            throw error;
        }
    }

    /**
     * Annuler tous les ordres
     */
    async cancelAllOrders() {
        try {
            if (!this.privateKey) throw new Error('Clé privée requise');

            const openOrders = await this.getOpenOrders();
            if (!openOrders.orders || openOrders.orders.length === 0) {
                return { status: 'no_orders_to_cancel' };
            }

            const cancels = openOrders.orders.map(order => ({
                a: order.coin,
                o: order.oid
            }));

            const cancelData = {
                type: 'cancel',
                cancels: cancels
            };

            const signedCancel = await this.signature.signOrder(this.privateKey, cancelData);

            const response = await axios.post(`${this.baseUrl}/exchange`, {
                action: signedCancel.action,
                nonce: signedCancel.nonce,
                signature: signedCancel.signature
            });

            return response.data;
        } catch (error) {
            console.error('Erreur cancelAllOrders:', error);
            throw error;
        }
    }

    /**
     * Modifier un ordre
     */
    async modifyOrder(orderId, asset, isBuy, price, size, reduceOnly = false) {
        try {
            if (!this.privateKey) throw new Error('Clé privée requise');

            const modifyData = {
                type: 'modify',
                oid: orderId,
                order: this.signature.createModifyOrder(orderId, asset, isBuy, price, size, reduceOnly)
            };

            const signedModify = await this.signature.signOrder(this.privateKey, modifyData);

            const response = await axios.post(`${this.baseUrl}/exchange`, {
                action: signedModify.action,
                nonce: signedModify.nonce,
                signature: signedModify.signature
            });

            return response.data;
        } catch (error) {
            console.error('Erreur modifyOrder:', error);
            throw error;
        }
    }

    /**
     * Mettre à jour le levier
     */
    async updateLeverage(asset, leverage, isCross = true) {
        try {
            if (!this.privateKey) throw new Error('Clé privée requise');

            const leverageData = {
                type: 'updateLeverage',
                asset: asset,
                isCross: isCross,
                leverage: leverage
            };

            const signedLeverage = await this.signature.signOrder(this.privateKey, leverageData);

            const response = await axios.post(`${this.baseUrl}/exchange`, {
                action: signedLeverage.action,
                nonce: signedLeverage.nonce,
                signature: signedLeverage.signature
            });

            return response.data;
        } catch (error) {
            console.error('Erreur updateLeverage:', error);
            throw error;
        }
    }

    /**
     * Transférer USDC
     */
    async transferUSDC(destination, amount, hyperliquidChain = 'Mainnet') {
        try {
            if (!this.privateKey) throw new Error('Clé privée requise');

            const transferData = {
                type: 'usdSend',
                hyperliquidChain: hyperliquidChain,
                signatureChainId: '0xa4b1', // HyperEVM chain ID
                destination: destination.toLowerCase(),
                amount: amount.toString(),
                time: Date.now()
            };

            const signedTransfer = await this.signature.signUserAction(this.privateKey, transferData);

            const response = await axios.post(`${this.baseUrl}/exchange`, {
                action: signedTransfer.action,
                nonce: signedTransfer.nonce,
                signature: signedTransfer.signature
            });

            return response.data;
        } catch (error) {
            console.error('Erreur transferUSDC:', error);
            throw error;
        }
    }

    /**
     * Obtenir le solde USDC
     */
    async getUSDCBalance(userAddress = null) {
        try {
            const position = await this.getUserPosition(userAddress);
            return position.marginSummary?.accountValue || '0';
        } catch (error) {
            console.error('Erreur getUSDCBalance:', error);
            return '0';
        }
    }

    /**
     * Convertir un symbole en asset ID
     */
    symbolToAsset(symbol) {
        return this.assetMapping[symbol.toUpperCase()] || null;
    }

    /**
     * Convertir un asset ID en symbole
     */
    assetToSymbol(asset) {
        const symbols = Object.keys(this.assetMapping);
        for (const symbol of symbols) {
            if (this.assetMapping[symbol] === asset) {
                return symbol;
            }
        }
        return null;
    }
}

module.exports = HyperliquidAPI;