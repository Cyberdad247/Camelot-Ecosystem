// AGENCY WAR ROOM CONTROLLER [Ω_RECON v1.0]
// //THINK PROTOCOL FIX: All DOM access wrapped in DOMContentLoaded

document.addEventListener("DOMContentLoaded", () => {

    // 1. Command Palette Logic
    const btnDeploy = document.getElementById("btn-deploy");
    const qfocusInput = document.getElementById("qfocus");
    const statusEl = document.getElementById("status");
    const resultsContainer = document.getElementById("results-container");
    const resultsDisplay = document.getElementById("results-display");

    if (!btnDeploy || !qfocusInput) {
        console.error("[AGENCY] Critical UI elements missing. Cannot initialize.");
        return;
    }

    btnDeploy.addEventListener("click", () => {
        executeCommand();
    });

    qfocusInput.addEventListener("keypress", (e) => {
        if (e.key === 'Enter') executeCommand();
    });

    function executeCommand() {
        const qfocus = qfocusInput.value;
        if (!qfocus) return;

        // Detect Agent Call
        const agent = detectAgent(qfocus);
        updateAgentStatus(agent, "ACTIVE");

        statusEl.innerHTML = `[STATUS]: <b>${agent}</b> DEPLOYED`;
        resultsContainer.style.display = "none";
        
        chrome.runtime.sendMessage({
          action: "START_MISSION",
          qfocus: qfocus
        }, (response) => {
          if (response && response.status === "MISSION_STARTED") {
            // Animation effects could go here
          }
        });
    }

    function detectAgent(query) {
        const lower = query.toLowerCase();
        if (lower.includes("audit") || lower.includes("security")) return "SIR_ZENITH";
        if (lower.includes("deep dive") || lower.includes("crawl")) return "LADY_APIS";
        if (lower.includes("analyze ui") || lower.includes("screenshot")) return "LADY_EYE";
        return "SIR_ORACLE";
    }

    function updateAgentStatus(agent, status) {
        // Reset all
        document.querySelectorAll('.agent-card').forEach(el => el.classList.remove('active'));
        
        // Highlight active
        const card = document.getElementById(`card-${agent.toLowerCase()}`);
        if (card) card.classList.add('active');
    }

    // 2. Settings
    const btnSettings = document.getElementById("btn-settings");
    if (btnSettings) {
        btnSettings.addEventListener("click", () => {
            if (chrome.runtime.openOptionsPage) chrome.runtime.openOptionsPage();
            else window.open(chrome.runtime.getURL('options.html'));
        });
    }

    // 3. Broadcaster (The Hive Feed)
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === "INTEL_READY") {
        
        statusEl.innerText = "[STATUS]: MISSION COMPLETE";
        resultsContainer.style.display = "block";
        
        // Pretty Print JSON-LD or Markdown
        const content = request.intel.content;
        const textToRender = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
        
        // Typewriter Effect
        typewriterEffect(resultsDisplay, textToRender);
        
        // Update Roster to Idle
        document.querySelectorAll('.agent-card').forEach(el => el.classList.remove('active'));
      }
    });

    function typewriterEffect(element, text, speed = 5) {
        element.textContent = "";
        element.classList.add("typewriter-cursor");
        
        let i = 0;
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                // Speed up for long text
                const dynamicSpeed = text.length > 500 ? 1 : speed;
                setTimeout(type, dynamicSpeed);
            } else {
                element.classList.remove("typewriter-cursor");
            }
        }
        type();
    }


    // 4. Utility Buttons
    const btnCopy = document.getElementById("btn-copy");
    if (btnCopy) {
        btnCopy.addEventListener("click", () => {
            navigator.clipboard.writeText(resultsDisplay.textContent);
            btnCopy.innerText = "COPIED";
            setTimeout(() => btnCopy.innerText = "COPY INTEL", 2000);
        });
    }

    const btnSync = document.getElementById("btn-sync");
    if (btnSync) {
        btnSync.addEventListener("click", () => {
            btnSync.innerText = "SYNCING...";
            
            // Construct Intel Packet
            let intel;
            try {
                intel = {
                    agent: "AGENCY_SWARM",
                    content: JSON.parse(resultsDisplay.textContent || "{}"),
                    timestamp: new Date().toISOString()
                };
            } catch (e) {
                console.error("[AGENCY] Invalid JSON in results:", e);
                btnSync.innerText = "❌ PARSE ERR";
                return;
            }

            chrome.runtime.sendMessage({ action: "SYNC_INTEL", intel: intel }, (res) => {
                if (res && res.status === "SUCCESS") {
                    btnSync.innerText = "✅ VAULTED";
                    btnSync.classList.add('success');
                } else {
                    btnSync.innerText = "❌ FAILED";
                    btnSync.classList.add('error');
                }
                setTimeout(() => { 
                    btnSync.innerText = "VAULT SYNC"; 
                    btnSync.classList.remove('success', 'error'); 
                }, 3000);
            });
        });
    }

    console.log("[AGENCY] War Room initialized.");
});