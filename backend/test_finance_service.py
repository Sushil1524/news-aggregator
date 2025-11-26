import asyncio
from app.services.finance_service import get_market_indices, get_stock_details, search_stocks

def test_finance():
    print("Testing Market Indices...")
    indices = get_market_indices()
    print(f"Indices: {indices}")
    
    print("\nTesting Stock Details (RELIANCE.NS)...")
    stock = get_stock_details("RELIANCE.NS")
    if stock:
        print(f"Stock Name: {stock['name']}")
        print(f"Price: {stock['price']}")
        print(f"Chart Data Points: {len(stock['chartData'])}")
    else:
        print("Failed to fetch stock details")

    print("\nTesting Search (TCS)...")
    results = search_stocks("TCS")
    print(f"Search Results: {results}")

if __name__ == "__main__":
    test_finance()
