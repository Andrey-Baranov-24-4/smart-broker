from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, services
from ..database import get_db
from ..moex import moex_client


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=schemas.PortfolioOut)
async def get_portfolio(db: Session = Depends(get_db)):
    portfolio = await services.build_portfolio(db)
    crud.save_snapshot(db, portfolio.total_value, portfolio.total_profit)
    return portfolio


@router.get("/history", response_model=list[schemas.SnapshotOut])
def portfolio_history(db: Session = Depends(get_db)):
    return crud.recent_snapshots(db)


@router.post("/positions", response_model=schemas.PositionOut, status_code=201)
async def add_position(payload: schemas.StockIn, db: Session = Depends(get_db)):
    info = await moex_client.find_stock(payload.query)
    if not info:
        raise HTTPException(
            status_code=422,
            detail=f"Акция «{payload.query}» не найдена на Мосбирже. "
                   "Попробуйте тикер (SBER, GAZP) или полное название.",
        )
    price = payload.purchase_price if payload.purchase_price else info.price
    position = crud.add_position(db, info, payload.quantity, price)

    quantity, cost = crud.total_quantity_and_cost(position.stock)
    avg = cost / quantity if quantity else price
    profit = crud.calc_profit(quantity, avg, info.price)
    return schemas.PositionOut(
        id=position.stock.id,
        ticker=info.ticker,
        name=info.name,
        quantity=quantity,
        purchase_price=round(avg, 4),
        current_price=round(info.price, 4),
        profit=round(profit, 2),
    )


@router.delete("/positions/{stock_id}", status_code=204)
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.get(services.models.Stock, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    db.delete(stock)
    db.commit()
    return None
