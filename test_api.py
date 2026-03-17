import requests
import json

# The URL of your local Safe-Surf AI server
API_URL = "http://127.0.0.1:5000/api/v1/scan"

# The target you want to analyze via the API
payload = {
    "url": "http://google.com"
}

print("🚀 INITIATING REMOTE API SCAN...")
print("-" * 40)

try:
    # Sending the POST request to your Flask API
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API STATUS: {data['status'].upper()}")
        print(f"👤 ARCHITECT: {data['architect']}")
        print(f"📊 VERDICT: {data['results']['verdict']}")
        print("\n🔍 FORENSIC DATA RECEIVED:")
        print(json.dumps(data['results']['forensics'], indent=4))
    else:
        print(f"❌ API ERROR: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ CONNECTION FAILED: {str(e)}")
    print("Ensure your Flask app is running on http://127.0.0.1:5000")