"""
SAFE-SURF AI | ADVERSARIAL DATA SYNTHESIZER
Lead Architect: Dikshant Sharma
Version: 4.3 (Punycode Injection & Chaos Upgrade)
"""

import pandas as pd
import random

def generate_punycode_spoof():
    """Generates synthetic Punycode strings common in phishing attacks."""
    spoofs = [
        'xn--80ak6aa92e', # spoof of apple.com
        'xn--gogle-p9a',  # spoof of google.com
        'xn--microsft-q6a',# spoof of microsoft.com
        'xn--instgram-49a',# spoof of instagram.com
        'xn--paypl-p9a',   # spoof of paypal.com
        'xn--facebok-80a'   # spoof of facebook.com
    ]
    return random.choice(spoofs) + random.choice(['.com', '.net', '.org', '.site'])

def generate_safe_surf_data(n=5000):
    data = []
    
    # --- DNA Components ---
    trusted_domains = ['google.com', 'microsoft.com', 'github.io', 'apple.com', 'linkedin.com', 'amazon.in', 'netflix.com']
    burner_tlds = ['.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.shop', '.info', '.site', '.online']
    risk_words = ['login', 'verify', 'bank', 'secure', 'update', 'account', 'credential', 'wallet', 'signin', 'billing']
    
    print(f"🧬 Injecting Punycode and Chaos into {n} nodes...")

    for i in range(n):
        # Inject 500 Punycode nodes (10% of total) to harden the model
        if i < 500:
            url = f"https://{generate_punycode_spoof()}/login-session"
            label = -1
        else:
            is_phishing = random.choice([True, False])
            
            if is_phishing:
                # --- MALICIOUS DNA ---
                protocol = 'https' if random.random() > 0.7 else 'http'
                domain_name = random.choice(risk_words) + "-" + str(random.randint(100, 999))
                tld = random.choice(burner_tlds)
                sub = random.choice(['secure', 'auth', 'login.microsoft', 'verify.account'])
                path = "/" + "/".join(random.sample(risk_words, 2)) if random.random() > 0.5 else "/auth"
                
                url = f"{protocol}://{sub}.{domain_name}{tld}{path}"
                label = -1
            else:
                # --- BENIGN DNA ---
                protocol = 'http' if random.random() > 0.9 else 'https'
                domain = random.choice(trusted_domains)
                slug = random.choice(['search', 'profile', 'docs', 'main', 'watch', 'shop', 'order'])
                
                if random.random() > 0.8:
                    domain = "my-" + domain

                url = f"{protocol}://{domain}/{slug}"
                label = 1
            
        data.append({"url": url, "label": label})
    
    # 3. Export Intelligence
    df = pd.DataFrame(data)
    # Shuffle to ensure Punycode nodes aren't all at the top (prevents training bias)
    df = df.sample(frac=1).reset_index(drop=True)
    df.to_csv("expanded_threat_intel.csv", index=False)
    
    print(f"✅ Intelligence Synthesis Complete: v4.3 Punycode-Hardened Dataset exported.")

if __name__ == "__main__":
    generate_safe_surf_data()