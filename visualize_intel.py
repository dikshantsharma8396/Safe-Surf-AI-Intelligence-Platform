"""
SAFE-SURF AI | INTELLIGENCE VISUALIZER
Lead Architect: Dikshant Sharma
Version: 4.2 (10-Feature DNA Mapping)
"""

import matplotlib.pyplot as plt
import pickle
import numpy as np
import os

def plot_importance():
    print("📈 [SAFE-SURF AI] Generating Feature Intelligence Chart...")
    
    # 1. Load the Intelligence Core
    model_path = "classifier.pkl"
    if not os.path.exists(model_path):
        print(f"❌ Error: {model_path} not found. Run train_engine.py first.")
        return

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    # 2. Architect's DNA Labels (Updated to 10 features to match features.py v4.6)
    labels = [
        "SSL/HTTPS", "URL Length", "@ Symbol", "IP Address", 
        "Pre-Suffix", "Domain Age", "DNS Status", "Sub-Depth", 
        "Heuristic", "Punycode"
    ]
    
    # 3. Extract Importances
    # We slice to 10 because our latest feature list has 10 active markers
    importances = model.feature_importances_[:10]
    indices = np.argsort(importances) # Sort for horizontal bar chart
    
    # 4. Cybersecurity Visualization Aesthetic
    plt.figure(figsize=(10, 7))
    plt.title("Safe-Surf AI: DNA Feature Importance (v4.2)", 
              fontsize=14, fontweight='bold', pad=20)
    
    # Using the signature cyan color from your UI
    plt.barh(range(len(indices)), importances[indices], color='#00f2fe', align='center')
    plt.yticks(range(len(indices)), [labels[i] for i in indices], fontweight='bold')
    
    plt.xlabel('Relative Intelligence Score', fontsize=10)
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    
    # 5. Export
    plt.savefig('dna_importance.png', dpi=300)
    print("✅ Success: 'dna_importance.png' updated with Punycode metrics.")

if __name__ == "__main__":
    plot_importance()