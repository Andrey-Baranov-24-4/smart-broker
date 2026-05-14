from fastapi import APIRouter, HTTPException

from .. import schemas
from ..moex import moex_client


router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{query}", response_model=schemas.PriceResponse)
async def get_price(query: str):
    info = await moex_client.find_stock(query)
    if not info:
        raise HTTPException(status_code=404, detail=f"Акция '{query}' не найдена")
    return schemas.PriceResponse(ticker=info.ticker, name=info.name, price=round(info.price, 4))
