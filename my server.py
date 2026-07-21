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
    pending_sms = None # Clear it so it doesn't send again
    return "OK", 200

# --- TESTING ENDPOINT ---
@app.route('/trigger', methods=['GET'])
def trigger_test():
    global pending_sms
    pending_sms = {
        "id": str(int(time.time())),
        "phoneNumber": "0771234567", # Change this to a real number for testing
        "message": "EMERGENCY: Elder needs help! Location: https://maps.google.com/?q=6.9271,79.8612"
    }
    return "<h1>Emergency Triggered!</h1><p>The Android app should react now.</p>", 200


if __name__ == '__main__':
    # Get Railway's dynamic PORT environment variable (default to 5000 if local)
    port = int(os.environ.get("PORT", 5000))
    
    print(f"\n[SERVER] Running on port {port}...")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
