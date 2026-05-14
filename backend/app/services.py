"""Сервисный слой: подсчёт портфеля и обработка голосовых команд."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .moex import MoexClient, StockInfo, moex_client


async def build_portfolio(db: Session, client: MoexClient = moex_client) -> schemas.PortfolioOut:
    stocks = crud.aggregated_positions(db)
    positions: list[schemas.PositionOut] = []
    total_value = 0.0
    total_profit = 0.0

    for stock in stocks:
        quantity, cost = crud.total_quantity_and_cost(stock)
        if quantity == 0:
            continue
        avg_purchase = cost / quantity
        info = await client.get_price(stock.ticker)
        current_price = info.price if info else avg_purchase
        profit = crud.calc_profit(quantity, avg_purchase, current_price)
        total_value += current_price * quantity
        total_profit += profit
        positions.append(
            schemas.PositionOut(
                id=stock.id,
                ticker=stock.ticker,
                name=stock.name,
                quantity=quantity,
                purchase_price=round(avg_purchase, 4),
                current_price=round(current_price, 4),
                profit=round(profit, 2),
            )
        )

    return schemas.PortfolioOut(
        positions=positions,
        total_value=round(total_value, 2),
        total_profit=round(total_profit, 2),
    )


# ---------- Голосовые команды ----------

@dataclass
class ParsedCommand:
    intent: str
    query: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None


_WORD_NUMBERS = {
    "ноль": 0, "один": 1, "одна": 1, "одну": 1, "два": 2, "две": 2, "три": 3,
    "четыре": 4, "пять": 5, "шесть": 6, "семь": 7, "восемь": 8, "девять": 9,
    "десять": 10, "двадцать": 20, "тридцать": 30, "сорок": 40, "пятьдесят": 50,
    "сто": 100,
}


def _number(word: str) -> Optional[float]:
    word = word.strip().lower().replace(",", ".")
    if not word:
        return None
    if word.replace(".", "", 1).isdigit():
        return float(word)
    return _WORD_NUMBERS.get(word)


def parse_command(text: str) -> ParsedCommand:
    t = text.lower().strip()

    if re.search(r"\b(помощ|помоги|что\s+ты\s+умеешь|справк|как\s+пользова|инструкц)", t):
        return ParsedCommand(intent="help")

    if re.search(r"\b(портфел|состоян|мои\s+акци)", t):
        return ParsedCommand(intent="show_portfolio")

    if re.search(r"(прибыл|заработал|заработа|потерял|потеря)", t):
        query = _extract_query(t, triggers=("на ", "по ", "от "))
        return ParsedCommand(intent="profit", query=query)

    # ВАЖНО: «добавь» должно проверяться раньше «цена», иначе фразы вида
    # «добавь Яндекс цена 4500» уйдут в интент price.
    if re.search(r"\b(добав|купи|закуп)", t):
        price = None
        quantity = None

        # Цена: «по 180», «по цене 180», «за 180», «цена 180», «ценой 180»
        m_price = re.search(
            r"(?:по\s+цене|цене[йю]?|по|за|цена[йю]?)\s+([\d.,]+)",
            t,
        )
        if m_price:
            price = _number(m_price.group(1))

        # Количество: «количество 3», «3 штук(и)», «3 шт»
        m_qty = re.search(r"количеств[оа]\s*[:\-]?\s*(\S+)", t)
        if m_qty:
            quantity = _number(m_qty.group(1))
        if quantity is None:
            m_qty = re.search(r"(\d+)\s*(?:штук|шт\.?)\b", t)
            if m_qty:
                quantity = _number(m_qty.group(1))

        # Перед извлечением тикера вычищаем из текста все упоминания цены и
        # количества — иначе цифры или «180 рублей» залипают в query и MOEX
        # отдаёт 404.
        cleaned = t
        cleaned = re.sub(
            r"(?:по\s+цене|цене[йю]?|цена[йю]?|по|за)\s+[\d.,]+\s*(?:рубл[яейь]+|руб\.?)?",
            " ",
            cleaned,
        )
        cleaned = re.sub(r"[\d.,]+\s*(?:рубл[яейь]+|руб\.?)", " ", cleaned)
        cleaned = re.sub(r"количеств[оа]\s*[:\-]?\s*\S+", " ", cleaned)
        cleaned = re.sub(r"\d+\s*(?:штук\w*|шт\.?)", " ", cleaned)
        cleaned = re.sub(r"\b\d+(?:[.,]\d+)?\b", " ", cleaned)

        query = _extract_query(
            cleaned,
            triggers=("добавь ", "добавить ", "купи ", "купить ", "закупи ", "закупить ", "акцию "),
        )
        return ParsedCommand(
            intent="add",
            query=query,
            price=price,
            quantity=int(quantity) if quantity else None,
        )

    # Используем стемы (цен/стоимост/котировк), чтобы ловить любые падежные
    # формы: «цена», «цену», «цены», «по цене», «стоимости», «котировку»…
    if re.search(r"(\bцен[аеуыио]|стоимост|котировк|почём|почем)", t):
        query = _extract_query(
            t,
            triggers=(
                "цена ", "цену ", "цены ", "цене ",
                "стоимость ", "стоимости ", "стоимостью ",
                "котировка ", "котировку ", "котировки ",
            ),
        )
        return ParsedCommand(intent="price", query=query)

    return ParsedCommand(intent="unknown")


_STOPWORDS = {
    "акцию", "акция", "акций", "акции", "по", "цене", "цена", "цену",
    "цены", "ценой", "стоимость", "стоимости", "стоимостью", "котировка",
    "котировку", "котировки", "за", "рубля", "рублей", "рубль", "руб",
    "количество", "количества", "штук", "штука", "штуки", "шт", "сейчас",
    "какая", "какой", "какое", "сколько", "почём", "почем", "я", "на",
    "от", "есть", "в", "моем", "моём", "портфеле", "пожалуйста", "добавь",
    "добавить", "купи", "купить", "закупи", "закупить", "покажи",
    "показать", "скажи", "сказать",
}


def _extract_query(text: str, triggers: tuple[str, ...]) -> Optional[str]:
    t = text
    for tr in triggers:
        idx = t.find(tr)
        if idx != -1:
            t = t[idx + len(tr):]
            break
    t = re.split(r"(?:по\s+цене|цене|количеств[оа]|штук|шт\.?|[?!.])", t)[0]
    tokens = [w for w in re.findall(r"[\wё-]+", t, flags=re.UNICODE) if w.lower() not in _STOPWORDS and not w.isdigit()]
    return " ".join(tokens).strip() or None


_HELP_TEXT = (
    "Я умею вести инвестиционный портфель. Скажите: «покажи портфель», "
    "«какая цена Сбера», «добавь Газпром по 150 рублей количество 5» или "
    "«сколько прибыли по Яндексу». Можно также удалять позиции и узнавать "
    "общую прибыль портфеля."
)


async def handle_voice(db: Session, text: str, client: MoexClient = moex_client) -> schemas.VoiceResponse:
    cmd = parse_command(text)

    if cmd.intent == "help":
        return schemas.VoiceResponse(reply=_HELP_TEXT)

    if cmd.intent == "show_portfolio":
        portfolio = await build_portfolio(db, client)
        if not portfolio.positions:
            return schemas.VoiceResponse(reply="Портфель пуст. Добавьте акции голосом.", portfolio=portfolio)
        lines = ", ".join(f"{p.name} {p.quantity} шт." for p in portfolio.positions)
        reply = (
            f"В портфеле: {lines}. Общая стоимость {portfolio.total_value:.2f} рублей, "
            f"прибыль {portfolio.total_profit:.2f} рублей."
        )
        return schemas.VoiceResponse(reply=reply, portfolio=portfolio)

    if cmd.intent == "price":
        if not cmd.query:
            return schemas.VoiceResponse(reply="Не понял, цену какой акции показать.")
        info = await client.find_stock(cmd.query)
        if not info:
            return schemas.VoiceResponse(reply=f"Не нашёл акцию «{cmd.query}» на Мосбирже.")
        return schemas.VoiceResponse(
            reply=f"Текущая цена {info.name} — {info.price:.2f} рублей.",
            price=schemas.PriceResponse(ticker=info.ticker, name=info.name, price=info.price),
        )

    if cmd.intent == "profit":
        if not cmd.query:
            portfolio = await build_portfolio(db, client)
            return schemas.VoiceResponse(
                reply=f"Общая прибыль портфеля: {portfolio.total_profit:.2f} рублей.",
                portfolio=portfolio,
            )
        stock = crud.find_stock_by_query(db, cmd.query)
        if not stock:
            return schemas.VoiceResponse(reply=f"Акции «{cmd.query}» нет в вашем портфеле.")
        quantity, cost = crud.total_quantity_and_cost(stock)
        if quantity == 0:
            return schemas.VoiceResponse(reply=f"Позиций по {stock.name} нет.")
        info = await client.get_price(stock.ticker)
        if not info:
            return schemas.VoiceResponse(reply=f"Не смог получить цену {stock.name}.")
        avg = cost / quantity
        profit = crud.calc_profit(quantity, avg, info.price)
        verb = "заработали" if profit >= 0 else "потеряли"
        return schemas.VoiceResponse(
            reply=f"Вы {verb} {abs(profit):.2f} рублей на {stock.name}.",
        )

    if cmd.intent == "add":
        if not cmd.query or not cmd.quantity:
            return schemas.VoiceResponse(
                reply="Скажите название акции и количество. Например: добавь Сбер по 180 рублей, количество 3."
            )
        info = await client.find_stock(cmd.query)
        if not info:
            return schemas.VoiceResponse(reply=f"Не нашёл акцию «{cmd.query}» на Мосбирже.")
        price = cmd.price if cmd.price else info.price
        crud.add_position(db, info, cmd.quantity, price)
        return schemas.VoiceResponse(
            reply=f"Добавил {cmd.quantity} шт. {info.name} по цене {price:.2f} рублей.",
        )

    return schemas.VoiceResponse(reply=_HELP_TEXT)
