import React from "react";
import "./App.css";
import Portfolio from "./pages/Portfolio";

export default function App() {
  return (
    <div className="app">
      <header className="app__header">
        <div>
          <h1 className="app__title">Умный брокер</h1>
          <div className="app__subtitle">
            Голосовой учёт инвестиционного портфеля
          </div>
        </div>
      </header>
      <Portfolio />
    </div>
  );
}
