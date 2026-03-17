/**
 * SAFE-SURF AI | BACKGROUND SENTINEL
 * Lead Architect: Dikshant Sharma
 * Version: 1.6 (Cloud-Synchronized Deployment)
 */

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Initiate scan only when page load is complete and URL is valid
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        
        // Skip scanning the extension's own internal resources
        if (tab.url.includes(chrome.runtime.id)) return;

        // PRODUCTION CONFIGURATION: Pointing to the Global Intelligence Hub
        const CLOUD_API = "https://safe-surf-ai-intelligence-platform.onrender.com/api/v1/scan";

        console.log(`[Safe-Surf AI] Initiating Global DNA Audit: ${tab.url}`);

        chrome.storage.local.get(['researchMode'], function(pref) {
            
            fetch(CLOUD_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: tab.url })
            })
            .then(response => response.json())
            .then(data => {
                // FIXED: Handle "PHISHING ⚠️" vs "PHISHING" for consistent verdict matching
                if (data.verdict && data.verdict.includes("PHISHING")) {
                    console.warn(`[Safe-Surf AI] GLOBAL THREAT DETECTED: ${tab.url}`);

                    // 1. System-Level Notification
                    chrome.notifications.create({
                        type: 'basic',
                        iconUrl: 'icon.png',
                        title: '🚨 PHISHING INTERCEPTED',
                        message: `Safe-Surf AI blocked a high-risk URL: ${tab.url}`,
                        priority: 2
                    });

                    // 2. Conditional Intervention Logic
                    if (!pref.researchMode) {
                        // FULL LOCKDOWN: Hard-redirect to local safety warning page
                        const blockedUrl = chrome.runtime.getURL("blocked.html");
                        chrome.tabs.update(tabId, { url: blockedUrl }, () => {
                            if (chrome.runtime.lastError) {
                                console.error("Redirect Failed:", chrome.runtime.lastError.message);
                            }
                        });
                    } else {
                        // ADVISORY MODE: Inject warning banner via content.js v1.6
                        console.info("[Safe-Surf AI] Researcher Mode active. Injecting advisory banner.");
                        chrome.tabs.sendMessage(tabId, { 
                            action: "warn_user",
                            verdict: data.verdict,
                            score: data.score
                        }).catch(() => console.log("Waiting for content script to handshake..."));
                    }
                    
                } else {
                    console.log(`[Safe-Surf AI] VERDICT: SAFE. DNA Intelligence Score: ${data.score}%`);
                }
            })
            .catch(error => {
                console.error('[Safe-Surf AI] Intelligence Hub Connection Failed.', error);
                // Note: On Render Free Tier, this usually means the server is waking up
            });
        });
    }
});