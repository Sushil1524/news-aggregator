import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional

def get_market_indices() -> List[Dict[str, Any]]:
    """
    Fetches current data for major Indian market indices.
    """
    indices = [
        {"symbol": "^NSEI", "name": "NIFTY 50"},
        {"symbol": "^BSESN", "name": "SENSEX"},
        {"symbol": "^NSEBANK", "name": "Nifty Bank"},
    ]
    
    results = []
    for index in indices:
        try:
            ticker = yf.Ticker(index["symbol"])
            # Get fast info first, fallback to history
            info = ticker.fast_info
            price = info.last_price
            prev_close = info.previous_close
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            
            results.append({
                "symbol": index["symbol"],
                "name": index["name"],
                "price": round(price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "isPositive": change >= 0
            })
        except Exception as e:
            print(f"Error fetching index {index['symbol']}: {e}")
            # Fallback mock data if API fails
            results.append({
                "symbol": index["symbol"],
                "name": index["name"],
                "price": 0.0,
                "change": 0.0,
                "changePercent": 0.0,
                "isPositive": True
            })
            
    return results

def get_stock_details(ticker_symbol: str) -> Dict[str, Any]:
    """
    Fetches detailed information and historical data for a stock.
    """
    try:
        if not ticker_symbol.endswith(".NS") and not ticker_symbol.endswith(".BO"):
            # Default to NSE if no suffix provided
            ticker_symbol += ".NS"
            
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        fast_info = ticker.fast_info
        
        # Get historical data for chart (1 month default)
        history = ticker.history(period="1mo")
        chart_data = []
        for date, row in history.iterrows():
            chart_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(row["Close"], 2)
            })
            
        current_price = fast_info.last_price
        prev_close = fast_info.previous_close
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100
        
        return {
            "symbol": ticker_symbol,
            "name": info.get("longName", ticker_symbol),
            "price": round(current_price, 2),
            "currency": info.get("currency", "INR"),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "isPositive": change >= 0,
            "previousClose": round(prev_close, 2),
            "open": round(fast_info.open, 2),
            "dayHigh": round(fast_info.day_high, 2),
            "dayLow": round(fast_info.day_low, 2),
            "marketCap": info.get("marketCap"),
            "peRatio": info.get("trailingPE"),
            "dividendYield": info.get("dividendYield"),
            "chartData": chart_data
        }
    except Exception as e:
        print(f"Error fetching stock {ticker_symbol}: {e}")
        return None

def search_stocks(query: str) -> List[Dict[str, Any]]:
    """
    Basic search for Indian stocks.
    Since yfinance doesn't have a robust search, we'll use a predefined list 
    or rely on frontend to pass valid tickers.
    For now, we return a filtered list of popular stocks.
    """
    popular_stocks = [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
        {"symbol": "INFY.NS", "name": "Infosys"},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
        {"symbol": "SBIN.NS", "name": "State Bank of India"},
        {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel"},
        {"symbol": "ITC.NS", "name": "ITC Ltd"},
        {"symbol": "TATAMOTORS.NS", "name": "Tata Motors"},
        {"symbol": "LT.NS", "name": "Larsen & Toubro"},
        {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance"},
        {"symbol": "MARUTI.NS", "name": "Maruti Suzuki"},
    ]
    
    if not query:
        return popular_stocks
        
    query = query.lower()
    return [
        s for s in popular_stocks 
        if query in s["symbol"].lower() or query in s["name"].lower()
    ]
