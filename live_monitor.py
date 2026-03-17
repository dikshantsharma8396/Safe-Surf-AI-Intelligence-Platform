"""
SAFE-SURF AI | REAL-TIME THREAT MONITOR
Lead Architect: Dikshant Sharma
Features: Database Intelligence, Forensic Distribution Chart
"""

import sqlite3
import matplotlib.pyplot as plt
import os
from datetime import datetime

def generate_live_dashboard():
    print("🚀 [SAFE-SURF AI] Syncing with Intelligence Database...")
    
    # 1. Connect to your active database
    db_path = 'safesurf.db'
    if not os.path.exists(db_path):
        print(f"❌ Error: {db_path} not found. Ensure you are in the project root.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 2. Query Scanned Results
        # Note: We use 'LIKE' because your result strings are "SAFE ✅" or "PHISHING ⚠️"
        cursor.execute("SELECT result FROM search_history")
        rows = cursor.fetchall()
        
        if not rows:
            print("📭 Database is empty. Scan some URLs first!")
            return

        # 3. Process Data
        results = [row[0] for row in rows]
        safe_count = sum(1 for r in results if 'SAFE' in r)
        phish_count = sum(1 for r in results if 'PHISHING' in r)
        total = len(results)

        print(f"📊 Forensic Audit: {total} total scans | {safe_count} Safe | {phish_count} Phishing")

        # 4. Visualization (Cybersecurity Aesthetic)
        labels = [f'Safe ({safe_count})', f'Phishing ({phish_count})']
        sizes = [safe_count, phish_count]
        colors = ['#00f2fe', '#ff4d4d']  # Cyan for safe, Red for threat
        explode = (0.05, 0)  # Slightly pull out the safe slice

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=140,
                textprops={'color':"black", 'weight':'bold'})
        
        plt.title(f"SAFE-SURF AI: Live Threat Distribution\nTotal Nodes Analyzed: {total}", 
                  fontsize=14, fontweight='bold', pad=20)
        
        # 5. Export
        plt.savefig('live_threat_monitor.png', bbox_inches='tight')
        conn.close()
        print("📈 Dashboard Updated: 'live_threat_monitor.png' generated successfully.")

    except Exception as e:
        print(f"❌ Database Access Error: {str(e)}")

if __name__ == "__main__":
    generate_live_dashboard()