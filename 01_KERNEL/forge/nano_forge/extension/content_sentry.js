// Ω_NANO_COUNCIL (v1.2.0)
// Runs in the context of the web page.

console.log("[NANO_SWARM] Agents Online. Version 1.2.0");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.target === "NAVIGATOR") {
    execute_navigator(request.instructions);
  }
  if (request.target === "SENTRY" && request.action === "HIGHLIGHT_SOURCE") {
      const el = document.querySelector(`[data-nano-id="${request.id}"]`);
      if (el) {
          el.scrollIntoView({behavior: "smooth", block: "center"});
          el.style.outline = "3px solid cyan";
          el.style.backgroundColor = "rgba(0, 255, 255, 0.2)";
          setTimeout(() => {
              el.style.outline = "";
              el.style.backgroundColor = "";
          }, 3000);
          console.log(`[SENTRY] Highlighted Source #${request.id}`);
      } else {
          console.warn(`[SENTRY] Source #${request.id} not found.`);
      }
  }
});

// --- AGENT: LADY APIS (The Forager) ---
// High-Velocity DOM Foraging + Renormalization
function lady_apis_forage() {
    console.log("[LADY APIS] Ingesting DOM...");
    const raw_text = document.body.innerText;
    
    // Triple-QFT Renormalization (Mock)
    // 1. Discard Fluff
    // 2. Quantize Relevant Operators
    return raw_text.substring(0, 5000); // Performance Tuning: Cap at 5k chars for Edge
}

// --- AGENT: SIR ZENITH (The Shield) ---
// Security & Dependency Audit
function sir_zenith_scan(text) {
  console.log("[SIR ZENITH] Scanning for Injection Vectors...");
  
  // 1. Spotlighting: Wrap untrusted content
  let safe_text = `<<<UNTRUSTED_ZONE_START>>>\n${text}\n<<<UNTRUSTED_ZONE_END>>>`;
  
  // 2. Adversarial Filtering (Regex)
  const injection_patterns = [
    /ignore previous instructions/i,
    /system override/i,
    /you are now/i,
    /<script>/i // Basic XSS check
  ];
  
  injection_patterns.forEach(pattern => {
    if (pattern.test(safe_text)) {
      console.warn(`[SIR ZENITH] Threat Detected: ${pattern}`);
      safe_text = safe_text.replace(pattern, "[REDACTED_THREAT]");
    }
  });
  
  return safe_text;
}

// --- AGENT: NAVIGATOR (The Orchestrator on Page) ---
function execute_navigator(instructions) {
  console.log(`[NAVIGATOR] Executing: ${instructions.action}`);
  
  if (instructions.action === "ANALYZE_PAGE") {
    // 1. Forage (Apis)
    const raw_data = lady_apis_forage();

    // 2. Secure (Zenith)
    const clean_text = sir_zenith_scan(raw_data);
    
    // 3. Report back to Merlin
    chrome.runtime.sendMessage({
      action: "REPORT_INTEL",
      agent: "NAVIGATOR",
      data: clean_text
    });
  }

  // --- NEW: KINETIC ACTIONS ---
  if (instructions.action === "CLICK") {
      const result = window.Kinetic.click(instructions.target);
      console.log(`[NAVIGATOR] Click Result:`, result);
  }
  
  if (instructions.action === "TYPE") {
      const result = window.Kinetic.type(instructions.target, instructions.text);
      console.log(`[NAVIGATOR] Type Result:`, result);
  }
}
