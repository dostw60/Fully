from typing import Dict, Optional, List
from app.providers.live_provider import LiveProvider
from app.providers.history_provider import HistoryProvider
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MarketService:
    """Combined market service that orchestrates live and historical data"""
    
    def __init__(self):
        self.live_provider = LiveProvider()
        self.history_provider = HistoryProvider()
    
    def get_company_data(self, symbol: str) -> Dict:
        """Get both live and historical data for a company"""
        try:
            live_data = self.live_provider.get_live_price(symbol)
            history_data = self.history_provider.get_history(symbol)
            
            if "error" in history_data:
                history_data = {
                    "symbol": symbol,
                    "data": [],
                    "count": 0,
                    "start_date": None,
                    "end_date": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            history_data.setdefault("start_date", None)
            history_data.setdefault("end_date", None)
            history_data.setdefault("timestamp", datetime.now().isoformat())
            history_data.setdefault("data", [])
            history_data.setdefault("count", len(history_data.get("data", [])))
            
            return {
                "symbol": symbol,
                "live": live_data,
                "history": history_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching company data for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}
    
    def get_live_data(self, symbol: str) -> Dict:
        """Get only live data"""
        return self.live_provider.get_live_price(symbol)
    
    def get_historical_data(self, symbol: str, days: int = 30) -> Dict:
        """Get only historical data"""
        result = self.history_provider.get_history(symbol, days)
        if "error" not in result:
            result.setdefault("start_date", None)
            result.setdefault("end_date", None)
            result.setdefault("timestamp", datetime.now().isoformat())
            result.setdefault("data", [])
            result.setdefault("count", len(result.get("data", [])))
        return result
    
    def get_market_summary(self) -> Dict:
        """Get market overview with top gainers/losers"""
        try:
            gainers = self.live_provider.get_top_gainers(limit=10)
            losers = self.live_provider.get_top_losers(limit=10)
            status = self.live_provider.get_market_status()
            
            return {
                "top_gainers": gainers if gainers else [],
                "top_losers": losers if losers else [],
                "market_status": status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching market summary: {e}")
            return {"error": str(e)}
    
    def get_company_full_profile(self, symbol: str) -> Dict:
        """Get comprehensive company profile combining all data sources"""
        try:
            live = self.live_provider.get_live_price(symbol)
            history = self.history_provider.get_history(symbol, days=90)
            
            if "error" in history:
                history = {
                    "symbol": symbol,
                    "data": [],
                    "count": 0,
                    "start_date": None,
                    "end_date": None,
                    "timestamp": datetime.now().isoformat()
                }
            
            history.setdefault("start_date", None)
            history.setdefault("end_date", None)
            history.setdefault("timestamp", datetime.now().isoformat())
            history.setdefault("data", [])
            history.setdefault("count", len(history.get("data", [])))
            
            return {
                "symbol": symbol,
                "live_data": live,
                "historical_data": history,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_market_depth(self, symbol: str) -> Dict:
        """Get market depth for a company"""
        try:
            return self.live_provider.get_market_depth(symbol)
        except Exception as e:
            logger.error(f"Error fetching market depth for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_floorsheet(self, symbol: Optional[str] = None) -> Dict:
        """Get floorsheet data"""
        try:
            return self.live_provider.get_floorsheet(symbol)
        except Exception as e:
            logger.error(f"Error fetching floorsheet: {e}")
            return {"error": str(e)}
    
    def get_market_status(self) -> Dict:
        """Get current market status"""
        try:
            return self.live_provider.get_market_status()
        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return {"error": str(e)}
    
    def get_all_stocks(self) -> List[Dict]:
        """Get all stocks with live data"""
        try:
            return self.live_provider.get_all_stocks()
        except Exception as e:
            logger.error(f"Error fetching all stocks: {e}")
            return []
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by name or symbol"""
        try:
            return self.live_provider.search_stocks(query)
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []