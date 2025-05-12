from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict
import services
import asyncio

app = FastAPI(title="Stock Price Aggregation Microservice")

# Pydantic models for response validation
class PricePoint(BaseModel):
    price: float
    lastUpdatedAt: str

class AverageStockPriceResponse(BaseModel):
    averageStockPrice: float
    priceHistory: List[PricePoint]

class StockData(BaseModel):
    averagePrice: float
    priceHistory: List[PricePoint]

class CorrelationResponse(BaseModel):
    correlation: float
    stocks: Dict[str, StockData]

# Background task to refresh stock data
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(services.refresh_stock_data_periodically())

@app.get("/stocks/{ticker}", response_model=AverageStockPriceResponse)
async def get_average_stock_price(
    ticker: str,
    minutes: int = Query(..., ge=1, description="Time window in minutes"),
    aggregation: str = Query("average", description="Aggregation type")
):
    if aggregation != "average":
        raise HTTPException(status_code=400, detail="Only 'average' aggregation is supported")
    
    try:
        result = await services.get_average_stock_price(ticker.upper(), minutes)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stockcorrelation", response_model=CorrelationResponse)
async def get_stock_correlation(
    minutes: int = Query(..., ge=1, description="Time window in minutes"),
    ticker: List[str] = Query(..., description="List of exactly two tickers")
):
    if len(ticker) != 2:
        raise HTTPException(status_code=400, detail="Exactly two tickers must be provided")
    
    ticker1, ticker2 = ticker[0].upper(), ticker[1].upper()
    try:
        result = await services.get_stock_correlation(ticker1, ticker2, minutes)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")