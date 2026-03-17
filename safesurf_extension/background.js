/**
 * SAFE-SURF AI | BACKGROUND SENTINEL
 * Lead Architect: Dikshant Sharma
 * Version: 1.5 (Robust Redirect & Emoji Sync)
 */

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Initiate scan only when page load is complete and URL is valid
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        
        // Skip scanning the extension's own internal resources
        if (tab.url.includes(chrome.runtime.id)) return;

        console.log(`[Safe-Surf AI] DNA Audit: ${tab.url}`);

        chrome.storage.local.get(['researchMode'], function(pref) {
            
            fetch('http://127.0.0.1:5000/api/v1/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: tab.url })
            })
            .then(response => response.json())
            .then(data => {
                // FIXED: Use .includes() to handle "PHISHING ⚠️" vs "PHISHING"
                if (data.verdict && data.verdict.includes("PHISHING")) {
                    console.warn(`[Safe-Surf AI] THREAT DETECTED: ${tab.url}`);

                    // 1. Notification
                    chrome.notifications.create({
                        type: 'basic',
                        iconUrl: 'icon.png',
                        title: '🚨 PHISHING INTERCEPTED',
                        message: `Safe-Surf AI blocked: ${tab.url}`,
                        priority: 2
                    });

                    // 2. Conditional Redirect
                    if (!pref.researchMode) {
                        const blockedUrl = chrome.runtime.getURL("blocked.html");
                        chrome.tabs.update(tabId, { url: blockedUrl }, () => {
                            if (chrome.runtime.lastError) {
                                console.error("Redirect Failed:", chrome.runtime.lastError.message);
                            }
                        });
                    } else {
                        console.info("[Safe-Surf AI] Researcher Mode active. Redirect bypassed.");
                        chrome.tabs.sendMessage(tabId, { 
                            action: "warn_user",
                            verdict: data.verdict,
                            score: data.score
                        }).catch(() => console.log("Content script loading..."));
                    }
                    
                } else {
                    console.log(`[Safe-Surf AI] SAFE. DNA Score: ${data.score}%`);
                }
            })
            .catch(error => console.error('[Safe-Surf AI] Engine Offline.', error));
        });
    }
});