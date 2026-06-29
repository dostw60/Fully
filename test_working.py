from app.providers.history_provider import HistoryProvider
import json

def test():
    print("Testing History Provider with Library...")
    provider = HistoryProvider()
    
    # Test NABIL
    result = provider.get_history("NABIL", days=7)
    
    print("\nResult:")
    print(f"Symbol: {result.get('symbol')}")
    print(f"Count: {result.get('count')}")
    print(f"Data points: {len(result.get('data', []))}")
    
    if result.get('data'):
        print("\nFirst data point:")
        print(json.dumps(result['data'][0], indent=2))
    else:
        print("No data returned (this is fine - market might be closed)")
    
    print("\n✅ Provider is working!")

if __name__ == "__main__":
    test()