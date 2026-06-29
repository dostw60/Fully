from nepse_data_api import Nepse
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LiveProvider:
    """Provider for real-time data using nepse_data_api library"""
    
    def __init__(self):
        self.nepse = Nepse(cache_ttl=30, enable_cache=True)
        self._company_map = None
        self._symbol_map = None
        self._company_list = None
        self._stock_cache = None
        self._stock_cache_time = None
    
    def _build_maps(self):
        """Build symbol to ID mapping"""
        try:
            companies = self.nepse.get_company_list()
            self._company_list = companies
            
            self._company_map = {}
            self._symbol_map = {}
            
            for comp in companies:
                symbol = comp.get('symbol')
                comp_id = comp.get('id')
                
                if symbol and comp_id:
                    self._company_map[symbol] = comp_id
                    self._symbol_map[symbol.upper()] = symbol
                    
                    clean_symbol = symbol.replace('-', '').replace('.', '')
                    if clean_symbol != symbol:
                        self._symbol_map[clean_symbol.upper()] = symbol
            
            logger.info(f"Built maps with {len(self._company_map)} companies")
            return True
        except Exception as e:
            logger.error(f"Error building maps: {e}")
            self._company_map = {}
            self._symbol_map = {}
            return False
    
    def _get_symbol(self, input_symbol: str) -> Optional[str]:
        """Get the correct symbol from case-insensitive input"""
        if self._symbol_map is None:
            self._build_maps()
        
        if not self._symbol_map:
            return None
        
        if input_symbol in self._company_map:
            return input_symbol
        
        upper_symbol = input_symbol.upper()
        if upper_symbol in self._symbol_map:
            return self._symbol_map[upper_symbol]
        
        return None
    
    def _get_company_id(self, symbol: str) -> Optional[int]:
        """Get security ID for a company symbol"""
        if self._company_map is None:
            success = self._build_maps()
            if not success:
                return None
        
        correct_symbol = self._get_symbol(symbol)
        if not correct_symbol:
            if self._company_list:
                for comp in self._company_list:
                    if comp.get('symbol', '').upper() == symbol.upper():
                        return comp.get('id')
            return None
        
        return self._company_map.get(correct_symbol)
    
    def _get_stocks_with_cache(self):
        """Get stocks with caching to avoid repeated API calls"""
        if self._stock_cache and self._stock_cache_time:
            if (datetime.now() - self._stock_cache_time).seconds < 30:
                return self._stock_cache
        
        try:
            stocks = self.nepse.get_stocks()
            self._stock_cache = stocks
            self._stock_cache_time = datetime.now()
            return stocks
        except Exception as e:
            logger.error(f"Error fetching stocks: {e}")
            return []
    
    def get_live_price(self, symbol: str) -> Dict:
        """Get current live price for a company"""
        try:
            security_id = self._get_company_id(symbol)
            if not security_id:
                return {"error": f"Symbol {symbol} not found", "symbol": symbol}
            
            stocks = self._get_stocks_with_cache()
            
            stock_data = None
            for stock in stocks:
                if stock.get('symbol') == symbol:
                    stock_data = stock
                    break
            
            if not stock_data:
                return {"error": f"Symbol {symbol} not found in stocks", "symbol": symbol}
            
            details = {}
            try:
                details = self.nepse.get_security_details(security_id)
            except Exception as e:
                logger.warning(f"Could not get security details: {e}")
            
            daily_trade = details.get('securityDailyTradeDto', {}) if details else {}
            security_info = details.get('security', {}) if details else {}
            
            return {
                "symbol": symbol,
                "security_id": security_id,
                "price": float(stock_data.get('lastTradedPrice', 0)),
                "change": float(stock_data.get('change', 0)),
                "change_percent": float(stock_data.get('percentageChange', 0)),
                "volume": int(stock_data.get('totalTradeQuantity', 0)),
                "timestamp": datetime.now().isoformat(),
                "open": float(stock_data.get('openPrice', 0)),
                "high": float(stock_data.get('highPrice', 0)),
                "low": float(stock_data.get('lowPrice', 0)),
                "prev_close": float(stock_data.get('previousClose', 0)),
                "turnover": float(stock_data.get('totalTradeValue', 0)),
                "transactions": int(daily_trade.get('totalTrades', 0)),
                "company_name": stock_data.get('securityName', ''),
                "sector": security_info.get('sector', ''),
                "isin": security_info.get('isin', ''),
                "face_value": security_info.get('faceValue', 0),
                "52_week_high": daily_trade.get('fiftyTwoWeekHigh', 0),
                "52_week_low": daily_trade.get('fiftyTwoWeekLow', 0),
                "last_updated": stock_data.get('lastUpdatedDateTime', '')
            }
        except Exception as e:
            logger.error(f"Error fetching live price for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}
    
    def get_market_depth(self, symbol: str) -> Dict:
        """Get market depth (buy/sell orders)"""
        try:
            correct_symbol = self._get_symbol(symbol)
            if not correct_symbol:
                return {"error": f"Symbol {symbol} not found"}
            
            depth_data = self.nepse.get_market_depth(symbol=correct_symbol)
            return {
                "symbol": correct_symbol,
                "depth": depth_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching market depth for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """Get top gainers of the day"""
        try:
            gainers = self.nepse.get_top_gainers(limit=limit)
            if gainers and isinstance(gainers, list) and len(gainers) > 0:
                return gainers
            
            # Fallback: calculate from stocks
            stocks = self._get_stocks_with_cache()
            if stocks:
                sorted_stocks = sorted(
                    [s for s in stocks if s.get('percentageChange', 0) > 0],
                    key=lambda x: x.get('percentageChange', 0),
                    reverse=True
                )
                return sorted_stocks[:limit]
            return []
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            # Fallback: calculate from stocks
            try:
                stocks = self._get_stocks_with_cache()
                if stocks:
                    sorted_stocks = sorted(
                        [s for s in stocks if s.get('percentageChange', 0) > 0],
                        key=lambda x: x.get('percentageChange', 0),
                        reverse=True
                    )
                    return sorted_stocks[:limit]
            except:
                pass
            return []
    
    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        """Get top losers of the day"""
        try:
            losers = self.nepse.get_top_losers(limit=limit)
            if losers and isinstance(losers, list) and len(losers) > 0:
                return losers
            
            # Fallback: calculate from stocks
            stocks = self._get_stocks_with_cache()
            if stocks:
                sorted_stocks = sorted(
                    [s for s in stocks if s.get('percentageChange', 0) < 0],
                    key=lambda x: x.get('percentageChange', 0)
                )
                return sorted_stocks[:limit]
            return []
        except Exception as e:
            logger.error(f"Error fetching top losers: {e}")
            # Fallback: calculate from stocks
            try:
                stocks = self._get_stocks_with_cache()
                if stocks:
                    sorted_stocks = sorted(
                        [s for s in stocks if s.get('percentageChange', 0) < 0],
                        key=lambda x: x.get('percentageChange', 0)
                    )
                    return sorted_stocks[:limit]
            except:
                pass
            return []
    
    def get_floorsheet(self, symbol: Optional[str] = None) -> Dict:
        """Get floorsheet data"""
        try:
            if symbol:
                correct_symbol = self._get_symbol(symbol)
                if not correct_symbol:
                    return {"error": f"Symbol {symbol} not found"}
                floorsheet = self.nepse.get_floorsheet(symbol=correct_symbol)
            else:
                floorsheet = self.nepse.get_floorsheet()
            return floorsheet if floorsheet else {"error": "No floorsheet data"}
        except Exception as e:
            logger.error(f"Error fetching floorsheet: {e}")
            return {"error": str(e)}
    
    def get_market_status(self) -> Dict:
        """Get current market status"""
        try:
            status = self.nepse.get_market_status()
            return status if status else {"error": "Could not get market status"}
        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return {"error": str(e)}
    
    def get_all_stocks(self) -> List[Dict]:
        """Get all stocks with live data"""
        try:
            stocks = self._get_stocks_with_cache()
            return stocks if stocks else []
        except Exception as e:
            logger.error(f"Error fetching all stocks: {e}")
            return []
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by name or symbol"""
        try:
            if self._company_list is None:
                self._build_maps()
            
            results = []
            query_upper = query.upper()
            
            for company in self._company_list:
                symbol = company.get('symbol', '')
                name = company.get('name', '')
                
                if (query_upper in symbol.upper() or 
                    query_upper in name.upper() or
                    query_upper in symbol.replace('-', '').upper()):
                    
                    results.append({
                        "symbol": symbol,
                        "id": company.get('id'),
                        "name": name
                    })
            
            return results[:20]
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []