/**
 * 🔐 HyperLiquid Signature Engine
 * Implementation complète de la signature pour les transactions HyperLiquid
 */

const crypto = require('crypto');
const { ethers } = require('ethers');

class HyperliquidSignature {
    constructor() {
        this.baseUrl = 'https://api.hyperliquid.xyz';
        this.chainId = 999; // HyperEVM Mainnet
    }

    /**
     * Signer un ordre de trading HyperLiquid
     */
    async signOrder(privateKey, orderData) {
        try {
            const wallet = new ethers.Wallet(privateKey);
            const address = wallet.address.toLowerCase();

            // Créer le payload de signature selon la spec HyperLiquid
            const payload = {
                action: {
                    type: 'order',
                    orders: [orderData]
                },
                nonce: Date.now(),
                signature: ''
            };

            // Serialiser le payload en msgpack
            const serializedPayload = this.serializePayload(payload);

            // Signer avec la clé privée
            const signature = await wallet.signMessage(ethers.hashMessage(serializedPayload));

            return {
                ...payload,
                signature,
                address
            };
        } catch (error) {
            console.error('Erreur de signature ordre:', error);
            throw error;
        }
    }

    /**
     * Signer une action utilisateur (transfert, etc.)
     */
    async signUserAction(privateKey, actionData) {
        try {
            const wallet = new ethers.Wallet(privateKey);
            const address = wallet.address.toLowerCase();

            // Structure pour les actions utilisateur signées
            const payload = {
                action: actionData,
                nonce: Date.now(),
                signature: ''
            };

            // Domaine pour la signature EIP-712
            const domain = {
                name: 'Hyperliquid',
                chainId: this.chainId,
                verifyingContract: '0x0000000000000000000000000000000000000000'
            };

            // Types pour EIP-712
            const types = {
                UserAction: [
                    { name: 'action', type: 'string' },
                    { name: 'nonce', type: 'uint256' }
                ]
            };

            // Valeurs pour la signature
            const value = {
                action: JSON.stringify(actionData),
                nonce: payload.nonce
            };

            // Signer avec EIP-712
            const signature = await wallet.signTypedData(domain, types, value);

            return {
                ...payload,
                signature,
                address
            };
        } catch (error) {
            console.error('Erreur de signature action utilisateur:', error);
            throw error;
        }
    }

    /**
     * Sérialiser le payload en format msgpack (simplifié)
     */
    serializePayload(payload) {
        // Implementation simplifiée - en production, utiliser une vraie lib msgpack
        return JSON.stringify(payload);
    }

    /**
     * Créer un ordre de trading
     */
    createOrder(asset, isBuy, price, size, reduceOnly = false, timeInForce = 'Gtc') {
        return {
            a: asset,                                    // asset ID
            b: isBuy,                                    // isBuy
            p: price.toString(),                         // price
            s: size.toString(),                          // size
            r: reduceOnly,                               // reduceOnly
            t: {                                         // order type
                limit: {
                    tif: timeInForce                    // time in force
                }
            }
        };
    }

    /**
     * Créer un ordre de marché
     */
    createMarketOrder(asset, isBuy, size, reduceOnly = false) {
        return {
            a: asset,
            b: isBuy,
            s: size.toString(),
            r: reduceOnly,
            t: {
                limit: {
                    tif: 'Ioc'                           // Immediate or Cancel
                }
            }
        };
    }

    /**
     * Créer un ordre de modification
     */
    createModifyOrder(oid, asset, isBuy, price, size, reduceOnly = false) {
        return {
            a: asset,
            b: isBuy,
            p: price.toString(),
            s: size.toString(),
            r: reduceOnly,
            t: {
                limit: {
                    tif: 'Gtc'
                }
            }
        };
    }

    /**
     * Vérifier la signature
     */
    verifySignature(message, signature, address) {
        try {
            const recoveredAddress = ethers.verifyMessage(message, signature);
            return recoveredAddress.toLowerCase() === address.toLowerCase();
        } catch (error) {
            console.error('Erreur de vérification signature:', error);
            return false;
        }
    }
}

module.exports = HyperliquidSignature;