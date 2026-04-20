/**
 * PHANTOM INJECTION: Rich Fingerprint Spoofing (v2.0)
 * Injected into every page context to override 20-50+ browser APIs
 * Based on Multi-Login anti-detect techniques
 */

(function () {
    'use strict';

    // Fingerprint config will be injected by Phantom Engine
    const FINGERPRINT = window.__PHANTOM_FINGERPRINT__ || {};

    console.log('[PHANTOM] Injection Active. Profile:', FINGERPRINT.id);

    // === 1. NAVIGATOR OVERRIDES ===
    if (FINGERPRINT.user_agent) {
        Object.defineProperty(navigator, 'userAgent', {
            get: () => FINGERPRINT.user_agent
        });
    }

    if (FINGERPRINT.platform) {
        Object.defineProperty(navigator, 'platform', {
            get: () => FINGERPRINT.platform
        });
    }

    if (FINGERPRINT.vendor) {
        Object.defineProperty(navigator, 'vendor', {
            get: () => FINGERPRINT.vendor
        });
    }

    if (FINGERPRINT.hardwareConcurrency) {
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => FINGERPRINT.hardwareConcurrency
        });
    }

    if (FINGERPRINT.deviceMemory) {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => FINGERPRINT.deviceMemory
        });
    }

    if (FINGERPRINT.languages) {
        Object.defineProperty(navigator, 'languages', {
            get: () => FINGERPRINT.languages
        });
    }

    if (FINGERPRINT.locale) {
        Object.defineProperty(navigator, 'language', {
            get: () => FINGERPRINT.locale
        });
    }

    if (FINGERPRINT.doNotTrack) {
        Object.defineProperty(navigator, 'doNotTrack', {
            get: () => FINGERPRINT.doNotTrack === 'null' ? null : FINGERPRINT.doNotTrack
        });
    }

    // === 2. SCREEN OVERRIDES ===
    if (FINGERPRINT.screen) {
        Object.defineProperty(window.screen, 'width', {
            get: () => FINGERPRINT.screen.width
        });
        Object.defineProperty(window.screen, 'height', {
            get: () => FINGERPRINT.screen.height
        });
        Object.defineProperty(window.screen, 'availWidth', {
            get: () => FINGERPRINT.screen.availWidth || FINGERPRINT.screen.width
        });
        Object.defineProperty(window.screen, 'availHeight', {
            get: () => FINGERPRINT.screen.availHeight || FINGERPRINT.screen.height - 40
        });
        Object.defineProperty(window.screen, 'colorDepth', {
            get: () => FINGERPRINT.screen.colorDepth || 24
        });
        Object.defineProperty(window.screen, 'pixelDepth', {
            get: () => FINGERPRINT.screen.pixelDepth || 24
        });
    }

    // === 3. WEBGL OVERRIDES ===
    if (FINGERPRINT.webgl) {
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function (parameter) {
            if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                return FINGERPRINT.webgl.vendor || FINGERPRINT.webgl.unmaskedVendor;
            }
            if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                return FINGERPRINT.webgl.renderer || FINGERPRINT.webgl.unmaskedRenderer;
            }
            return getParameter.call(this, parameter);
        };

        // WebGL2 support
        if (typeof WebGL2RenderingContext !== 'undefined') {
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function (parameter) {
                if (parameter === 37445) return FINGERPRINT.webgl.vendor || FINGERPRINT.webgl.unmaskedVendor;
                if (parameter === 37446) return FINGERPRINT.webgl.renderer || FINGERPRINT.webgl.unmaskedRenderer;
                return getParameter2.call(this, parameter);
            };
        }
    }

    // === 4. WEBRTC PROTECTION ===
    if (FINGERPRINT.webrtc && FINGERPRINT.webrtc.mode === 'disabled') {
        // Disable WebRTC entirely
        if (window.RTCPeerConnection) {
            window.RTCPeerConnection = undefined;
        }
        if (window.webkitRTCPeerConnection) {
            window.webkitRTCPeerConnection = undefined;
        }
        if (window.mozRTCPeerConnection) {
            window.mozRTCPeerConnection = undefined;
        }
    }

    // === 5. CANVAS FINGERPRINT NOISE ===
    if (FINGERPRINT.canvas && FINGERPRINT.canvas.enabled) {
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const originalToBlob = HTMLCanvasElement.prototype.toBlob;
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

        // Deterministic noise based on seed
        function applyCanvasNoise(imageData, seed) {
            if (!seed) return imageData;

            const data = imageData.data;
            const seedNum = parseInt(seed.substring(0, 8), 16);

            for (let i = 0; i < data.length; i += 4) {
                // Apply minimal noise (±1-2 per channel)
                const noise = ((seedNum + i) % 5) - 2;
                data[i] = Math.min(255, Math.max(0, data[i] + noise));
                data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + noise));
                data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + noise));
            }

            return imageData;
        }

        CanvasRenderingContext2D.prototype.getImageData = function (...args) {
            const imageData = originalGetImageData.apply(this, args);
            return applyCanvasNoise(imageData, FINGERPRINT.canvas.noiseSeed);
        };
    }

    // === 6. AUDIO CONTEXT NOISE ===
    if (FINGERPRINT.audioContext && FINGERPRINT.audioContext.enabled) {
        const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;

        if (OriginalAudioContext) {
            window.AudioContext = function () {
                const context = new OriginalAudioContext(...arguments);
                const originalCreateOscillator = context.createOscillator.bind(context);

                context.createOscillator = function () {
                    const oscillator = originalCreateOscillator();
                    const seedNum = parseInt(FINGERPRINT.audioContext.noiseSeed?.substring(0, 8) || '0', 16);
                    const noise = (seedNum % 100) / 100000; // Minimal frequency shift

                    const originalFrequency = Object.getOwnPropertyDescriptor(
                        OscillatorNode.prototype, 'frequency'
                    );

                    Object.defineProperty(oscillator, 'frequency', {
                        get: () => {
                            const freq = originalFrequency.get.call(oscillator);
                            freq.value += noise;
                            return freq;
                        }
                    });

                    return oscillator;
                };

                return context;
            };
        }
    }

    // === 7. GEOLOCATION ===
    if (FINGERPRINT.geolocation && navigator.geolocation) {
        const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;

        navigator.geolocation.getCurrentPosition = function (success, error, options) {
            const fakePosition = {
                coords: {
                    latitude: FINGERPRINT.geolocation.latitude,
                    longitude: FINGERPRINT.geolocation.longitude,
                    accuracy: FINGERPRINT.geolocation.accuracy || 100,
                    altitude: null,
                    altitudeAccuracy: null,
                    heading: null,
                    speed: null
                },
                timestamp: Date.now()
            };

            if (success) success(fakePosition);
        };
    }

    // === 8. TIMEZONE ===
    if (FINGERPRINT.timezone) {
        const originalDateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function (...args) {
            if (!args[1]) args[1] = {};
            if (!args[1].timeZone) args[1].timeZone = FINGERPRINT.timezone;
            return new originalDateTimeFormat(...args);
        };
    }

    // === 9. AUTOMATION DETECTION EVASION ===
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false
    });

    // Chrome detection evasion
    if (window.chrome) {
        Object.defineProperty(window.chrome, 'runtime', {
            get: () => undefined
        });
    }

    console.log('[PHANTOM] Fingerprint injection complete.');
})();
