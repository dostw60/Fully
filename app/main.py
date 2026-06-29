from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import market
from app.services.market_service import MarketService
from app.providers.live_provider import LiveProvider
import json
import asyncio
from datetime import datetime

app = FastAPI(
    title="NEPSE Platform API",
    description="Professional NEPSE trading platform backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(market.router)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}  # symbol -> list of websockets
    
    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        self.active_connections[symbol].append(websocket)
        print(f"✅ Client connected to {symbol}. Total connections: {len(self.active_connections[symbol])}")
    
    def disconnect(self, websocket: WebSocket, symbol: str):
        if symbol in self.active_connections:
            if websocket in self.active_connections[symbol]:
                self.active_connections[symbol].remove(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
            print(f"❌ Client disconnected from {symbol}")
    
    async def broadcast(self, symbol: str, message: str):
        if symbol in self.active_connections:
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()
market_service = MarketService()
live_provider = LiveProvider()  # Direct provider for WebSocket

@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await manager.connect(websocket, symbol)
    try:
        while True:
            # Use LiveProvider directly (same as REST API)
            data = live_provider.get_live_price(symbol)
            
            # Check for error
            if "error" in data:
                error_data = {
                    "symbol": symbol,
                    "error": data["error"],
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(error_data))
                await asyncio.sleep(3)
                continue
            
            # Format data with all fields
            formatted_data = {
                "symbol": data.get("symbol", symbol),
                "price": data.get("price", 0),
                "change": data.get("change", 0),
                "change_percent": data.get("change_percent", 0),
                "volume": data.get("volume", 0),
                "open": data.get("open", 0),
                "high": data.get("high", 0),
                "low": data.get("low", 0),
                "prev_close": data.get("prev_close", 0),
                "turnover": data.get("turnover", 0),
                "transactions": data.get("transactions", 0),
                "company_name": data.get("company_name", ""),
                "timestamp": datetime.now().isoformat(),
                "server_time": datetime.now().strftime("%H:%M:%S")
            }
            
            # Send to client
            await websocket.send_text(json.dumps(formatted_data))
            
            # Wait 3 seconds before next update
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
    except Exception as e:
        print(f"WebSocket error for {symbol}: {e}")
        manager.disconnect(websocket, symbol)

@app.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    """WebSocket for market-wide updates"""
    await websocket.accept()
    try:
        while True:
            # Get market summary
            summary = market_service.get_market_summary()
            summary["timestamp"] = datetime.now().isoformat()
            summary["server_time"] = datetime.now().strftime("%H:%M:%S")
            
            await websocket.send_text(json.dumps(summary))
            await asyncio.sleep(5)  # Update every 5 seconds
    except WebSocketDisconnect:
        print("Market client disconnected")
    except Exception as e:
        print(f"Market WebSocket error: {e}")

@app.get("/")
async def root():
    return {
        "message": "Welcome to NEPSE Platform API",
        "version": "1.0.0",
        "websocket_endpoints": {
            "single_stock": "ws://localhost:8000/ws/{symbol}",
            "market": "ws://localhost:8000/ws/market"
        },
        "endpoints": {
            "live": "/market/live/{symbol}",
            "history": "/market/history/{symbol}",
            "company": "/market/company/{symbol}",
            "summary": "/market/summary",
            "profile": "/market/profile/{symbol}",
            "all_stocks": "/market/all-stocks",
            "search": "/market/search?query=NABIL",
            "depth": "/market/depth/{symbol}",
            "floorsheet": "/market/floorsheet",
            "status": "/market/status",
            "today": "/market/today/{symbol}"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "websocket_connections": {
            symbol: len(connections) 
            for symbol, connections in manager.active_connections.items()
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )