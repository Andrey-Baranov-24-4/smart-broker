import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api/client";
import { initAssistant } from "../assistant/assistant";
import AddStock from "../components/AddStock";
import PortfolioChart from "../components/PortfolioChart";
import PortfolioSummary from "../components/PortfolioSummary";
import StockList from "../components/StockList";
import VoiceBar from "../components/VoiceBar";

export default function Portfolio() {
  const [portfolio, setPortfolio] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [voiceReply, setVoiceReply] = useState("");
  const assistantRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const [p, h] = await Promise.all([api.getPortfolio(), api.getHistory()]);
      setPortfolio(p);
      setHistory(h);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 30000);
    return () => clearInterval(id);
  }, [refresh]);

  const handleVoiceText = useCallback(
    async (text) => {
      try {
        const response = await api.sendVoiceCommand(text);
        setVoiceReply(response.reply);
        if (assistantRef.current) {
          assistantRef.current.sendData({
            action: { action_id: "voice_reply", parameters: { text: response.reply } },
          });
        }
        await refresh();
      } catch (e) {
        setVoiceReply(`Ошибка: ${e.message}`);
      }
    },
    [refresh]
  );

  useEffect(() => {
    const state = () => ({
      item_selector: {
        items:
          (portfolio?.positions || []).map((p, idx) => ({
            number: idx + 1,
            id: p.id,
            title: p.name,
          })) || [],
      },
    });

    const assistant = initAssistant(state);
    assistantRef.current = assistant;

    const unsubscribe = assistant.on("data", (event) => {
      if (event?.type === "smart_app_data" && event.smart_app_data?.text) {
        handleVoiceText(event.smart_app_data.text);
      } else if (event?.action?.type === "voice_text" && event.action.parameters?.text) {
        handleVoiceText(event.action.parameters.text);
      }
    });

    return () => {
      if (typeof unsubscribe === "function") unsubscribe();
    };
  }, [portfolio, handleVoiceText]);

  const handleAdd = useCallback(
    async (payload) => {
      setError("");
      try {
        await api.addPosition(payload);
        await refresh();
      } catch (e) {
        setError(e.message);
      }
    },
    [refresh]
  );

  const handleDelete = useCallback(
    async (id) => {
      try {
        await api.deletePosition(id);
        await refresh();
      } catch (e) {
        setError(e.message);
      }
    },
    [refresh]
  );

  const positions = useMemo(() => portfolio?.positions || [], [portfolio]);

  return (
    <>
      <PortfolioSummary portfolio={portfolio} />
      <VoiceBar lastReply={voiceReply} onText={handleVoiceText} />
      <AddStock onAdd={handleAdd} error={error} />
      <StockList positions={positions} onDelete={handleDelete} />
      <PortfolioChart history={history} />
    </>
  );
}
