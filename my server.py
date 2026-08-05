import os
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Global storage for emergency triggers and latest health data
pending_sms = None
latest_health_data = {
    "bpm": 0,
    "acceleration": 0.0,
    "lat": 0.0,
    "lng": 0.0,
    "status": "Normal"
}

# --- API ENDPOINTS ---

@app.route('/', methods=['GET'])
def home():
    return "<h1>Elder Care Server is Live! 🚀</h1>", 200

@app.route('/config', methods=['POST'])
def receive_config():
    sim = request.args.get('sim')
    target = request.args.get('target')
    print(f"\n[CONFIG] Received from App:")
    print(f"   - Band SIM: {sim}")
    print(f"   - Target Phone: {target}")
    return "OK", 200

@app.route('/get_pending_sms', methods=['GET'])
def get_sms():
    global pending_sms
    if pending_sms:
        print(f"[POLLING] App requested SMS. Sending: {pending_sms['id']}")
        return jsonify(pending_sms)
    return "null", 200

@app.route('/confirm_sms', methods=['POST'])
def confirm_sms():
    global pending_sms
    sms_id = request.args.get('id')
    print(f"[SUCCESS] App confirmed SMS {sms_id} was sent to the elder!")
    pending_sms = None 
    return "OK", 200

# --- ESP32 TRIGGER ENDPOINT (Receives Health Data) ---
@app.route('/trigger', methods=['GET', 'POST'])
def trigger_test():
    global pending_sms, latest_health_data
    
    if request.method == 'POST':
        data = request.get_json()
        if data:
            bpm = data.get('bpm', 0)
            acc = data.get('acceleration', 0.0)
            lat = data.get('lat', 0.0)
            lng = data.get('lng', 0.0)
            
            # Status එක තීරණය කිරීම
            status = "Normal"
            if bpm > 130 or (bpm < 40 and bpm != 0):
                status = "Abnormal Heart Rate!"
            elif acc > 20.0:
                status = "Fall Detected!"

            # ඩේටා ටික ග්ලෝබල් වේරියබල් එකේ සේව් කරගන්නවා (ඇප් එකට ඉල්ලනකොට දෙන්න)
            latest_health_data = {
                "bpm": bpm,
                "acceleration": acc,
                "lat": lat,
                "lng": lng,
                "status": status
            }
            
            print(f"\n[ESP32 DATA] -> BPM: {bpm}, Acc: {acc}, Status: {status}")
            
            # හදිසි තත්ත්වයක් නම් SMS එකක් ත්‍රීගර් කරන්න
            if status != "Normal":
                pending_sms = {
                    "id": str(int(time.time())),
                    "phoneNumber": "0771234567",
                    "message": f"EMERGENCY! {status} Location: https://maps.google.com/?q={lat},{lng}"
                }
                print("[ALERT] Emergency condition met! SMS queued.")
                
        return jsonify({"status": "Success", "message": "Data received!"}), 200

    return "<h1>Trigger Endpoint Active via GET</h1>", 200

# --- ANDROID APP HEALTH DATA ENDPOINT ---
@app.route('/get_health', methods=['GET'])
def get_health():
    global latest_health_data
    return jsonify(latest_health_data), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"\n[SERVER] Running on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
