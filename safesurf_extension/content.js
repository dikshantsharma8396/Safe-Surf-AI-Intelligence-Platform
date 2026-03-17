/**
 * SAFE-SURF AI | WEB INTERVENTION ENGINE
 * Lead Architect: Dikshant Sharma
 * Version: 1.6 (Cloud-Resilient Defense)
 */

// --- WEB INTERVENTION ENGINE ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "warn_user") {
        
        // Prevents duplicate banners if the user navigates within a malicious SPA
        if (document.getElementById('safeSurfAlertBanner')) return;

        // Create the Forensic Warning Banner
        const alertBanner = document.createElement('div');
        alertBanner.id = 'safeSurfAlertBanner'; // Added ID for lifecycle management
        alertBanner.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; 
            background: #ff4d4d; color: white; text-align: center; 
            padding: 20px; z-index: 2147483647; font-weight: bold;
            font-family: 'Segoe UI', sans-serif; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            border-bottom: 5px solid #800000;
        `;
        
        alertBanner.innerHTML = `
            <div style="font-size: 22px; letter-spacing: 1px;">⚠️ SAFE-SURF AI: CRITICAL PHISHING THREAT DETECTED</div>
            <div style="font-size: 15px; margin-top: 8px; opacity: 0.9;">
                Lead Architect Dikshant Sharma's Cloud AI Engine has flagged this URL as MALICIOUS. 
                This site matches known <b>DNA Fraud Patterns</b> (Punycode/Homograph attack detected).
            </div>
            <div style="margin-top: 15px;">
                <button id="closeSafeSurf" style="
                    background: white; color: #ff4d4d; border: none; 
                    padding: 8px 25px; cursor: pointer; font-weight: bold; 
                    border-radius: 4px; transition: 0.3s;
                ">ACKNOWLEDGE RISK & DISMISS</button>
            </div>
        `;

        // Using prepend to ensure it appears at the very top of the DOM
        document.body.prepend(alertBanner);

        // Logic to remove the banner upon acknowledgment
        document.getElementById('closeSafeSurf').onclick = () => {
            alertBanner.style.transition = "0.5s";
            alertBanner.style.opacity = "0";
            setTimeout(() => alertBanner.remove(), 500);
        };
    }
});