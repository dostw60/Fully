import pytest
from app.providers.live_provider import LiveProvider
from app.providers.history_provider import HistoryProvider

def test_live_provider()
    provider = LiveProvider()
    data = provider.get_live_price(NABIL)
    assert symbol in data
    assert price in data

def test_history_provider()
    provider = HistoryProvider()
    data = provider.get_history(NABIL, days=7)
    assert symbol in data
    assert data in data