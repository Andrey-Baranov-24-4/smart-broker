import React from "react";
import StockItem from "./StockItem";

export default function StockList({ positions, onDelete }) {
  if (!positions || positions.length === 0) {
    return (
      <div className="card">
        <h2 className="card__title">Портфель</h2>
        <div className="empty">
          Портфель пуст. Добавьте акцию в форме выше или скажите:
          «Добавь Сбер по 180 рублей, количество 3».
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card__title">Портфель</h2>
      <table>
        <thead>
          <tr>
            <th>Акция</th>
            <th>Количество</th>
            <th>Цена покупки</th>
            <th>Текущая цена</th>
            <th>Прибыль</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {positions.map((p) => (
            <StockItem key={p.id} position={p} onDelete={onDelete} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
