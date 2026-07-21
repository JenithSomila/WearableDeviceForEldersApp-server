from flask import Flask, request, jsonify
import socket
from zeroconf import ServiceInfo, Zeroconf
import time

app = Flask(__name__)

# Storage for the emergency trigger
pending_sms = None

# --- API ENDPOINTS FOR THE APP ---

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
# Open http://192.168.8.101:8080/trigger in your computer browser to test the app!
@app.route('/trigger', methods=['GET'])
def trigger_test():
    global pending_sms
    pending_sms = {
        "id": str(int(time.time())),
        "phoneNumber": "0771234567", # Change this to a real number for testing
        "message": "EMERGENCY: Elder needs help! Location: https://maps.google.com/?q=6.9271,79.8612"
    }
    return "<h1>Emergency Triggered!</h1><p>The Android app should react now.</p>", 200

# --- AUTO-DISCOVERY (NSD) ---
def start_mdns(ip):
    desc = {'path': '/'}
    info = ServiceInfo(
        "_eldercare._tcp.local.",
        "ElderCareServer._eldercare._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=8080,
        properties=desc,
        server="eldercare.local.",
    )
    zeroconf = Zeroconf()
    print(f"[NSD] Broadcasting service as 'ElderCareServer' on {ip}...")
    zeroconf.register_service(info)
    return zeroconf

if __name__ == '__main__':
    # Get your computer's IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Start the Auto-Discovery
    zc = start_mdns(local_ip)
    
    print(f"\n[SERVER] Running on http://{local_ip}:8080")
    print(f"[TEST] Open http://{local_ip}:8080/trigger to simulate an emergency.")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    finally:
        zc.close()