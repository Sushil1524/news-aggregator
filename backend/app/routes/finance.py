from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from app.services.finance_service import get_market_indices, get_stock_details, search_stocks

router = APIRouter()

@router.get("/indices", response_model=List[Dict[str, Any]])
async def read_indices():
    """
    Get current market indices (NIFTY 50, SENSEX, etc.)
    """
    return get_market_indices()

@router.get("/stock/{ticker}", response_model=Dict[str, Any])
async def read_stock(ticker: str):
    """
    Get details for a specific stock by ticker symbol.
    """
    data = get_stock_details(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found")
    return data

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_stock_market(q: str = Query(..., min_length=1)):
    """
    Search for stocks.
    """
    return search_stocks(q)
