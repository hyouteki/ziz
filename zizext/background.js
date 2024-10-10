let isMonitoring = false;
let tabSequence = [];
let tabHTMLCache = [];

// Initialize storage
chrome.storage.local.get(["tabSequence", "tabHTMLCache"], (result) => {
	tabSequence = result.tabSequence || [];
	tabHTMLCache = result.tabHTMLCache || [];
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
	if (request.action === "start") {
		startMonitoring();
	} else if (request.action === "pause") {
		pauseMonitoring();
	} else if (request.action === "stop") {
		stopMonitoring();
	} else if (request.action === "restart") {
		restartMonitoring();
	} else if (request.action === "getData") {
		sendResponse({ sequence: tabSequence, htmlContent: tabHTMLCache });
	}
	return true;
});

function startMonitoring() {
	if (isMonitoring) return;
	isMonitoring = true;
	chrome.storage.local.set({ monitoring: true });

	// Listen for new tab creation
	chrome.tabs.onCreated.addListener(handleTabCreated);
	// Listen for tab updates (URL changes)
	chrome.tabs.onUpdated.addListener(handleTabUpdated);
}

function pauseMonitoring() {
	if (!isMonitoring) return;
	isMonitoring = false;
	chrome.storage.local.set({ monitoring: false });
	// Remove listeners
	chrome.tabs.onCreated.removeListener(handleTabCreated);
	chrome.tabs.onUpdated.removeListener(handleTabUpdated);
}

function stopMonitoring() {
	pauseMonitoring();
	tabSequence = [];
	tabHTMLCache = [];
	chrome.storage.local.set({ tabSequence, tabHTMLCache });
}

function restartMonitoring() {
	pauseMonitoring();
	startMonitoring();
}

function handleTabCreated(tab) {
	if (!isMonitoring) return;
	const event = {
		type: "new_tab",
		tabId: tab.id,
		url: tab.url || "about:blank",
		timestamp: new Date().toISOString()
	};
	if (tab.url && tab.url !== "about:blank") {
		tabSequence.push(event);
		chrome.storage.local.set({ tabSequence });
		fetchTabHTML(tab.id, tab.url);
	}
}

function handleTabUpdated(tabId, changeInfo, tab) {
	if (!isMonitoring) return;
	if (changeInfo.url) {
		const event = {
			type: "url_change",
			tabId: tabId,
			url: changeInfo.url,
			timestamp: new Date().toISOString()
		};
		tabSequence.push(event);
		chrome.storage.local.set({ tabSequence });
		fetchTabHTML(tabId, changeInfo.url);
	}
}

function fetchTabHTML(tabId, url) {
	chrome.scripting.executeScript(
		{
			target: { tabId: tabId },
			func: () => document.documentElement.outerHTML
		},
		(results) => {
			if (chrome.runtime.lastError || !results || results.length === 0) {
				console.error(`Failed to get HTML for tab ${tabId}:`,
							  chrome.runtime.lastError);
				return;
			}
			const html = results[0].result;
			tabHTMLCache.push({ url, html, timestamp: new Date().toISOString() });
			chrome.storage.local.set({ tabHTMLCache });
		}
	);
}
