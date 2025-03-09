from binance.client import Client
import os

# Load Binance API credentials from environment variables
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def get_futures_balance(asset="USDT"):
    """
    Fetch your Binance Futures account balance for the given asset.
    """
    try:
        balances = client.futures_account_balance()
        for balance in balances:
            if balance["asset"] == asset:
                return float(balance["balance"])
        return 0.0
    except Exception as e:
        return {"error": str(e)}

def close_all_positions():
    """
    Closes all open positions across all symbols.
    For each open position, if the position amount is positive (long), submits a SELL market order to close.
    If negative (short), submits a BUY market order to close.
    Returns a dictionary with the results for each symbol.
    """
    results = {}
    try:
        # Get position information for all symbols (futures API without symbol returns all positions)
        positions = client.futures_position_information()
        for pos in positions:
            pos_amt = float(pos["positionAmt"])
            symbol = pos["symbol"]
            # Only consider positions with a non-zero amount
            if abs(pos_amt) > 0:
                if pos_amt > 0:
                    # Long position: close by selling
                    order = client.futures_create_order(
                        symbol=symbol,
                        side="SELL",
                        type="MARKET",
                        quantity=abs(pos_amt),
                        reduceOnly=True
                    )
                    results[symbol] = {"closed_long": order}
                elif pos_amt < 0:
                    # Short position: close by buying
                    order = client.futures_create_order(
                        symbol=symbol,
                        side="BUY",
                        type="MARKET",
                        quantity=abs(pos_amt),
                        reduceOnly=True
                    )
                    results[symbol] = {"closed_short": order}
        if not results:
            results = {"closed": "No open positions"}
        return results
    except Exception as e:
        return {"error": str(e)}

def place_order(symbol, new_side, futures_balance):
    """
    Closes all existing positions, then opens a new position for the given symbol based on the TradingView signal.
    
    Uses 10% of the USDT futures balance with 15× leverage:
      - Nominal order value = futures_balance * 0.10 * 15
      - Order quantity = (order value) / current market price
    
    Sets a stop-loss order:
      - For a long (BUY): stop loss is set below the entry price.
      - For a short (SELL): stop loss is set above the entry price.
    """
    results = {}
    
    # Close all open positions first
    results["close_all_positions"] = close_all_positions()
    
    try:
        # Get the current market price for the symbol
        price_info = client.futures_ticker_price(symbol=symbol)
        mark_price = float(price_info['price'])
        
        # Calculate nominal order value and order quantity
        order_value = futures_balance * 0.10 * 15  # USDT value at 15x leverage
        order_quantity = order_value / mark_price
        
        # Place the new market order based on the new TradingView signal
        market_order = client.futures_create_order(
            symbol=symbol,
            side=new_side,
            type="MARKET",
            quantity=order_quantity
        )
        results["market_order"] = market_order
        
        # Determine stop loss parameters based on new position direction
        if new_side.upper() == "BUY":
            # For a long position, stop loss is set below the entry price.
            stop_loss_price = mark_price - (mark_price / 15)
            stop_loss_side = "SELL"
        elif new_side.upper() == "SELL":
            # For a short position, stop loss is set above the entry price.
            stop_loss_price = mark_price + (mark_price / 15)
            stop_loss_side = "BUY"
        else:
            return {"error": "Invalid new_side provided"}
        
        # Place a STOP_MARKET order as the stop loss (reduceOnly ensures it only closes the position)
        stop_loss_order = client.futures_create_order(
            symbol=symbol,
            side=stop_loss_side,
            type="STOP_MARKET",
            quantity=order_quantity,
            stopPrice=round(stop_loss_price, 2),
            reduceOnly=True
        )
        results["stop_loss_order"] = stop_loss_order
        results["calculations"] = {
            "mark_price": mark_price,
            "order_value": order_value,
            "order_quantity": order_quantity,
            "stop_loss_price": stop_loss_price
        }
        return results
    except Exception as e:
        return {"error": str(e)}
