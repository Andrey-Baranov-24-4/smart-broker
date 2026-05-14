import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function PortfolioChart({ history }) {
  if (!history || history.length === 0) {
    return null;
  }

  const data = history.map((h) => ({
    time: new Date(h.taken_at).toLocaleTimeString("ru-RU", {
      hour: "2-digit",
      minute: "2-digit",
    }),
    value: h.total_value,
    profit: h.total_profit,
  }));

  return (
    <div className="card">
      <h2 className="card__title">Стоимость портфеля</h2>
      <div style={{ width: "100%", height: 240 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1d2844" />
            <XAxis dataKey="time" stroke="#97a3b6" />
            <YAxis stroke="#97a3b6" />
            <Tooltip
              contentStyle={{ background: "#0e1626", border: "1px solid #1d2844" }}
            />
            <Line type="monotone" dataKey="value" stroke="#3d7cff" dot={false} name="Стоимость" />
            <Line type="monotone" dataKey="profit" stroke="#3dd68c" dot={false} name="Прибыль" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
