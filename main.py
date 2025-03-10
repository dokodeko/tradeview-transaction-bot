from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
from utils.binance_utils import get_futures_balance, place_order

# Load environment variables from .env file
load_dotenv()

# Configure your local ngrok URL
ngrok_url = os.getenv("NGROK_URL")    

app = Flask(__name__)

@app.route("/")
def index():
    # Display the current USDT futures balance
    futures_balance = get_futures_balance("USDT")
    return jsonify({
        "message": "TradingView Webhook Listener is Running!",
        "futures_balance": futures_balance
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Print received data for debugging
    print("Received webhook data:", data)

    try:
        # Forward the data to your local ngrok server
        response = requests.post(ngrok_url, json=data)
        print(f"Forwarded to local server. Response: {response.status_code}")


        if response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "Local server returned an error"
            }), response.status_code

        return jsonify({
            "status": "success",
            "message": "Signal forwarded to local server",
            "local_response": response.json()
        }), 200
    except Exception as e:
        print(f"Error forwarding to local server: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to forward signal: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)