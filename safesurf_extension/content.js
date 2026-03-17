// --- WEB INTERVENTION ENGINE ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "warn_user") {
        // Create the Forensic Warning Banner
        const alertBanner = document.createElement('div');
        alertBanner.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; 
            background: #ff4d4d; color: white; text-align: center; 
            padding: 20px; z-index: 999999; font-weight: bold;
            font-family: 'Segoe UI', sans-serif; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            border-bottom: 5px solid #800000;
        `;
        alertBanner.innerHTML = `
            <div style="font-size: 20px;">⚠️ SAFE-SURF AI: CRITICAL PHISHING THREAT DETECTED</div>
            <div style="font-size: 14px; margin-top: 5px;">
                Lead Architect Dikshant Sharma's AI Engine has flagged this URL as MALICIOUS. 
                Proceeding may result in credential theft.
            </div>
            <button id="closeSafeSurf" style="margin-top: 10px; padding: 5px 15px; cursor: pointer;">ACKNOWLEDGE RISK</button>
        `;
        document.body.prepend(alertBanner);

        document.getElementById('closeSafeSurf').onclick = () => alertBanner.remove();
    }
});