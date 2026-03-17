"""
SAFE-SURF AI | CYBER SHIELD LABORATORY v4.6
Lead Architect: Dikshant Sharma
Features: Punycode Detection, Whitelist Hardening, & Network Bypass
"""

import re
import socket
import whois
import requests
from datetime import datetime, timezone
from urllib.parse import urlparse

# --- GLOBAL ARCHITECT CONFIG ---
TRUSTED_DOMAINS = [
    'google.com', 'docs.google.com', 'forms.gle', 'microsoft.com', 
    'apple.com', 'github.com', 'linkedin.com', 'twitter.com'
]

def expand_url(url):
    """Unrolls shortened URLs. Note: Skipped in training for speed."""
    try:
        # Use GET with stream=True for better expansion results than HEAD
        response = requests.get(url, allow_redirects=True, timeout=3, stream=True)
        return response.url
    except:
        return url

def extract_features(url, training_mode=False):
    """
    v4.6 DNA Extractor: Hardened against Punycode and Whitelist spoofing.
    """
    # 0. Pre-Processing: Expand only if NOT in training mode
    if not training_mode:
        url = expand_url(url)
        
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    parsed = urlparse(url)
    hostname = (parsed.hostname if parsed.hostname else "").lower()
    
    # Check for Lead Architect's Local Environment
    is_localhost = "127.0.0.1" in hostname or "localhost" in hostname
    
    # 0.1 NEW: Punycode (Homograph) Detection
    is_punycode = 1 if "xn--" in hostname else -1
    
    # 0.2 NEW: Hardened Whitelist (Ensures 'google.com.tk' is NOT whitelisted)
    is_whitelisted = any(hostname == domain or hostname.endswith('.' + domain) for domain in TRUSTED_DOMAINS)
    # Check if a burner TLD is attached at the end of a trusted name
    burner_tlds = ('.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.online', '.site')
    if any(hostname.endswith(tld) for tld in burner_tlds):
        is_whitelisted = False 

    # ==========================================
    # --- 1. STRUCTURAL DNA EXTRACTION ---
    # ==========================================
    ssl = 1 if parsed.scheme == 'https' else -1
    url_len = -1 if len(url) > 54 else 1
    have_at = -1 if '@' in url else 1
    
    is_ip = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname)
    have_ip = -1 if (is_ip and not is_localhost) else 1
    
    prefix_suffix = -1 if '-' in hostname else 1
    subdomain_depth = -1 if hostname.count('.') >= 4 else 1

    # ==========================================
    # --- 2. DEEP-CHECK (DOMAIN AGE) ---
    # ==========================================
    if training_mode or is_whitelisted or is_localhost:
        domain_age = 1 if (not is_ip or is_localhost) else -1
    else:
        try:
            domain_info = whois.whois(hostname)
            creation_date = domain_info.creation_date
            if isinstance(creation_date, list): creation_date = creation_date[0]
            
            if creation_date:
                age_days = (datetime.now() - creation_date.replace(tzinfo=None)).days
                domain_age = 1 if age_days > 180 else -1
            else:
                domain_age = -1
        except:
            domain_age = -1

    # ==========================================
    # --- 3. DNS RESOLUTION STATUS ---
    # ==========================================
    if training_mode or is_localhost:
        dns_valid = 1
    else:
        try:
            socket.gethostbyname(hostname)
            dns_valid = 1
        except:
            dns_valid = -1

    # ==========================================
    # --- 4. HEURISTIC SAFETY LAYER ---
    # ==========================================
    risk_words = ['bank', 'login', 'verify', 'account', 'update', 'credential', 'wallet']
    keyword_match = any(word in url.lower() for word in risk_words)
    
    zero_tolerance_keywords = ['phishing', 'malware', 'wicar.org', 'testphishing']
    zero_tolerance_match = any(word in url.lower() for word in zero_tolerance_keywords)

    tld_match = hostname.endswith(burner_tlds)

    free_cloud = ['herokuapp.com', 'netlify.app', 'vercel.app', 'github.io']
    is_cloud_hosted = any(hostname.endswith(cloud) for cloud in free_cloud)

    # Force Phish ONLY if NOT whitelisted and NOT localhost
    force_phish = False
    if not is_whitelisted and not is_localhost:
        force_phish = True if (
            (is_punycode == 1) or # <-- AUTO-BLOCK PUNYCODE
            (have_ip == -1) or 
            (ssl == -1 and keyword_match) or 
            (domain_age == -1 and dns_valid == -1) or 
            zero_tolerance_match or
            (tld_match and keyword_match) or 
            (is_cloud_hosted and keyword_match)
        ) else False
    
    f_signal = -1 if force_phish else 1

    # ==========================================
    # --- 5. ML VECTOR GENERATION ---
    # ==========================================
    # Added Punycode as the 10th feature
    extracted = [ssl, url_len, have_at, have_ip, prefix_suffix, domain_age, dns_valid, subdomain_depth, f_signal, is_punycode]
    features_list = extracted + [1] * (30 - len(extracted))

    # ==========================================
    # --- 6. RICH UI ANALYTICS ---
    # ==========================================
    analytics = {
        "Entity Trust Status": "Trusted Provider (Exempt) ✅" if is_whitelisted else ("Internal Node ✅" if is_localhost else "Standard Audit In-Progress"),
        "Protocol Security (SSL)": "Active HTTPS ✅" if ssl == 1 else "Insecure HTTP ⚠️",
        "Domain Age": "Established ✅" if domain_age == 1 else "New or Hidden ⚠️",
        "Targeted Keywords": "Clean ✅" if not keyword_match else "Suspicious Terms Found ⚠️",
        "Homograph Detection": "Safe DNA ✅" if is_punycode == -1 else "Punycode Spoof Detected ⚠️"
    }

    return [features_list], analytics, force_phish