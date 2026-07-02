// QERE side panel logic. Talks to the real Cybertronia Multivoice-Router
// (04_KINETIC/multivoice, orchestration/router.go) at ROUTER_URL — NOT the
// fictional api.cybertronia.internal endpoint. The router's real /intent
// contract is: POST with a raw text body (not JSON, not form-encoded);
// success is a single SSE-formatted event ("event: response\ndata: ...\n\n"),
// failure is a plain-text body with a non-200 status. Confirmed by directly
// running the Go server and curling both endpoints before writing this file.
//
// HTMX was in the original draft, but its default form-encoded POST doesn't
// match this raw-text-body contract — using plain fetch() here instead of
// vendoring a library only to bypass its core AJAX behavior.

// Default multivoice-router SSE bind address per 04_KINETIC/multivoice's own
// README (CAMELOT_MV_SSE, default :7680). If :7680 is occupied on your
// machine (Windows sometimes squats it with a system service — confirmed
// during development), start the router with CAMELOT_MV_SSE=:<port> and
// change this to match.
const ROUTER_URL = 'http://127.0.0.1:7680/intent';

const promptInput = document.getElementById('user-prompt-input');
const executeButton = document.getElementById('execute-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const terminalOutput = document.getElementById('terminal-output');

function applyQERERefinement(rawText) {
  return `[QERE-PROTOCOL: ACTIVE]
[QUERY-INTENT]: Analyze, restructure, and optimize the following data extraction.
[EXTRACT-PAYLOAD]:
"""
${rawText}
"""
[REFINE-DIRECTIVES]:
- Distill into core operational logic.
- Remove redundant syntax.
[EXECUTE]: Awaiting Multivoice-Router dispatch...`;
}

function loadPendingExtraction() {
  chrome.storage.local.get('pending_qere_prompt', (data) => {
    if (!data.pending_qere_prompt) return;
    promptInput.value = applyQERERefinement(data.pending_qere_prompt);
    chrome.storage.local.remove('pending_qere_prompt');
  });
}

// Pick up an extraction already sitting in storage when the panel opens
// (the background worker writes it, then opens the panel — there's a real
// race between that write and this script attaching its listener).
document.addEventListener('DOMContentLoaded', loadPendingExtraction);

// Pick up any extraction that arrives while the panel is already open.
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.pending_qere_prompt?.newValue) {
    promptInput.value = applyQERERefinement(changes.pending_qere_prompt.newValue);
    chrome.storage.local.remove('pending_qere_prompt');
  }
});

// Parse the router's SSE-formatted single-event success response:
// "event: response\ndata: <payload>\n\n" -> "<payload>"
function parseSseResponse(text) {
  const match = text.match(/^data:\s?(.*)$/m);
  return match ? match[1] : text;
}

async function executeQerePipeline() {
  const payload = promptInput.value.trim();
  if (!payload) return;

  executeButton.disabled = true;
  loadingIndicator.classList.add('active');

  try {
    const res = await fetch(ROUTER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: payload,
    });
    const body = await res.text();

    if (res.ok) {
      terminalOutput.textContent = parseSseResponse(body);
    } else {
      const err = document.createElement('span');
      err.className = 'err';
      err.textContent = `[ROUTER ERROR ${res.status}] ${body}`;
      terminalOutput.textContent = '';
      terminalOutput.appendChild(err);
    }
  } catch (e) {
    const err = document.createElement('span');
    err.className = 'err';
    err.textContent = `[UNREACHABLE] Could not reach ${ROUTER_URL} — is the multivoice-router running? (${e.message})`;
    terminalOutput.textContent = '';
    terminalOutput.appendChild(err);
  } finally {
    executeButton.disabled = false;
    loadingIndicator.classList.remove('active');
  }
}

executeButton.addEventListener('click', executeQerePipeline);
