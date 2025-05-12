import aiohttp
import os
from fastapi import HTTPException
from datetime import datetime, timedelta
import asyncio
from redis_cache import RedisCache

cache = RedisCache()

async def fetch_stock_data(ticker: str, token: str = None):
    url = f"http://20.244.56.144/evaluation-service/stocks?ticker={ticker}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail=f"Failed to fetch data for {ticker}: {response.status}")
                return await response.json()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error fetching data for {ticker}: {str(e)}")

async def get_stock_data(ticker: str, minutes: int):
    
    token = os.getenv("STOCK_API_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQ3MDU0ODAyLCJpYXQiOjE3NDcwNTQ1MDIsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjJjNjYyYzRkLTI0ZGEtNGVlNC04ZmVkLTAyNWI5ZTMyZjE2NSIsInN1YiI6InNhaWNoYXJhbmRhczIwMDVAZ21haWwuY29tIn0sImVtYWlsIjoic2FpY2hhcmFuZGFzMjAwNUBnbWFpbC5jb20iLCJuYW1lIjoic2FpIGNoYXJhbiBkYXMiLCJyb2xsTm8iOiJhbS5lbi51NGNzZTIyMDQ3IiwiYWNjZXNzQ29kZSI6IlN3dXVLRSIsImNsaWVudElEIjoiMmM2NjJjNGQtMjRkYS00ZWU0LThmZWQtMDI1YjllMzJmMTY1IiwiY2xpZW50U2VjcmV0IjoiQXJ0d2tEQVdZS1RXR2VuYSJ9.tZ_RDBDKhEYGVJm6Vo2yMQT_5sfw9cSYlbhlHvOYPC4")  # Replace with your actual token
    if not token:
        raise HTTPException(status_code=500, detail="API token not configured")
    
    cached_data = cache.get(ticker)
    if cached_data:
        return cached_data
    
    raw_data = await fetch_stock_data(ticker, token)
    if not raw_data:
        return {"priceHistory": []}
    
    cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
    filtered_data = [
        entry for entry in raw_data.get("priceHistory", [])
        if datetime.fromisoformat(entry["lastUpdatedAt"].replace("Z", "+00:00")) >= cutoff_time
    ]
    
    result = {"priceHistory": filtered_data}
    cache.set(ticker, result)
    return result

async def refresh_stock_data_periodically():
    while True:
        # Prefer environment variable for token, fall back to hardcoded token
        token = os.getenv("STOCK_API_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQ3MDU0ODAyLCJpYXQiOjE3NDcwNTQ1MDIsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjJjNjYyYzRkLTI0ZGEtNGVlNC04ZmVkLTAyNWI5ZTMyZjE2NSIsInN1YiI6InNhaWNoYXJhbmRhczIwMDVAZ21haWwuY29tIn0sImVtYWlsIjoic2FpY2hhcmFuZGFzMjAwNUBnbWFpbC5jb20iLCJuYW1lIjoic2FpIGNoYXJhbiBkYXMiLCJyb2xsTm8iOiJhbS5lbi51NGNzZTIyMDQ3IiwiYWNjZXNzQ29kZSI6IlN3dXVLRSIsImNsaWVudElEIjoiMmM2NjJjNGQtMjRkYS00ZWU0LThmZWQtMDI1YjllMzJmMTY1IiwiY2xpZW50U2VjcmV0IjoiQXJ0d2tEQVdZS1RXR2VuYSJ9.tZ_RDBDKhEYGVJm6Vo2yMQT_5sfw9cSYlbhlHvOYPC4")  # Replace with your actual token
        if not token:
            raise Exception("API token not configured")
        
        tickers = ["NVDA", "PYPL", "AAPL", "MSFT"]
        for ticker in tickers:
            try:
                raw_data = await fetch_stock_data(ticker, token)
                if raw_data and "priceHistory" in raw_data:
                    cache.set(ticker, {"priceHistory": raw_data["priceHistory"]})
            except Exception as e:
                print(f"Error refreshing data for {ticker}: {str(e)}")
        await asyncio.sleep(60)  # Refresh every minute