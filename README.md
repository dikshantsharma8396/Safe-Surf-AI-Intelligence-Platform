# 🛡️ SAFE-SURF AI | Threat Intelligence & Forensic Platform
**Lead Architect:** Dikshant Sharma

SAFE-SURF AI is a professional-grade, ML-driven cybersecurity platform designed to identify and neutralize advanced phishing threats, including **Homograph (Punycode) attacks** that are invisible to the human eye.

## 🚀 Key Technical Innovations

### 1. Homograph Sentinel (v4.6 DNA Extractor)
Unlike standard scanners, this platform detects Punycode spoofing (e.g., `xn--pple-43d.com` rendered as `apple.com`). By analyzing the ASCII signature of every URL, the AI identifies character-spoofing attacks with zero-tolerance precision.

### 2. Random Forest Intelligence Core
The system uses a Random Forest Classifier trained on **5,000 adversarial nodes**. I engineered the dataset with "Noise Injection" to ensure the AI remains resilient even against phishing sites using valid SSL certificates or trusted cloud hosting providers.

### 3. Forensic Audit Reporting (v3.2)
Every scan generates a detailed **Forensic Audit PDF**. These reports provide:
- **DNA Statistical Breakdown**: A deep-dive into the URL's safety markers.
- **Unique Ref IDs**: AI-verified digital signatures for traceability.
- **Security Advisories**: Dynamic prevention tips based on the detected threat level.

### 4. Admin Threat Matrix
A headless, real-time analytics dashboard that visualizes global threat distribution and detection timelines using memory-buffered Matplotlib rendering.

## 🛠️ Project Ecosystem
- **The Brain**: Flask-based Intelligence API (Python, Scikit-Learn, Pandas).
- **The Shield**: Real-time Chrome Extension for passive user protection.
- **The Lab**: Synthetic data generators and retraining engines for constant evolution.

## 📦 Installation
Please refer to the [SETUP.txt](SETUP.txt) file for detailed instructions on loading the Chrome extension and connecting to the Intelligence Core.
