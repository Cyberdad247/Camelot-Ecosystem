// SPDX-License-Identifier: MIT

// VERIFICATION SCRIPT: AGENT LOGIC & KINETIC HAND
// Mocks the DOM and Browser environment to test execute_navigator

// --- MOCKS ---
const mockElement = {
    click: () => console.log("  -> [MOCK] Element Clicked"),
    value: "",
    dispatchEvent: (e) => console.log(`  -> [MOCK] Event Dispatched: ${e.type}`),
    getBoundingClientRect: () => ({ top: 10, left: 10, width: 100, height: 100, bottom: 110, right: 110 })
};

global.window = {
    innerHeight: 1080,
    innerWidth: 1920,
    scrollBy: (opts) => console.log(`  -> [MOCK] Scrolled by ${opts.top}`),
    Kinetic: null // Will be assigned
};

global.document = {
    documentElement: { clientHeight: 1080, clientWidth: 1920 },
    querySelector: (sel) => sel === "#valid-btn" ? mockElement : null,
    body: { innerText: "Mock Page Content" }
};

global.Event = class Event { constructor(type) { this.type = type; } };

global.chrome = {
    runtime: {
        sendMessage: (msg) => console.log("  -> [MOCK] Message Sent:", msg)
    }
};

// --- IMPORT MODULES (Simulated by Copy/Paste for this environment) ---

// 1. Kinetic Module (from agent_hand.js)
const Kinetic = {
    click: (selector) => {
        const el = document.querySelector(selector);
        if (el) { // Visibility check simplified for mock
            console.log(`[HAND] Clicking: ${selector}`);
            el.click();
            return { status: "SUCCESS", action: "click", target: selector };
        }
        return { status: "FAILED", reason: "Element not found" };
    },
    type: (selector, text) => {
        const el = document.querySelector(selector);
        if (el) {
            console.log(`[HAND] Typing into: ${selector}`);
            el.value = text;
            el.dispatchEvent(new Event('input'));
            return { status: "SUCCESS", action: "type", target: selector };
        }
        return { status: "FAILED", reason: "Input not accessible" };
    }
};
global.window.Kinetic = Kinetic;

// 2. Navigator Logic (from content_sentry.js)
function execute_navigator(instructions) {
  console.log(`[NAVIGATOR] Executing: ${instructions.action}`);
  
  if (instructions.action === "CLICK") {
      const result = window.Kinetic.click(instructions.target);
      console.log(`[NAVIGATOR] Click Result:`, result);
  }
  
  if (instructions.action === "TYPE") {
      const result = window.Kinetic.type(instructions.target, instructions.text);
      console.log(`[NAVIGATOR] Type Result:`, result);
  }
}

// --- EXECUTION TESTS ---

console.log("--- TEST 1: VALID CLICK ---");
execute_navigator({ action: "CLICK", target: "#valid-btn" });

console.log("\n--- TEST 2: INVALID CLICK ---");
execute_navigator({ action: "CLICK", target: "#missing-btn" });

console.log("\n--- TEST 3: TYPE TEXT ---");
execute_navigator({ action: "TYPE", target: "#valid-btn", text: "Hello World" });
