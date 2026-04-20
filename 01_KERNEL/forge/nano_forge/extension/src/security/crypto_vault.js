/**
 * CRYPTO VAULT
 * AES-GCM Encryption for Sovereign Data
 */

const ALGO = { name: 'AES-GCM', length: 256 };

export class CryptoVault {
    constructor() {
        this.key = null;
    }

    // Initialize or load master key
    async init() {
        const stored = await chrome.storage.local.get('master_key_jwk');
        if (stored.master_key_jwk) {
            this.key = await crypto.subtle.importKey(
                'jwk', 
                stored.master_key_jwk, 
                ALGO, 
                true, 
                ['encrypt', 'decrypt']
            );
        } else {
            this.key = await crypto.subtle.generateKey(ALGO, true, ['encrypt', 'decrypt']);
            const jwk = await crypto.subtle.exportKey('jwk', this.key);
            await chrome.storage.local.set({ master_key_jwk: jwk });
        }
    }

    async encrypt(data) {
        if (!this.key) await this.init();
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const encoded = new TextEncoder().encode(JSON.stringify(data));
        
        const encrypted = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: iv }, 
            this.key, 
            encoded
        );

        // Pack IV + Ciphertext
        return {
            iv: Array.from(iv),
            content: Array.from(new Uint8Array(encrypted))
        };
    }

    async decrypt(packed) {
        if (!this.key) await this.init();
        const iv = new Uint8Array(packed.iv);
        const data = new Uint8Array(packed.content);

        const decrypted = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: iv }, 
            this.key, 
            data
        );

        const decoded = new TextDecoder().decode(decrypted);
        return JSON.parse(decoded);
    }
}
