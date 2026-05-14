"""Клиент для публичного ISS API Московской биржи."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx

from .config import settings


ENGINE = "stock"
MARKET = "shares"


@dataclass
class StockInfo:
    ticker: str
    name: str
    price: float


_NAME_ALIASES = {
    "сбер": "SBER",
    "сбербанк": "SBER",
    "газпром": "GAZP",
    "лукойл": "LKOH",
    "яндекс": "YDEX",
    "норникель": "GMKN",
    "норильский никель": "GMKN",
    "магнит": "MGNT",
    "роснефть": "ROSN",
    "втб": "VTBR",
    "мтс": "MTSS",
    "тинькофф": "T",
    "t-банк": "T",
    "озон": "OZON",
    "ozon": "OZON",
    "полюс": "PLZL",
    "новатэк": "NVTK",
    "татнефть": "TATN",
}


# Допустимые русские падежные окончания после стема названия акции.
# Использовалось для отсечки ложных префиксных матчей: «яндексморе» не
# должен резолвиться в «яндекс», а «яндексом» — должен.
_RU_NOUN_ENDINGS = frozenset({
    "", "а", "у", "ы", "е", "и", "о", "ю",
    "ом", "ой", "ей", "ев", "ов", "ам", "ах", "ям", "ях",
    "ами", "ями",
})


def _resolve_alias(lowered: str) -> Optional[str]:
    """Поиск тикера в _NAME_ALIASES с учётом русской морфологии.

    Sber STT и пользователь могут произносить название в любом падеже:
    «купи Яндекса», «прибыль по Сбербанку», «цена Газпромом». Жёсткая
    словарная сверка таких форм не ловит, поэтому:

    1. Сначала пробуем точный матч.
    2. Затем ищем алиас, который является префиксом запроса с
       допустимым русским падежным окончанием (берём самый длинный
       алиас, чтобы «сбербанка» резолвился через «сбербанк», а не «сбер»).
    """
    if lowered in _NAME_ALIASES:
        return _NAME_ALIASES[lowered]

    best_match: Optional[str] = None
    best_len = 0
    for alias_key, ticker in _NAME_ALIASES.items():
        if not lowered.startswith(alias_key) or len(alias_key) <= best_len:
            continue
        tail = lowered[len(alias_key):]
        if tail in _RU_NOUN_ENDINGS:
            best_match = ticker
            best_len = len(alias_key)
    return best_match


class MoexClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = (base_url or settings.moex_base_url).rstrip("/")

    async def find_stock(self, query: str) -> Optional[StockInfo]:
        """Ищет акцию по тикеру или части названия, возвращает тикер + цену."""
        query = query.strip()
        if not query:
            return None

        lowered = query.lower()
        # Алиас может совпадать как точно («сбер»), так и с учётом
        # русских падежных окончаний — модератор сообщил, что «Яндекса»
        # не распознаётся, а «Яндекс» работает. Сначала пробуем точный
        # матч, затем — алиас, который является префиксом запроса
        # («яндекса» → «яндекс», «сбербанка» → «сбербанк»).
        ticker_guess = _resolve_alias(lowered) or query.upper()

        info = await self._fetch_by_ticker(ticker_guess)
        if info:
            return info

        return await self._fetch_by_search(query)

    async def get_price(self, ticker: str) -> Optional[StockInfo]:
        return await self._fetch_by_ticker(ticker.upper())

    async def _fetch_by_ticker(self, ticker: str) -> Optional[StockInfo]:
        url = (
            f"{self.base_url}/iss/engines/{ENGINE}/markets/{MARKET}/securities/{ticker}.json"
            "?iss.meta=off&iss.only=securities,marketdata"
        )
        data = await self._get(url)
        if not data:
            return None

        securities = _rows(data.get("securities"))
        marketdata = _rows(data.get("marketdata"))
        if not securities:
            return None

        sec = securities[0]
        md = marketdata[0] if marketdata else {}
        price = md.get("LAST") or md.get("MARKETPRICE") or sec.get("PREVPRICE")
        if price is None:
            return None

        return StockInfo(
            ticker=sec.get("SECID", ticker),
            name=sec.get("SHORTNAME") or sec.get("SECNAME") or ticker,
            price=float(price),
        )

    async def _fetch_by_search(self, query: str) -> Optional[StockInfo]:
        url = (
            f"{self.base_url}/iss/securities.json"
            f"?q={query}&iss.meta=off&iss.only=securities&limit=5"
        )
        data = await self._get(url)
        if not data:
            return None

        rows = _rows(data.get("securities"))
        for row in rows:
            if row.get("is_traded") in (1, "1") and row.get("group", "").startswith("stock_shares"):
                return await self._fetch_by_ticker(row["secid"])

        if rows:
            return await self._fetch_by_ticker(rows[0]["secid"])
        return None

    @staticmethod
    async def _get(url: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.json()
        except (httpx.HTTPError, ValueError):
            return None


def _rows(block: Optional[dict]) -> list[dict]:
    if not block:
        return []
    columns = block.get("columns") or []
    data = block.get("data") or []
    return [dict(zip(columns, row)) for row in data]


moex_client = MoexClient()
