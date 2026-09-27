// 🛡️ CRYPTO UTILS (AES-GCM)
// Provides secure Export/Import capabilities for Profile Data

const CryptoUtils = {
  // Generate Key from Password
  async getKey(password) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      enc.encode(password),
      { name: 'PBKDF2' },
      false,
      ['deriveKey'],
    );
    return crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: enc.encode('NANO_SALT_v1'), // In prod, random salt stored with data
        iterations: 100000,
        hash: 'SHA-256',
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      true,
      ['encrypt', 'decrypt'],
    );
  },

  // Encrypt JSON Object
  async encryptData(dataObj, password) {
    const key = await this.getKey(password);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const enc = new TextEncoder();

    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: iv },
      key,
      enc.encode(JSON.stringify(dataObj)),
    );

    // Return as Base64 string: IV + Ciphertext
    const ivArr = Array.from(iv);
    const encArr = Array.from(new Uint8Array(encrypted));
    return btoa(String.fromCharCode(...ivArr.concat(encArr)));
  },

  // Decrypt Base64 String
  async decryptData(base64Str, password) {
    try {
      const key = await this.getKey(password);
      const str = atob(base64Str);
      const arr = new Uint8Array(str.length);
      for (let i = 0; i < str.length; i++) arr[i] = str.charCodeAt(i);

      const iv = arr.slice(0, 12);
      const data = arr.slice(12);

      const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: iv }, key, data);

      const dec = new TextDecoder();
      return JSON.parse(dec.decode(decrypted));
    } catch (e) {
      throw new Error('Decryption Failed. Wrong Password?');
    }
  },
};

self.CryptoUtils = CryptoUtils;
