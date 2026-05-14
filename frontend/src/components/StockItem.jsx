import React from "react";

const fmt = (n) => n.toLocaleString("ru-RU", { maximumFractionDigits: 2 });

export default function StockItem({ position, onDelete }) {
  const profitClass = position.profit >= 0 ? "positive" : "negative";
  return (
    <tr>
      <td>
        <div style={{ fontWeight: 600 }}>{position.name}</div>
        <div style={{ fontSize: 12, color: "#97a3b6" }}>{position.ticker}</div>
      </td>
      <td>{position.quantity}</td>
      <td>{fmt(position.purchase_price)} ₽</td>
      <td>{fmt(position.current_price)} ₽</td>
      <td className={profitClass}>
        {position.profit >= 0 ? "+" : ""}
        {fmt(position.profit)} ₽
      </td>
      <td>
        <button
          className="btn btn--ghost"
          onClick={() => onDelete(position.id)}
          aria-label={`Удалить ${position.name}`}
        >
          ×
        </button>
      </td>
    </tr>
  );
}
