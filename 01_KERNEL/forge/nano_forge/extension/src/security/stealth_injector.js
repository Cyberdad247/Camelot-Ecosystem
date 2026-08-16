// SPDX-License-Identifier: MIT

// 🕵️ STEALTH INJECTOR (Content Script - Isolated World)
// Reads config and injects anti-detect script into Main World.

(async function () {
  try {
    // 1. Get Global Config from Storage
    const storage = await chrome.storage.local.get(null);
    // We might not have the full library in storage if it's hardcoded in JS.
    // So we will inject the library definitions directly into the page context.

    const scriptContent = `
        (function() {
            // --- EMBEDDED PROFILE LIBRARY ---
            const PROFILE_LIBRARY = {
                'default': {
                    screen: { width: 1920, height: 1080 },
                    canvasSeed: 0.0000001,
                    webglVendor: "Google Inc. (NVIDIA)",
                    webglRenderer: "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11)",
                    userAgent: navigator.userAgent
                },
                'mobile_ios_17': {
                    screen: { width: 393, height: 852 },
                    canvasSeed: 0.0004123,
                    webglVendor: "Apple Inc.",
                    webglRenderer: "Apple GPU",
                    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
                },
                'desktop_macos': {
                    screen: { width: 2560, height: 1600 },
                    canvasSeed: 0.0009871,
                    webglVendor: "Apple Inc.",
                    webglRenderer: "Apple M2",
                    userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            };

            // 1. Determine Identity (Knight Override vs Global)
            let activeId = sessionStorage.getItem('NANO_PROFILE_ID') || 'default';
            let profile = PROFILE_LIBRARY[activeId] || PROFILE_LIBRARY['default'];

            console.log("[Omega_STEALTH] Active Identity:", activeId);
            
            // 2. Apply Spoofer
            const NOISE_CANVAS = profile.canvasSeed || 0.0000001;
            const NOISE_AUDIO = 0.0000001;
            const VENDOR = profile.webglVendor;
            const RENDERER = profile.webglRenderer;
            const UA = profile.userAgent;

            // Canvas
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const ctx = this.getContext('2d');
                if (ctx) {
                    const verify = ctx.getImageData(0,0,1,1);
                    if (verify.data[3]!==0) {
                        ctx.fillStyle = \`rgba(0,0,0,\${NOISE_CANVAS})\`;
                        ctx.fillRect(0,0,1,1);
                    }
                }
                return toDataURL.apply(this, arguments);
            };

            // Audio
            try {
                const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function(channel) {
                    const buffer = originalGetChannelData.apply(this, arguments);
                    for(let i=0; i<buffer.length; i+=100) buffer[i]+=NOISE_AUDIO;
                    return buffer;
                };
            } catch(e) {}

            // WebGL
            try {
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return VENDOR;
                    if (parameter === 37446) return RENDERER;
                    return getParameter.apply(this, arguments);
                };
            } catch(e) {}

            // UserAgent (Navigator Props)
            try {
                Object.defineProperty(navigator, 'userAgent', { get: () => UA });
                if (UA.includes("iPhone")) {
                    Object.defineProperty(navigator, 'platform', { get: () => "iPhone" });
                    Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 5 });
                } else {
                    Object.defineProperty(navigator, 'platform', { get: () => "Win32" });
                }
            } catch(e) {}

        })();
        `;

    const script = document.createElement('script');
    script.textContent = scriptContent;
    (document.head || document.documentElement).appendChild(script);
    script.remove();
  } catch (e) {
    console.error('[STEALTH] Injection Failed:', e);
  }
})();
