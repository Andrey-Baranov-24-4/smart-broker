from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class StockIn(BaseModel):
    query: str = Field(..., description="Тикер или часть названия акции")
    quantity: int = Field(..., gt=0)
    purchase_price: Optional[float] = Field(None, gt=0, description="Если не указано — берётся текущая цена")


class PriceResponse(BaseModel):
    ticker: str
    name: str
    price: float


class PositionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    name: str
    quantity: int
    purchase_price: float
    current_price: float
    profit: float


class PortfolioOut(BaseModel):
    positions: list[PositionOut]
    total_value: float
    total_profit: float


class SnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    taken_at: datetime
    total_value: float
    total_profit: float


class VoiceCommand(BaseModel):
    text: str = Field(..., description="Распознанный текст реплики пользователя")


class VoiceResponse(BaseModel):
    reply: str
    portfolio: Optional[PortfolioOut] = None
    price: Optional[PriceResponse] = None
