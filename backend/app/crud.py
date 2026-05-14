from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .moex import StockInfo


def get_or_create_stock(db: Session, info: StockInfo) -> models.Stock:
    stmt = select(models.Stock).where(models.Stock.ticker == info.ticker)
    stock = db.scalar(stmt)
    if stock is None:
        stock = models.Stock(ticker=info.ticker, name=info.name)
        db.add(stock)
        db.flush()
    elif stock.name != info.name:
        stock.name = info.name
    return stock


def add_position(db: Session, info: StockInfo, quantity: int, purchase_price: float) -> models.Position:
    stock = get_or_create_stock(db, info)
    position = models.Position(stock_id=stock.id, quantity=quantity, purchase_price=purchase_price)
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


def aggregated_positions(db: Session) -> list[models.Stock]:
    stmt = select(models.Stock).join(models.Position).distinct()
    return list(db.scalars(stmt).all())


def total_quantity_and_cost(stock: models.Stock) -> tuple[int, float]:
    quantity = sum(p.quantity for p in stock.positions)
    cost = sum(p.quantity * p.purchase_price for p in stock.positions)
    return quantity, cost


def calc_profit(quantity: int, avg_purchase: float, current_price: float) -> float:
    commission = settings.commission_rate
    return ((current_price * (1 - commission)) - (avg_purchase * (1 + commission))) * quantity


def find_stock_by_query(db: Session, query: str) -> Optional[models.Stock]:
    q = query.strip().upper()
    stmt = select(models.Stock).where(models.Stock.ticker == q)
    found = db.scalar(stmt)
    if found:
        return found
    stmt = select(models.Stock).where(models.Stock.name.ilike(f"%{query}%"))
    return db.scalar(stmt)


def save_snapshot(db: Session, total_value: float, total_profit: float) -> models.PortfolioSnapshot:
    snap = models.PortfolioSnapshot(total_value=total_value, total_profit=total_profit)
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


def recent_snapshots(db: Session, limit: int = 50) -> list[models.PortfolioSnapshot]:
    stmt = select(models.PortfolioSnapshot).order_by(models.PortfolioSnapshot.taken_at.desc()).limit(limit)
    rows = list(db.scalars(stmt).all())
    return list(reversed(rows))
