from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
ngrok_url = os.getenv("NGROK_URL")
expected_passphrase = os.getenv("TRADINGVIEW_PASSPHRASE")

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Webhook proxy server running"})

@app.route("/debug")
def debug():
    return jsonify({
        "status": "running",
        "working_directory": os.getcwd(),
        "env_file_exists": os.path.exists(".env")
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    # Ensure JSON payload exists
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Extract passphrase from the JSON body
    received_passphrase = data.get("TRADINGVIEW_PASSPHRASE")

    # Validate passphrase
    if received_passphrase != expected_passphrase:
        return jsonify({"error": "Unauthorized access"}), 401

    print("Received signal:", data)

    try:
        # Ensure ngrok_url points to the webhook endpoint
        webhook_url = ngrok_url if ngrok_url.endswith('/webhook') else f"{ngrok_url}/webhook"
        response = requests.post(webhook_url, json=data)
        
        print(f"Forwarding to: {webhook_url}")
        
        if response.status_code != 200:
            return jsonify({"error": "Local server error", "details": response.text}), response.status_code

        return jsonify({
            "status": "success",
            "local_response": response.json()
        }), 200
    except Exception as e:
        return jsonify({"error": "Request error", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
