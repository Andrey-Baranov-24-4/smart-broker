"""Юнит-тесты парсера голосовых команд (без БД и без сети)."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.services import parse_command


def test_add_with_price_and_quantity():
    cmd = parse_command("Добавь акцию Сбер по цене 180 рублей, количество 3")
    assert cmd.intent == "add"
    assert cmd.quantity == 3
    assert cmd.price == 180.0
    assert cmd.query and "сбер" in cmd.query.lower()


def test_price_question():
    cmd = parse_command("Какая сейчас цена Яндекс?")
    assert cmd.intent == "price"
    assert cmd.query and "яндекс" in cmd.query.lower()


def test_profit_question():
    cmd = parse_command("Сколько я заработал на Норникель?")
    assert cmd.intent == "profit"
    assert cmd.query and "норникель" in cmd.query.lower()


def test_show_portfolio():
    cmd = parse_command("Покажи мой портфель")
    assert cmd.intent == "show_portfolio"


def test_unknown():
    cmd = parse_command("привет как дела")
    assert cmd.intent == "unknown"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"OK {name}")
