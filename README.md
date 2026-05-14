# Smart Broker

Смартап для учёта инвестиционного портфеля с голосовым управлением через ассистента **Сбер Салют**.

## Что умеет

- Добавлять акции в портфель голосом или через форму: «добавь Сбер по 180 рублей, количество 3»
- Показывать текущие котировки с Московской биржи: «какая цена Яндекса?»
- Считать прибыль/убыток по каждой бумаге и по всему портфелю
- Строить график истории стоимости портфеля
- Работать внутри приложений Сбер Салют (SberPortal, SberBox, СберБанк Онлайн)

## Архитектура

```
┌─────────────────────┐     smart_app_data      ┌──────────────────────┐
│  Canvas App (React) │ ◄────────────────────── │  SmartApp Code       │
│  frontend/          │                          │  voice-assistant/    │
└────────┬────────────┘                          └────────┬─────────────┘
         │ REST API                                       │ POST /voice/command
         ▼                                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                              │
│  backend/   ·  PostgreSQL  ·  ISS API Мосбиржи                     │
│  https://212-8-227-28.sslip.io                                      │
└─────────────────────────────────────────────────────────────────────┘
```

| Компонент | Стек |
|-----------|------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2, PostgreSQL 17 |
| **Frontend** | React, @salutejs/client, recharts |
| **Voice** | JAICP / SaluteScript, CAILA NLU |
| **Infra** | VPS Ubuntu 24.04, nginx, systemd, Let's Encrypt |

## Структура репозитория

```
smart-broker/
├── backend/                # FastAPI-сервис
│   ├── app/
│   │   ├── main.py         # точка входа, CORS, lifespan
│   │   ├── models.py       # SQLAlchemy-модели (stocks, positions, snapshots)
│   │   ├── schemas.py      # Pydantic-схемы
│   │   ├── crud.py         # операции с БД
│   │   ├── services.py     # бизнес-логика + разбор голосовых команд
│   │   ├── moex.py         # клиент ISS API Мосбиржи
│   │   └── routers/
│   │       ├── portfolio.py
│   │       ├── prices.py
│   │       └── voice.py
│   └── requirements.txt
│
├── frontend/               # React Canvas App
│   └── src/
│       ├── assistant/      # обёртка @salutejs/client
│       ├── api/            # REST-клиент
│       ├── components/     # StockList, PortfolioChart, AddStock, VoiceBar…
│       └── pages/
│
└── voice-assistant/        # JAICP-сценарий SmartApp Code
    ├── src/
    │   ├── entryPoint.sc
    │   ├── scenario/       # addStock, getPrice, getProfit, showPortfolio
    │   └── js/             # вызов backend + формирование ответа
    ├── caila_import.json   # интенты для CAILA NLU
    └── scenario.zip        # готовый архив для SmartApp Studio
```

## Быстрый старт

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env          # задайте DATABASE_URL
uvicorn app.main:app --reload
```

Swagger-документация: http://localhost:8000/docs

### Frontend

```bash
cd frontend
cp .env.sample .env          # задайте REACT_APP_API_URL
npm install && npm start
```

### Голосовой сценарий

1. Соберите ZIP: `cd voice-assistant && python build_zip.py`
2. В SmartApp Studio создайте проект **Code for SmartApp**
3. Загрузите `scenario.zip`
4. Добавьте переменную среды `BACKEND_URL` = URL вашего бэкенда
5. Опубликуйте и свяжите с Canvas App

## API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка доступности |
| GET | `/portfolio` | Состояние портфеля + снэпшот |
| GET | `/portfolio/history` | История стоимости (для графика) |
| POST | `/portfolio/positions` | Добавить позицию |
| DELETE | `/portfolio/positions/{id}` | Удалить позицию |
| GET | `/prices/{query}` | Текущая цена по тикеру/названию |
| POST | `/voice/command` | Обработать голосовую команду |

Публичный API: https://212-8-227-28.sslip.io/docs

## Голосовые команды

| Что сказать | Что произойдёт |
|-------------|----------------|
| «покажи портфель» | Озвучит состав и общую стоимость |
| «какая цена Сбера?» | Вернёт текущую котировку с Мосбиржи |
| «добавь Газпром по 150 рублей количество 5» | Добавит позицию |
| «сколько я заработал на Яндексе?» | Посчитает прибыль по бумаге |
| «что ты умеешь?» | Справка по командам |

## Состав проекта

```
smart-broker/
├── backend/          Python + FastAPI + SQLAlchemy + PostgreSQL, интеграция с MOEX
├── frontend/         React (Canvas App) + @salutejs/client
└── voice-assistant/  SmartApp Code — сценарий для Сбер Салют (JAICP)
```

## Быстрый старт

### 1. Backend

Нужен локальный PostgreSQL — инструкции по установке и созданию БД
смотрите в [backend/README.md](backend/README.md).

```bash
cd backend
python -3.12 -m venv .venv
source .venv/bin/activate      # Windows: 
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Строка подключения — в `backend/.env` (`DATABASE_URL`).

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

Откроется `http://localhost:3000`, API-запросы проксируются на `:8000`.

### 3. Voice Assistant

Сценарий Сбер Салют живёт в облаке SmartApp Studio, локально ничего не
запускается. Нужно:
1. Собрать архив: `cd voice-assistant && python build_zip.py`
2. Загрузить `scenario.zip` в проект **Code for SmartApp**.
3. Указать в настройках Studio переменную `BACKEND_URL` (публичный HTTPS backend —
   ngrok для разработки или ваш хостинг для продакшена).

## Основные возможности

- Добавление акции в портфель: название/тикер, цена покупки, количество.
- Автоматическое получение текущей цены через API Московской биржи.
- Подсчёт прибыли/убытка с учётом комиссии.
- Голосовые команды:
  - «Добавь акцию Сбер по цене 180 рублей, количество 3»
  - «Какая сейчас цена Яндекс?»
  - «Сколько я заработал на Норникель?»
  - «Покажи мой портфель»
- Просмотр портфеля: акция, количество, цена покупки, текущая цена, прибыль.
- График изменения общей стоимости портфеля.

## Архитектура

```
┌──────────────┐     ┌──────────────┐       ┌──────────────┐
│ Sber Салют   │─────│  Frontend    │──HTTP─│   Backend    │
│ (голос)      │     │  (React +    │       │ (FastAPI +   │
│              │     │  Canvas App) │       │  SQLAlchemy) │
└──────┬───────┘     └──────────────┘       └──────┬───────┘
       │                                           │
       │                                    ┌──────┴──────┐
       │                                    │ PostgreSQL  │
       │                                    └─────────────┘
       │
       │  ┌──────────────────┐
       └─▶│  SmartApp Code   │──HTTPS──▶ backend /voice/command
          │  (scenario)      │
          └──────────────────┘
```

SmartApp Code и Canvas App хостятся Сбером — локально запускаются только
backend и frontend (опционально).
