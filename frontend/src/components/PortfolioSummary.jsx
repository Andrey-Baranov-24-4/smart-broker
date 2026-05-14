import React from "react";

const fmt = (n) => n.toLocaleString("ru-RU", { maximumFractionDigits: 2 });

export default function PortfolioSummary({ portfolio }) {
  if (!portfolio) return null;
  const profitClass = portfolio.total_profit >= 0 ? "positive" : "negative";
  return (
    <div className="card">
      <h2 className="card__title">Сводка</h2>
      <div className="summary">
        <div className="summary__item">
          <div className="summary__label">Позиций</div>
          <div className="summary__value">{portfolio.positions.length}</div>
        </div>
        <div className="summary__item">
          <div className="summary__label">Стоимость</div>
          <div className="summary__value">{fmt(portfolio.total_value)} ₽</div>
        </div>
        <div className="summary__item">
          <div className="summary__label">Прибыль</div>
          <div className={`summary__value ${profitClass}`}>
            {portfolio.total_profit >= 0 ? "+" : ""}
            {fmt(portfolio.total_profit)} ₽
          </div>
        </div>
      </div>
    </div>
  );
}
