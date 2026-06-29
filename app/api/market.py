from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.services.market_service import MarketService
from datetime import datetime, timedelta

router = APIRouter(prefix="/market", tags=["market"])
market_service = MarketService()

@router.get("/live/{symbol}")
async def get_live_price(symbol: str):
    """Get current live price for a company"""
    try:
        data = market_service.get_live_data(symbol)
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        return data
    except Exception as e:
        print(f"Live endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{symbol}")
async def get_historical_data(
    symbol: str,
    days: Optional[int] = Query(30, ge=1, le=365)
):
    """Get historical data for a company"""
    try:
        data = market_service.get_historical_data(symbol, days)
        
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        
        # Ensure required fields exist
        data.setdefault("start_date", None)
        data.setdefault("end_date", None)
        data.setdefault("timestamp", datetime.now().isoformat())
        data.setdefault("data", [])
        data.setdefault("count", len(data.get("data", [])))
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        print(f"History endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{symbol}")
async def get_company_data(symbol: str):
    """Get both live and historical data for a company"""
    try:
        data = market_service.get_company_data(symbol)
        
        # Check for errors
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        
        # Ensure live data exists
        if "live" not in data or not data["live"]:
            data["live"] = {
                "symbol": symbol,
                "price": 0,
                "change": 0,
                "change_percent": 0,
                "volume": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ensure history data exists
        if "history" not in data or not data["history"]:
            data["history"] = {
                "symbol": symbol,
                "data": [],
                "count": 0,
                "start_date": None,
                "end_date": None,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Ensure history has all required fields
            history = data["history"]
            history.setdefault("start_date", None)
            history.setdefault("end_date", None)
            history.setdefault("timestamp", datetime.now().isoformat())
            history.setdefault("data", [])
            history.setdefault("count", len(history.get("data", [])))
            
            # Add OHLC data
            if history.get("data"):
                ohlc_data = []
                for item in history["data"]:
                    ohlc_data.append({
                        "date": item.get("date"),
                        "open": item.get("open", 0),
                        "high": item.get("high", 0),
                        "low": item.get("low", 0),
                        "close": item.get("close", 0),
                        "volume": item.get("volume", 0)
                    })
                history["ohlc"] = ohlc_data
        
        # Ensure timestamp exists
        data.setdefault("timestamp", datetime.now().isoformat())
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Company endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/summary")
async def get_market_summary():
    """Get market overview with top gainers/losers"""
    try:
        data = market_service.get_market_summary()
        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])
        
        data.setdefault("top_gainers", [])
        data.setdefault("top_losers", [])
        data.setdefault("market_status", {})
        data.setdefault("timestamp", datetime.now().isoformat())
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{symbol}")
async def get_company_profile(symbol: str):
    """Get comprehensive company profile"""
    try:
        data = market_service.get_company_full_profile(symbol)
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/depth/{symbol}")
async def get_market_depth(symbol: str):
    """Get market depth (order book) for a company"""
    try:
        data = market_service.get_market_depth(symbol)
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/floorsheet")
async def get_floorsheet(symbol: Optional[str] = None):
    """Get floorsheet data"""
    try:
        data = market_service.get_floorsheet(symbol)
        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_market_status():
    """Get current market status"""
    try:
        data = market_service.get_market_status()
        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-stocks")
