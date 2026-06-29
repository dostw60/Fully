from pydantic import BaseModel
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
    turnover: Optional[float] = None
    transactions: Optional[int] = None
    company_name: Optional[str] = None
    sector: Optional[str] = None
    security_id: Optional[int] = None

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
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    timestamp: Optional[str] = None

class CompanyDataResponse(BaseModel):
    symbol: str
    live: LivePriceResponse
    history: HistoricalDataResponse
    timestamp: str

class MarketSummaryResponse(BaseModel):
    top_gainers: List[dict]
    top_losers: List[dict]
    market_status: Optional[dict] = None
    timestamp: str

class CompanyProfileResponse(BaseModel):
    symbol: str
    live_data: LivePriceResponse
    historical_data: HistoricalDataResponse
    timestamp: str
