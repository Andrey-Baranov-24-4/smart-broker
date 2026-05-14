import React, { useState } from "react";

// Голосовой ввод теперь обеспечивает только Сбер Салют — через панель ассистента
// (createSmartappDebugger / нативный AssistantHost). Браузерный Web Speech API
// и SpeechSynthesis из этого компонента убраны намеренно.
//
// Текстовый ввод оставлен как ручной fallback для отладки.
export default function VoiceBar({ lastReply, onText }) {
  const [text, setText] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    // Закрываем системную клавиатуру до отправки, чтобы webview Салюта
    // не подхватил автоматический зум.
    if (document.activeElement && document.activeElement.blur) {
      document.activeElement.blur();
    }
    await onText(text);
    setText("");
  };

  return (
    <div className="card">
      <h2 className="card__title">Команды</h2>
      <form className="voice-bar" onSubmit={submit}>
        <input
          placeholder='Например: "Какая сейчас цена Яндекс?" или "Добавь Сбер по 300, количество 5"'
          value={text}
          onChange={(e) => setText(e.target.value)}
          autoComplete="off"
          enterKeyHint="send"
        />
        <button className="btn" type="submit">Отправить</button>
      </form>
      <div className="voice-log">
        {lastReply || "Скажите команду через Сбер Салют или введите её в поле выше."}
      </div>
    </div>
  );
}
