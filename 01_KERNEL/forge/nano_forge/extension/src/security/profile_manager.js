// SPDX-License-Identifier: MIT

// 🕵️ PROFILE MANAGER (Antidetect Engine)
// Manages: Identity Isolation, Fingerprint Spoofing, Device Emulation

const PROFILE_LIBRARY = {
    'default': {
        id: "default",
        name: "Default Agent (Windows)",
        type: "DESKTOP",
        userAgent: navigator.userAgent,
        screen: { width: 1920, height: 1080, availWidth: 1920, availHeight: 1040, colorDepth: 24, pixelDepth: 24 },
        canvasSeed: 0.0000001,
        webglVendor: "Google Inc. (NVIDIA)",
        webglRenderer: "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11)",
        timezone: "America/New_York",
        locale: "en-US",
        platform: "Win32"
    },
    'mobile_ios_17': {
        id: "mobile_ios_17",
        name: "Knight Alpha (iPhone 15)",
        type: "MOBILE",
        userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        screen: { width: 393, height: 852, availWidth: 393, availHeight: 852, colorDepth: 32, pixelDepth: 32 },
        canvasSeed: 0.0004123,
        webglVendor: "Apple Inc.",
        webglRenderer: "Apple GPU",
        timezone: "America/Los_Angeles",
        locale: "en-US",
        platform: "iPhone"
    },
    'desktop_macos': {
        id: "desktop_macos",
        name: "Knight Beta (MacOS)",
        type: "DESKTOP",
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        screen: { width: 2560, height: 1600, availWidth: 2560, availHeight: 1512, colorDepth: 30, pixelDepth: 30 },
        canvasSeed: 0.0009871,
        webglVendor: "Apple Inc.",
        webglRenderer: "Apple M2",
        timezone: "Europe/London",
        locale: "en-GB",
        platform: "MacIntel"
    }
};

class ProfileManager {
    constructor() {
        this.activeProfile = PROFILE_LIBRARY['default'];
        this.customProfiles = {};
    }

    async createProfile(name, type = "DESKTOP") {
        // If name is specific like "Mobile_Drone", use deterministic ID to reuse it/overwrite
        const id = (name === "Mobile_Drone") ? "mobile_drone_v1" : crypto.randomUUID();
        
        const profile = {
            id,
            name,
            type,
            userAgent: type === "MOBILE" 
                ? "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
                : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            screen: type === "MOBILE" ? { width: 390, height: 844 } : { width: 1920, height: 1080 },
            canvasSeed: Math.random() * 0.0001, // Renamed from canvasNoise
            audioNoise: Math.random() * 0.0001,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            locale: navigator.language
        };
        
        await chrome.storage.local.set({ [`profile_${id}`]: profile });
        return profile;
    }

    async loadProfile(id) {
        // 1. Save current session cookies to active profile before switching
        if (this.activeProfile.id !== "default") {
            await this.saveCookies(this.activeProfile.id);
        }

        // Check Library first, then Custom
        let profile = PROFILE_LIBRARY[id] || this.customProfiles[id];
        
        // If not found in memory, check storage
        if (!profile) {
            const stored = await chrome.storage.local.get(`profile_${id}`);
            profile = stored[`profile_${id}`];
        }

        if (profile) {
            this.activeProfile = profile;
            // Persist choice to Sync for Options Page
            await chrome.storage.sync.set({ stealthConfig: { activeProfile: id } });
            
            // 2. Restore cookies for new profile
            await this.restoreCookies(this.activeProfile.id);
            
            console.log(`[PROFILE] Switched to Identity: ${this.activeProfile.name}`);
            return true;
        }
        return false;
    }

    // Capture current browser cookies into the profile
    async saveCookies(profileId) {
        const cookies = await chrome.cookies.getAll({});
        await chrome.storage.local.set({ [`cookies_${profileId}`]: cookies });
        console.log(`[COOKIE_JAR] Saved ${cookies.length} cookies for ${profileId}`);
    }