async def get_all_stocks():
    """Get all stocks with live prices"""
    try:
        from app.providers.live_provider import LiveProvider
        provider = LiveProvider()
        stocks = provider.get_all_stocks()
        if not stocks:
            return {
                "count": 0,
                "stocks": [],
                "timestamp": datetime.now().isoformat(),
                "message": "No stocks available. Market might be closed or API is down."
            }
        return {
            "count": len(stocks),
            "stocks": stocks,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_stocks(query: str = Query(..., min_length=1)):
    """Search for stocks by symbol or name"""
    try:
        from app.providers.live_provider import LiveProvider
        provider = LiveProvider()
        results = provider.search_stocks(query)
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/{symbol}")
async def debug_stock_data(symbol: str):
    """Debug endpoint to see raw data for a symbol"""
    try:
        from app.providers.live_provider import LiveProvider
        provider = LiveProvider()
        
        stocks = provider.get_all_stocks()
        if "error" in stocks:
            return {"error": stocks["error"]}
        
        stock_data = None
        for stock in stocks:
            if stock.get('symbol') == symbol:
                stock_data = stock
                break
        
        security_id = provider._get_company_id(symbol)
        details = {}
        if security_id:
            try:
                details = provider.nepse.get_security_details(security_id)
            except Exception as e:
                details = {"error": str(e)}
        
        return {
            "symbol": symbol,
            "security_id": security_id,
            "raw_stock_data": stock_data,
            "security_details": details,
            "all_keys": list(stock_data.keys()) if stock_data else [],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today/{symbol}")
async def get_today_data(symbol: str):
    """Get today's data for a company"""
    try:
        from app.providers.live_provider import LiveProvider
        provider = LiveProvider()
        
        live_data = provider.get_live_price(symbol)
        if "error" in live_data:
            raise HTTPException(status_code=404, detail=live_data["error"])
        
        today = datetime.now().strftime("%Y-%m-%d")
        return {
            "symbol": symbol,
            "data": [{
                "date": today,
                "open": live_data.get("open", 0),
                "high": live_data.get("high", 0),
                "low": live_data.get("low", 0),
                "close": live_data.get("price", 0),
                "volume": live_data.get("volume", 0)
            }],
            "count": 1,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== OHLC ENDPOINTS ====================

@router.get("/ohlc/{symbol}")
async def get_ohlc_data(
    symbol: str,
    days: Optional[int] = Query(30, ge=1, le=365),
    period: Optional[str] = Query("1d", regex="^(1d|1w|1m|3m|6m|1y)$")
):
    """
    Get OHLC (Open, High, Low, Close) data for a company
    
    - **symbol**: Company symbol (e.g., NABIL, HHL)
    - **days**: Number of days of data (default: 30, max: 365)
    - **period**: Time period (1d, 1w, 1m, 3m, 6m, 1y)
    """
    try:
        # Get historical data
        data = market_service.get_historical_data(symbol, days)
        
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        
        # Format OHLC data
        ohlc_data = []
        for item in data.get("data", []):
            ohlc_data.append({
                "date": item.get("date"),
                "open": item.get("open", 0),
                "high": item.get("high", 0),
                "low": item.get("low", 0),
                "close": item.get("close", 0),
                "volume": item.get("volume", 0)
            })
        
        # Calculate additional statistics
        if ohlc_data:
            prices = [d["close"] for d in ohlc_data]
            highest = max(prices)
            lowest = min(prices)
            avg_price = sum(prices) / len(prices)
            current_price = prices[-1] if prices else 0
            price_change = current_price - prices[0] if prices else 0
            price_change_percent = (price_change / prices[0] * 100) if prices and prices[0] > 0 else 0
        else:
            highest = lowest = avg_price = current_price = price_change = price_change_percent = 0
        
        # Calculate simple moving averages
        def calculate_sma(data, window):
            if len(data) < window:
                return []
            sma = []
            for i in range(len(data)):
                if i < window - 1:
                    sma.append(None)
                else:
                    sma.append(round(sum(data[i-window+1:i+1]) / window, 2))
            return sma
        
        prices = [d["close"] for d in ohlc_data]
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)
        sma_200 = calculate_sma(prices, 200)
        
        return {
            "symbol": symbol,
            "period": period,
            "days": days,
            "data": ohlc_data,
            "count": len(ohlc_data),
            "statistics": {
                "current_price": round(current_price, 2),
                "highest": round(highest, 2),
                "lowest": round(lowest, 2),
                "avg_price": round(avg_price, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2)
            },
            "technical_indicators": {
                "sma_20": sma_20 if sma_20 else None,
                "sma_50": sma_50 if sma_50 else None,
                "sma_200": sma_200 if sma_200 else None
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"OHLC endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlc/batch")
async def get_batch_ohlc(
    symbols: str = Query(..., description="Comma-separated symbols (e.g., NABIL,HHL,NTC)"),
    days: Optional[int] = Query(30, ge=1, le=365)
):
    """
    Get OHLC data for multiple symbols in a single request
    
    - **symbols**: Comma-separated list of symbols
    - **days**: Number of days of data (default: 30)
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        results = {}
        
        for symbol in symbol_list:
            try:
                data = market_service.get_historical_data(symbol, days)
                if "error" not in data:
                    ohlc_data = []
                    for item in data.get("data", []):
                        ohlc_data.append({
                            "date": item.get("date"),
                            "open": item.get("open", 0),
                            "high": item.get("high", 0),
                            "low": item.get("low", 0),
                            "close": item.get("close", 0),
                            "volume": item.get("volume", 0)
                        })
                    
                    # Calculate current price
                    current_price = ohlc_data[-1]["close"] if ohlc_data else 0
                    
                    results[symbol] = {
                        "data": ohlc_data,
                        "count": len(ohlc_data),
                        "current_price": current_price,
                        "status": "success"
                    }
                else:
                    results[symbol] = {
                        "error": data.get("error", "No data available"),
                        "status": "error"
                    }
            except Exception as e:
                results[symbol] = {
                    "error": str(e),
                    "status": "error"
                }
        
        return {
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Batch OHLC endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlc/statistics/{symbol}")
async def get_ohlc_statistics(
    symbol: str,
    days: Optional[int] = Query(30, ge=1, le=365)
):
    """
    Get OHLC statistics for a company
    
    - **symbol**: Company symbol
    - **days**: Number of days of data (default: 30)
    """
    try:
        # Get OHLC data
        ohlc_response = await get_ohlc_data(symbol, days)
        
        if isinstance(ohlc_response, dict) and "detail" in ohlc_response:
            raise HTTPException(status_code=404, detail=ohlc_response["detail"])
        
        data = ohlc_response.get("data", [])
        
        if not data:
            return {
                "symbol": symbol,
                "error": "No data available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate advanced statistics
        closes = [d["close"] for d in data]
        highs = [d["high"] for d in data]
        lows = [d["low"] for d in data]
        volumes = [d["volume"] for d in data]
        
        # Daily returns
        daily_returns = []
        for i in range(1, len(closes)):
            returns = (closes[i] - closes[i-1]) / closes[i-1] * 100
            daily_returns.append(round(returns, 2))
        
        # Volatility (standard deviation of daily returns)
        volatility = round((sum((r - sum(daily_returns)/len(daily_returns))**2 for r in daily_returns) / len(daily_returns)) ** 0.5, 2) if daily_returns else 0
        
        # Average volume
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        
        return {
            "symbol": symbol,
            "statistics": {
                "total_days": len(data),
                "current_price": closes[-1] if closes else 0,
                "highest_price": max(highs) if highs else 0,
                "lowest_price": min(lows) if lows else 0,
                "avg_price": round(sum(closes) / len(closes), 2) if closes else 0,
                "avg_volume": round(avg_volume, 2),
                "volatility": volatility,
                "daily_returns": daily_returns,
                "best_day": max(daily_returns) if daily_returns else 0,
                "worst_day": min(daily_returns) if daily_returns else 0
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"OHLC statistics endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))