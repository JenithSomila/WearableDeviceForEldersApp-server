import os
import time
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging

app = Flask(__name__)

# Firebase Credentials File එක Load කිරීම
# Repo එකේ තියෙන JSON File එකේ නම මෙතනට දෙන්න
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Global Variables
device_fcm_token = None
target_phone_number = "0771234567"

@app.route('/', methods=['GET'])
def home():
    return "<h1>Elder Care Server with Firebase is Live! 🚀</h1>", 200

# App එකෙන් FCM Token එක ගන්න Endpoint එක
@app.route('/config', methods=['POST', 'GET'])
def receive_config():
    global device_fcm_token, target_phone_number
    target = request.args.get('target')
    fcm_token = request.args.get('fcm_token')
    
    if target:
        target_phone_number = target
    if fcm_token:
        device_fcm_token = fcm_token
        
    print(f"\n[CONFIG] Received - Target: {target_phone_number}, Token: {device_fcm_token}")
    return "OK", 200

# Notification එක Phone එකට යවන Function එක
def send_firebase_notification(maps_url):
    global device_fcm_token
    if not device_fcm_token:
        print("[FIREBASE ERROR] No Device FCM Token registered yet!")
        return False

    message = messaging.Message(
        notification=messaging.Notification(
            title="🚨 EMERGENCY SOS ALERT!",
            body=f"Elder Needs Help! Location: {maps_url}"
        ),
        token=device_fcm_token,
    )
    
    try:
        response = messaging.send(message)
        print(f"[FIREBASE SUCCESS] Notification sent: {response}")
        return True
    except Exception as e:
        print(f"[FIREBASE ERROR] Failed to send: {e}")
        return False

# ESP32 එකෙන් Trigger වෙන Endpoint එක
@app.route('/trigger', methods=['GET', 'POST'])
def trigger_test():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    maps_url = request.args.get('maps_url')

    if lat and lng:
        final_maps_url = f"https://maps.google.com/?q=6.9271,79.8612{lat},{lng}"
    elif maps_url and maps_url != "No_GPS_Fix":
        final_maps_url = maps_url
    else:
        final_maps_url = "Location Not Available (No GPS Fix)"

    # Notification එක යැවීම
    send_firebase_notification(final_maps_url)

    return f"<h1>Emergency Triggered!</h1><p>Location: {final_maps_url}</p>", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
