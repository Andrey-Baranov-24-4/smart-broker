import React, { useRef, useState } from "react";

export default function AddStock({ onAdd, error }) {
  const [query, setQuery] = useState("");
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const formRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query || !quantity) return;
    // Снимаем фокус с активного инпута до отправки — это закрывает системную
    // клавиатуру и предотвращает «застревание» зума на мобильных Салютах.
    if (document.activeElement && document.activeElement.blur) {
      document.activeElement.blur();
    }
    setSubmitting(true);
    try {
      await onAdd({
        query,
        quantity: Number(quantity),
        purchase_price: price ? Number(price) : undefined,
      });
      setQuery("");
      setQuantity("");
      setPrice("");
    } finally {
      setSubmitting(false);
    }
  };

  // На мобильной/виртуальной клавиатуре нажатие «ОК» по умолчанию вызывает
  // submit формы и одновременно автоматический фокус на следующем поле — это
  // приводит к произвольному увеличению масштаба webview Салюта. Перехватываем
  // Enter вручную: либо отправляем форму, либо просто закрываем клавиатуру.
  const handleKeyDown = (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    if (e.target && typeof e.target.blur === "function") {
      e.target.blur();
    }
    if (query && quantity && !submitting) {
      handleSubmit(e);
    }
  };

  return (
    <div className="card">
      <h2 className="card__title">Добавить акцию</h2>
      <form
        ref={formRef}
        className="add-form"
        onSubmit={handleSubmit}
        onKeyDown={handleKeyDown}
      >
        <input
          placeholder="Тикер или название (SBER, Сбер, Газпром...)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoComplete="off"
          enterKeyHint="next"
        />
        <input
          type="number"
          inputMode="numeric"
          min="1"
          placeholder="Количество"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          autoComplete="off"
          enterKeyHint="next"
        />
        <input
          type="number"
          inputMode="decimal"
          step="0.01"
          min="0"
          placeholder="Цена покупки"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          autoComplete="off"
          enterKeyHint="done"
        />
        <button className="btn" type="submit" disabled={submitting}>
          {submitting ? "..." : "Добавить"}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
