import { useCallback, useEffect, useRef, useState } from "react";

// Браузерный Web Speech API: распознавание голоса + озвучка ответа.
// Работает в Chrome, Edge, Opera, Safari. В Firefox распознавание отсутствует.
export default function useSpeech({ lang = "ru-RU", onResult } = {}) {
  const recognitionRef = useRef(null);
  const onResultRef = useRef(onResult);
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(false);
  const [interim, setInterim] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    onResultRef.current = onResult;
  }, [onResult]);

  useEffect(() => {
    const SR =
      typeof window !== "undefined" &&
      (window.SpeechRecognition || window.webkitSpeechRecognition);
    if (!SR) {
      setSupported(false);
      return undefined;
    }

    const rec = new SR();
    rec.lang = lang;
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;

    rec.onstart = () => {
      setListening(true);
      setError("");
      setInterim("");
    };
    rec.onend = () => {
      setListening(false);
      setInterim("");
    };
    rec.onerror = (e) => {
      setListening(false);
      setInterim("");
      setError(e.error || "recognition_error");
    };
    rec.onresult = (event) => {
      let finalText = "";
      let interimText = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript;
        } else {
          interimText += result[0].transcript;
        }
      }
      if (finalText) {
        setInterim("");
        if (onResultRef.current) onResultRef.current(finalText.trim());
      } else {
        setInterim(interimText);
      }
    };

    recognitionRef.current = rec;
    setSupported(true);
    return () => {
      try {
        rec.onresult = null;
        rec.onend = null;
        rec.onerror = null;
        rec.onstart = null;
        rec.abort();
      } catch (_) {
        // ignore
      }
    };
  }, [lang]);

  const start = useCallback(() => {
    const rec = recognitionRef.current;
    if (!rec || listening) return;
    try {
      rec.start();
    } catch (e) {
      setError("already_started");
    }
  }, [listening]);

  const stop = useCallback(() => {
    const rec = recognitionRef.current;
    if (!rec) return;
    try {
      rec.stop();
    } catch (_) {
      // ignore
    }
  }, []);

  const speak = useCallback(
    (text) => {
      if (!text || typeof window === "undefined" || !window.speechSynthesis) return;
      try {
        window.speechSynthesis.cancel();
        const utter = new window.SpeechSynthesisUtterance(text);
        utter.lang = lang;
        utter.rate = 1.0;
        utter.pitch = 1.0;
        window.speechSynthesis.speak(utter);
      } catch (_) {
        // ignore
      }
    },
    [lang]
  );

  return { listening, supported, interim, error, start, stop, speak };
}
