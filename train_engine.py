"""
SAFE-SURF AI | INTELLIGENCE RETRAINING ENGINE
Lead Architect: Dikshant Sharma
Version: 4.2 (Punycode Feature Mapping & DNA Analysis)
"""

import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from features import extract_features 

def start_retraining():
    print("🚀 [SAFE-SURF AI] Initializing Retraining Engine v4.2...")
    
    # 1. Load Synthesized Data
    try:
        df = pd.read_csv("expanded_threat_intel.csv")
        print(f"📊 Loaded {len(df)} intelligence nodes.")
    except FileNotFoundError:
        print("❌ Error: 'expanded_threat_intel.csv' not found. Run generate_dataset.py first.")
        return

    # 2. DNA Extraction (Feature Mapping)
    print("🧬 Extracting DNA Features (v4.6 Feature Engine Active)...")
    X = []
    y = []
    
    for index, row in df.iterrows():
        # Passing training_mode=True to bypass network delays (WHOIS/DNS)
        features, _, _ = extract_features(row['url'], training_mode=True)
        X.append(features[0]) 
        y.append(row['label'])
        
        if index % 500 == 0 and index > 0:
            print(f"   > Processed {index} nodes...")

    X = np.array(X)
    y = np.array(y)

    # 3. Data Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Intelligence Synthesis
    print("🧠 Synthesizing Neural Connections (Random Forest | 150 Estimators)...")
    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)

    # 5. Validation
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"\n✅ [v4.2 BUILD SUCCESSFUL]")
    print(f"🎯 Model Accuracy: {accuracy * 100:.2f}%")
    print("-" * 40)
    print(classification_report(y_test, predictions))

    # 6. DNA Importance Analysis (Architect's Insight)
    print("\n🔍 [DNA FEATURE IMPORTANCE]")
    # Updated to 10 labels to perfectly match features.py v4.6
    feature_labels = [
        "SSL/HTTPS", "URL Length", "Has @ Symbol", "IP Address", 
        "Prefix-Suffix", "Domain Age", "DNS Valid", "Subdomain Depth", 
        "Heuristic Signal", "Punycode Detection"
    ]
    
    importances = model.feature_importances_
    # We now map the first 10 markers to include our new Homograph shield
    indices = np.argsort(importances[:10])[::-1]
    
    for f in range(len(indices)):
        print(f"{f + 1}. {feature_labels[indices[f]]}: {importances[indices[f]]:.4f}")

    # 7. Deploy
    with open("classifier.pkl", "wb") as f:
        pickle.dump(model, f)
    print("\n💾 Intelligence Core Exported: 'classifier.pkl' is now Punycode-hardened.")

if __name__ == "__main__":
    start_retraining()