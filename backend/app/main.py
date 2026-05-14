from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import portfolio, prices, voice


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Smart Broker API",
    description="Учёт инвестиционного портфеля с голосовым управлением через Сбер Салют",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.include_router(portfolio.router)
app.include_router(prices.router)
app.include_router(voice.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
