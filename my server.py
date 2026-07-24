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
    pending_sms = None  # Clear it so it doesn't send again
    return "OK", 200

# --- ESP32 TRIGGER ENDPOINT (FIXED!) ---
@app.route('/trigger', methods=['GET', 'POST'])
def trigger_test():
    global pending_sms
    
    # 1. ESP32 එකෙන් එවන GET Query Parameters ලබා ගැනීම
    status = request.args.get('status', 'EMERGENCY')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    maps_url = request.args.get('maps_url')

    # 2. Google Maps URL එක සෑදීම
    if lat and lng:
        final_maps_url = f"https://maps.google.com/?q=6.9271,79.8612{lat},{lng}"
    elif maps_url and maps_url != "No_GPS_Fix":
        final_maps_url = maps_url
    else:
        final_maps_url = "Location Not Available (No GPS Fix)"

    # 3. Emergency Message එක පිළියෙල කිරීම (Map Link එක සහිතව)
    emergency_message = f"EMERGENCY: Elder needs help! Location: {final_maps_url}"

    # 4. App එකට යැවීමට pending_sms එක set කිරීම
    pending_sms = {
        "id": str(int(time.time())),
        "phoneNumber": "0771234567",  # Change this to a real target number if needed
        "message": emergency_message
    }
    
    print(f"\n[TRIGGERED] New Emergency Alert Generated!")
    print(f"   - Message: {emergency_message}")

    return f"<h1>Emergency Triggered!</h1><p>Message: {emergency_message}</p>", 200


if __name__ == '__main__':
    # Get Railway's dynamic PORT environment variable (default to 5000 if local)
    port = int(os.environ.get("PORT", 5000))
    
    print(f"\n[SERVER] Running on port {port}...")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
