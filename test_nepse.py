from app.providers.live_provider import LiveProvider
from app.providers.history_provider import HistoryProvider
import json

def test_live_data():
    print("Testing Live Provider...")
    provider = LiveProvider()
    
    # Test live price
    print("\n1. Getting live price for NABIL:")
    data = provider.get_live_price("NABIL")
    print(json.dumps(data, indent=2))
    
    # Test top gainers
    print("\n2. Getting top gainers:")
    gainers = provider.get_top_gainers(limit=5)
    print(json.dumps(gainers, indent=2))
    
    # Test market status
    print("\n3. Getting market status:")
    status = provider.get_market_status()
    print(json.dumps(status, indent=2))

def test_history_data():
    print("\nTesting History Provider...")
    provider = HistoryProvider()
    
    # Test historical data
    print("\n1. Getting historical data for NABIL (last 7 days):")
    data = provider.get_history("NABIL", days=7)
    print(json.dumps(data, indent=2))
    
    # Test company history
    print("\n2. Getting company history for NABIL:")
    history = provider.get_company_history("NABIL")
    print(json.dumps(history, indent=2))
    
    # Test market summary
    print("\n3. Getting market summary:")
    summary = provider.get_market_summary()
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    test_live_data()
    test_history_data()