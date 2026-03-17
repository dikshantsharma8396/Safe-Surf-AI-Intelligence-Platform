/**
 * SAFE-SURF AI | POPUP INTERFACE LOGIC
 * Lead Architect: Dikshant Sharma
 * Version: 1.6 (Cloud-Synchronized & Forensic Export)
 */

document.addEventListener('DOMContentLoaded', function() {
    const verdictEl = document.getElementById('verdict');
    const scoreEl = document.getElementById('score');
    const detailsEl = document.getElementById('details');
    const researchToggle = document.getElementById('researchMode');
    const reportBtn = document.getElementById('reportBtn');
    const downloadBtn = document.getElementById('downloadPdf');

    // --- PRODUCTION CONFIGURATION ---
    // Swapping local laboratory IP for the Global Intelligence Hub
    const CLOUD_URL = "https://safe-surf-ai-intelligence-platform.onrender.com";

    // --- PHASE 1: PREFERENCE PERSISTENCE ---
    chrome.storage.local.get(['researchMode'], function(result) {
        researchToggle.checked = result.researchMode || false;
    });

    researchToggle.addEventListener('change', function() {
        chrome.storage.local.set({ researchMode: researchToggle.checked });
    });

    // --- PHASE 2: AUTOMATIC DNA SCAN (SILENT MODE) ---
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        if (!tabs[0]) return;
        let currentUrl = tabs[0].url;

        // Redirecting scan request to Render Cloud
        fetch(`${CLOUD_URL}/api/v1/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                url: currentUrl, 
                silent: true // Prevents double-logging in Search History
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                // Update UI DNA Markers
                verdictEl.innerText = data.verdict;
                verdictEl.style.color = data.verdict === "SAFE" ? "#00f2fe" : "#ff4d4d";
                scoreEl.innerText = data.score + "%";
                
                // Logic-driven status messages
                detailsEl.innerText = data.verdict === "SAFE" 
                    ? "Model matches safe DNA patterns." 
                    : "⚠️ High-risk markers identified.";

                // ENABLE FORENSIC EXPORT (v3.2 Forensic Engine)
                if (downloadBtn) {
                    downloadBtn.style.display = "block";
                    downloadBtn.onclick = () => {
                        // Bridge to Flask Forensic Engine on Render
                        const downloadUrl = `${CLOUD_URL}/download_report/${encodeURIComponent(currentUrl)}/${data.verdict}`;
                        chrome.tabs.create({ url: downloadUrl });
                    };
                }
            }
        })
        .catch(err => {
            verdictEl.innerText = "OFFLINE";
            detailsEl.innerText = "Intelligence Hub is waking up (Free Tier delay)...";
            console.error("Connection Error:", err);
        });
    });

    // --- PHASE 3: MANUAL THREAT REPORTING ---
    reportBtn?.addEventListener('click', () => {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            let currentUrl = tabs[0].url;
            fetch(`${CLOUD_URL}/report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `target_url=${encodeURIComponent(currentUrl)}&comment=Manual Sentinel Log`
            }).then(() => {
                reportBtn.innerText = "LOGGED ✅";
                setTimeout(() => { reportBtn.innerText = "REPORT THREAT TO ADMIN"; }, 2000);
            });
        });
    });
});