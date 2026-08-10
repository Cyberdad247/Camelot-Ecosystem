// QERE background service worker — creates the "Extract to QERE" context
// menu item, and on click stores the selected text for the side panel to
// pick up. No network calls happen here; this is pure capture + handoff.

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'qere-extract',
    title: 'Extract to QERE',
    contexts: ['selection'],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== 'qere-extract' || !info.selectionText) return;

  await chrome.storage.local.set({
    pending_qere_prompt: info.selectionText,
    pending_qere_source_url: tab?.url ?? null,
  });

  if (tab?.windowId != null) {
    await chrome.sidePanel.open({ windowId: tab.windowId });
  }
});
