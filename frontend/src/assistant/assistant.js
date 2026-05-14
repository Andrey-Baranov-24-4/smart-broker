import { createAssistant, createSmartappDebugger } from "@salutejs/client";

const INITIAL_DATA = { action: { action_id: "smart-broker/hello" } };

function getToken() {
  return process.env.REACT_APP_TOKEN;
}

function getSmartApp() {
  return process.env.REACT_APP_SMARTAPP || "smart-broker";
}

// Заглушка для запуска в обычном браузере (без Salute host и без токена отладчика).
// Позволяет странице работать — текстовая голосовая строка продолжает обращаться к backend.
function createNoopAssistant() {
  const listeners = new Set();
  return {
    on(event, cb) {
      if (event === "data") listeners.add(cb);
      return () => listeners.delete(cb);
    },
    sendData() {},
    sendAction() {},
    close() {
      listeners.clear();
    },
  };
}

// Оборачиваем методы ассистента в try/catch, чтобы неожиданные ошибки
// из внутреннего WebSocket-клиента @salutejs/client не падали в overlay.
function wrapSafe(assistant) {
  if (!assistant) return createNoopAssistant();
  const origOn = assistant.on?.bind(assistant);
  const origSendData = assistant.sendData?.bind(assistant);
  const origSendAction = assistant.sendAction?.bind(assistant);
  return {
    ...assistant,
    on(event, cb) {
      try {
        return origOn?.(event, (...args) => {
          try {
            cb(...args);
          } catch (e) {
            console.warn("[assistant] listener error:", e);
          }
        });
      } catch (e) {
        console.warn("[assistant] on() failed:", e);
        return () => {};
      }
    },
    sendData(...args) {
      try {
        return origSendData?.(...args);
      } catch (e) {
        console.warn("[assistant] sendData failed:", e);
      }
    },
    sendAction(...args) {
      try {
        return origSendAction?.(...args);
      } catch (e) {
        console.warn("[assistant] sendAction failed:", e);
      }
    },
  };
}

export function initAssistant(getState) {
  try {
    const token = getToken();
    if (token) {
      return wrapSafe(
        createSmartappDebugger({
          token,
          initPhrase: `Запусти ${getSmartApp()}`,
          getState,
          nativePanel: {
            defaultText: "покажи портфель",
            screenshotMode: false,
            tabIndex: -1,
          },
        })
      );
    }

    if (typeof window !== "undefined" && window.AssistantHost) {
      return wrapSafe(createAssistant({ getState, initialData: INITIAL_DATA }));
    }
  } catch (e) {
    console.warn("[assistant] init failed, using noop:", e);
  }

  return createNoopAssistant();
}
