/**
 * SAFE-SURF AI | POPUP INTERFACE LOGIC
 * Lead Architect: Dikshant Sharma
 * Version: 1.5 (Silent Scan & Forensic Export)
 */

document.addEventListener('DOMContentLoaded', function() {
    const verdictEl = document.getElementById('verdict');
    const scoreEl = document.getElementById('score');
    const detailsEl = document.getElementById('details');
    const researchToggle = document.getElementById('researchMode');
    const reportBtn = document.getElementById('reportBtn');
    const downloadBtn = document.getElementById('downloadPdf'); // Ensure this ID exists in popup.html

    // --- PHASE 1: PREFERENCE PERSISTENCE ---
    chrome.storage.local.get(['researchMode'], function(result) {
        researchToggle.checked = result.researchMode || false;
    });

    researchToggle.addEventListener('change', function() {
        chrome.storage.local.set({ researchMode: researchToggle.checked });
    });

    // --- PHASE 2: AUTOMATIC DNA SCAN (SILENT MODE) ---
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        let currentUrl = tabs[0].url;

        fetch('http://127.0.0.1:5000/api/v1/scan', {
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
                // Update UI
                verdictEl.innerText = data.verdict;
                verdictEl.style.color = data.verdict === "SAFE" ? "#00f2fe" : "#ff4d4d";
                scoreEl.innerText = data.score + "%";
                detailsEl.innerText = data.verdict === "SAFE" 
                    ? "Model matches safe DNA patterns." 
                    : "⚠️ High-risk markers identified.";

                // ENABLE FORENSIC EXPORT
                if (downloadBtn) {
                    downloadBtn.style.display = "block";
                    downloadBtn.onclick = () => {
                        // Bridge to Flask Forensic Engine
                        const downloadUrl = `http://127.0.0.1:5000/download_report/${encodeURIComponent(currentUrl)}/${data.verdict}`;
                        chrome.tabs.create({ url: downloadUrl });
                    };
                }
            }
        })
        .catch(err => {
            verdictEl.innerText = "OFFLINE";
            detailsEl.innerText = "Check Lead Architect's Flask server status.";
        });
    });

    // --- PHASE 3: MANUAL THREAT REPORTING ---
    reportBtn?.addEventListener('click', () => {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            let currentUrl = tabs[0].url;
            fetch('http://127.0.0.1:5000/report', {
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