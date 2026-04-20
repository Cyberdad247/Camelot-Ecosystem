// Ω_HAND: KINETIC ACTION MODULE
// Capabilities: Click, Type, Scroll

console.log("[Ω_HAND] Kinetic Systems Online.");

const Kinetic = {
    
    // 1. CLICK
    click: (selector) => {
        const el = document.querySelector(selector);
        if (el && isVisible(el)) {
            console.log(`[HAND] Clicking: ${selector}`);
            el.click();
            return { status: "SUCCESS", action: "click", target: selector };
        }
        return { status: "FAILED", reason: "Element not found or invisible" };
    },

    // 2. TYPE
    type: (selector, text) => {
        const el = document.querySelector(selector);
        if (el && isVisible(el)) {
            console.log(`[HAND] Typing into: ${selector}`);
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return { status: "SUCCESS", action: "type", target: selector };
        }
        return { status: "FAILED", reason: "Input not accessible" };
    },

    // 3. SCROLL
    scroll: (direction) => {
        const amount = direction === "down" ? window.innerHeight : -window.innerHeight;
        window.scrollBy({ top: amount, behavior: 'smooth' });
        return { status: "SUCCESS", action: "scroll" };
    },

    // 4. RIGHT CLICK
    rightClick: (selector) => {
        const el = document.querySelector(selector);
        if (el && isVisible(el)) {
             el.dispatchEvent(new MouseEvent('contextmenu', {
                 bubbles: true,
                 cancelable: true,
                 view: window,
                 buttons: 2
             }));
             return { status: "SUCCESS", action: "rightClick", target: selector };
        }
        return { status: "FAILED", reason: "Element not found" };
    },

    // 5. HOVER
    hover: (selector, duration = 1000) => {
        const el = document.querySelector(selector);
        if (el && isVisible(el)) {
            el.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
            el.dispatchEvent(new MouseEvent('mousemove', { bubbles: true }));
            // We can't blocking wait here easily without async, but simulation is fine.
            return { status: "SUCCESS", action: "hover", target: selector };
        }
        return { status: "FAILED", reason: "Element not found" };
    },

    // 6. DRAG (Simulation)
    drag: (fromSelector, toSelector) => {
        const src = document.querySelector(fromSelector);
        const dest = document.querySelector(toSelector);
        if (src && dest) {
            // Complex event chain
            src.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
            dest.dispatchEvent(new MouseEvent('mousemove', { bubbles: true }));
            dest.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
            return { status: "SUCCESS", action: "drag", from: fromSelector, to: toSelector };
        }
        return { status: "FAILED", reason: "Source or Dest not found" };
    },

    // 7. WAIT
    wait: (ms) => {
        return new Promise(resolve => setTimeout(() => {
            resolve({ status: "SUCCESS", action: "wait", duration: ms });
        }, ms));
    }

// Helper: Visibility Check
function isVisible(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) &&
        rect.width > 0 && 
        rect.height > 0
    );
}

// Export to Global Scope for Sentry
window.Kinetic = Kinetic;