    // Clear browser and inject profile cookies
    async restoreCookies(profileId) {
        // Clear all
        const current = await chrome.cookies.getAll({});
        for (const c of current) {
            await chrome.cookies.remove({ url: `http${c.secure ? 's' : ''}://${c.domain}${c.path}`, name: c.name });
        }

        // Restore
        const data = await chrome.storage.local.get(`cookies_${profileId}`);
        const cookies = data[`cookies_${profileId}`] || [];
        
        for (const c of cookies) {
            // Chrome API requires specific format for setting
            const newComp = {
                url: `http${c.secure ? 's' : ''}://${c.domain.startsWith('.') ? c.domain.substring(1) : c.domain}${c.path}`,
                name: c.name,
                value: c.value,
                domain: c.domain,
                path: c.path,
                secure: c.secure,
                httpOnly: c.httpOnly,
                expirationDate: c.expirationDate,
                storeId: c.storeId
            };
            try { await chrome.cookies.set(newComp); } catch(e) {}
        }
        console.log(`[COOKIE_JAR] Restored ${cookies.length} cookies for ${profileId}`);
    }

    // --- IMPORT / EXPORT (Team Security) ---
    
    async exportProfile(profileId, password) {
        // Gather Data: Config + Cookies
        const data = await chrome.storage.local.get([`profile_${profileId}`, `cookies_${profileId}`]);
        const exportBlob = {
            config: data[`profile_${profileId}`],
            cookies: data[`cookies_${profileId}`] || []
        };
        
        // Encrypt
        return await self.CryptoUtils.encryptData(exportBlob, password);
    }

    async importProfile(encryptedBlob, password) {
        try {
            const data = await self.CryptoUtils.decryptData(encryptedBlob, password);
            if (!data.config || !data.config.id) throw new Error("Invalid Profile Structure");
            
            // Re-ID to avoid collisions? Or overwrite? 
            // "Team Sync" implies overwrite. "Clone" implies new ID.
            // We'll use the ID from the blob to allow syncing.
            const id = data.config.id;
            
            await chrome.storage.local.set({
                [`profile_${id}`]: data.config,
                [`cookies_${id}`]: data.cookies
            });
            
            return { status: "SUCCESS", name: data.config.name, id: id };
        } catch (e) {
            return { status: "ERROR", msg: e.message };
        }
    }

    // Generates the injection script for the content layer
    getInjectionScript() {
        // This script runs in the MAIN world of the page to hook APIs
        return `
            (function() {
                const NOISE_CANVAS = ${this.activeProfile.canvasNoise};
                const NOISE_AUDIO = ${this.activeProfile.audioNoise};
                
                // 1. Canvas Fingerprint Spoofing
                const toDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    const ctx = this.getContext('2d');
                    if (ctx) {
                        // Add negligible noise to a pixel to alter hash
                        const verify = ctx.getImageData(0, 0, 1, 1);
                        // Only modify if not empty to avoid breaking functionality
                        if (verify.data[3] !== 0) {
                             ctx.fillStyle = \`rgba(0,0,0,\${NOISE_CANVAS})\`;
                             ctx.fillRect(0, 0, 1, 1);
                        }
                    }
                    return toDataURL.apply(this, arguments);
                };

                // 2. AudioContext Fingerprint Spoofing
                const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function(channel) {
                    const buffer = originalGetChannelData.apply(this, arguments);
                    for (let i = 0; i < buffer.length; i += 100) {
                        buffer[i] += NOISE_AUDIO; // Micro-noise
                    }
                    return buffer;
                };

                // 3. WebGL Parameter Spoofing
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    // UNMASKED_VENDOR_WEBGL
                    if (parameter === 37445) return "${this.activeProfile.webglVendor}";
                    // UNMASKED_RENDERER_WEBGL
                    if (parameter === 37446) return "${this.activeProfile.webglRenderer}";
                    return getParameter.apply(this, arguments);
                };
                
                // 4. Navigator Property Overrides
                Object.defineProperty(navigator, 'userAgent', { 
                    get: () => "${this.activeProfile.userAgent}" 
                });
                
                console.log("[Omega_STEALTH] Fingerprint Spoofing Active.");
            })();
        `;
    }
}

// Export singleton
const profileManager = new ProfileManager();
// Attach to global for Background.js usage
self.ProfileManager = profileManager;
