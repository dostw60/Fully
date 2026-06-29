from pydantic import BaseModel, Field
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