import os
import time
import socket
from flask import Flask, request, jsonify

app = Flask(__name__)

# Storage for the emergency trigger
pending_sms = None

# --- API ENDPOINTS FOR THE APP ---

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

# --- ESP32 TRIGGER ENDPOINT (UPDATED FOR POST & GET) ---
@app.route('/trigger', methods=['GET', 'POST'])
def trigger_test():
    global pending_sms
    
    # ESP32 එකෙන් JSON ඩේටා POST කරනකොට මේක ක්‍රියාත්මක වෙනවා
    if request.method == 'POST':
        data = request.get_json()
        if data:
            bpm = data.get('bpm')
            acc = data.get('acceleration')
            lat = data.get('lat')
            lng = data.get('lng')
            print(f"\n[ESP32 DATA RECEIVED] -> BPM: {bpm}, Acc: {acc}, Lat: {lat}, Lng: {lng}")
            
            # හදිසි තත්ත්වයක් නම් (ఉదా: BPM වැඩි නම් හෝ වැටීමක් වුණොත්) SMS එකක් ත්‍රීගර් කරන්න පුළුවන්
            if (bpm and bpm > 130) or (acc and acc > 20.0):
                pending_sms = {
                    "id": str(int(time.time())),
                    "phoneNumber": "0771234567",
                    "message": f"EMERGENCY! Elder needs help! Location: https://maps.google.com/?q={lat},{lng}"
                }
                print("[ALERT] Emergency condition met! SMS queued.")
                
        return jsonify({"status": "Success", "message": "Data received!"}), 200

    # බ්‍රව්සර් එකෙන් GET ඉල්ලීමක් කළොත් පරණ ටෙස්ට් පේජ් එක පෙන්වයි
    pending_sms = {
        "id": str(int(time.time())),
        "phoneNumber": "0771234567", 
        "message": "EMERGENCY: Elder needs help!"
    }
    return "<h1>Emergency Triggered via GET!</h1>", 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"\n[SERVER] Running on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
