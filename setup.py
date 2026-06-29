import os

# Create all directories
directories = [
    'app',
    'app/api',
    'app/providers',
    'app/services',
    'app/schemas'
]

for dir_name in directories:
    os.makedirs(dir_name, exist_ok=True)
    # Create __init__.py in each directory
    init_file = os.path.join(dir_name, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass

# Create schemas/market.py
with open('app/schemas/market.py', 'w') as f:
    f.write('''from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LivePriceResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    prev_close: Optional[float] = None

class HistoricalDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class HistoricalDataResponse(BaseModel):
    symbol: str
    data: List[HistoricalDataPoint]
    count: int
    start_date: str
    end_date: str

class CompanyDataResponse(BaseModel):
    symbol: str
    live: LivePriceResponse
    history: HistoricalDataResponse
    timestamp: str

class MarketSummaryResponse(BaseModel):
    top_gainers: List[dict]
    top_losers: List[dict]
    timestamp: str

class CompanyProfileResponse(BaseModel):
    symbol: str
    live_data: dict
    historical_data: dict
    company_info: dict
    timestamp: str
''')

# Create providers/live_provider.py
with open('app/providers/live_provider.py', 'w') as f:
    f.write('''import httpx
from typing import Dict, List, Optional
from datetime import datetime

class LiveProvider:
    """Provider for real-time data using NepseAPI-Unofficial"""
    
    def __init__(self):
        self.base_url = "https://nepseapi-production.up.railway.app/api"
        self.client = httpx.Client(timeout=10.0)
    
    def get_live_price(self, symbol: str) -> Dict:
        """Get current live price for a company"""
        try:
            response = self.client.get(f"{self.base_url}/live/{symbol}")
            response.raise_for_status()
            data = response.json()
            
            return {
                "symbol": data.get("symbol", symbol),
                "price": float(data.get("ltp", 0)),
                "change": float(data.get("change", 0)),
                "change_percent": float(data.get("change_percent", 0)),
                "volume": int(data.get("volume", 0)),
                "timestamp": datetime.now().isoformat(),
                "open": float(data.get("open", 0)),
                "high": float(data.get("high", 0)),
                "low": float(data.get("low", 0)),
                "prev_close": float(data.get("previous_close", 0))
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def get_market_depth(self, symbol: str) -> Dict:
        """Get market depth (buy/sell orders)"""
        try:
            response = self.client.get(f"{self.base_url}/depth/{symbol}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_top_gainers(self) -> List[Dict]:
        """Get top gainers of the day"""
        try:
            response = self.client.get(f"{self.base_url}/market/top-gainers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_top_losers(self) -> List[Dict]:
        """Get top losers of the day"""
        try:
            response = self.client.get(f"{self.base_url}/market/top-losers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_floorsheet(self, date: Optional[str] = None) -> Dict:
        """Get floorsheet data"""
        try:
            url = f"{self.base_url}/floorsheet"
            if date:
                url += f"?date={date}"
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
''')

# Create providers/history_provider.py
with open('app/providers/history_provider.py', 'w') as f:
    f.write('''import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta

class HistoryProvider:
    """Provider for historical data using nepse_data_api"""
    
    def __init__(self):
        self.base_url = "https://nepse-data-api.onrender.com/api"
        self.client = httpx.Client(timeout=15.0)
    
    def get_history(self, symbol: str, days: int = 30) -> Dict:
        """Get historical data for a company"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            response = self.client.get(
                f"{self.base_url}/history/{symbol}",
                params={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "symbol": symbol,
                "data": data.get("data", []),
                "count": len(data.get("data", [])),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def get_ohlc(self, symbol: str, period: str = "1d") -> Dict:
        """Get OHLC (Open, High, Low, Close) data"""
        try:
            response = self.client.get(
                f"{self.base_url}/ohlc/{symbol}",
                params={"period": period}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_company_history(self, company_name: str) -> Dict:
        """Get full company history including fundamentals"""
        try:
            response = self.client.get(f"{self.base_url}/company/{company_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
''')

# Create services/market_service.py
with open('app/services/market_service.py', 'w') as f:
    f.write('''from typing import Dict
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
        return self.history_provider.get_history(symbol, days)
    
    def get_market_summary(self) -> Dict:
        """Get market overview with top gainers/losers"""
        try:
            gainers = self.live_provider.get_top_gainers()
            losers = self.live_provider.get_top_losers()
            
            return {
                "top_gainers": gainers[:10],
                "top_losers": losers[:10],
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
            company_info = self.history_provider.get_company_history(symbol)
            
            return {
                "symbol": symbol,
                "live_data": live,
                "historical_data": history,
                "company_info": company_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {e}")
            return {"error": str(e)}
''')

# Create api/market.py
with open('app/api/market.py', 'w') as f:
    f.write('''from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.market_service import MarketService
from app.schemas.market import (
    LivePriceResponse,
    HistoricalDataResponse,
    CompanyDataResponse,
    MarketSummaryResponse,
    CompanyProfileResponse
)

router = APIRouter(prefix="/market", tags=["market"])
market_service = MarketService()

@router.get("/live/{symbol}", response_model=LivePriceResponse)
async def get_live_price(symbol: str):
    """Get current live price for a company"""
    data = market_service.get_live_data(symbol)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@router.get("/history/{symbol}", response_model=HistoricalDataResponse)
async def get_historical_data(
    symbol: str,
    days: Optional[int] = Query(30, ge=1, le=365)
):
    """Get historical data for a company"""
    data = market_service.get_historical_data(symbol, days)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@router.get("/company/{symbol}", response_model=CompanyDataResponse)
async def get_company_data(symbol: str):
    """Get both live and historical data for a company"""
    data = market_service.get_company_data(symbol)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@router.get("/summary", response_model=MarketSummaryResponse)
async def get_market_summary():
    """Get market overview with top gainers/losers"""
    data = market_service.get_market_summary()
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@router.get("/profile/{symbol}", response_model=CompanyProfileResponse)
async def get_company_profile(symbol: str):
    """Get comprehensive company profile"""
    data = market_service.get_company_full_profile(symbol)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data
''')

print("✅ All files created successfully!")
print("Now run: uvicorn app.main:app --reload")