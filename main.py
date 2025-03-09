from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from utils.binance_utils import get_futures_balance, place_order

# Load environment variables from .env file
load_dotenv()

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

    # Expected JSON: {"symbol": "BTCUSDT", "side": "BUY" or "SELL"}
    symbol = data.get("symbol", "BTCUSDT")
    new_side = data.get("side", "BUY")

    # Get the current USDT futures balance
    futures_balance = get_futures_balance("USDT")
    
    # Close all open positions and then open a new one based on the signal
    order_results = place_order(symbol, new_side, futures_balance)

    return jsonify(order_results), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
