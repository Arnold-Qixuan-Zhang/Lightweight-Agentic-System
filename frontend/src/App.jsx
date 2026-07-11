import { useCallback, useEffect, useState } from "react";
import { exportHistory, getHistory, submitTask } from "./api/client";
import ExecutionTrace from "./components/ExecutionTrace";
import HistoryPanel from "./components/HistoryPanel";
import InstructionInput from "./components/InstructionInput";
import "./index.css";

export default function App() {
  const [trace, setTrace] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const records = await getHistory();
      setHistory(records);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleSubmit = async (instruction) => {
    setLoading(true);
    setError(null);
    setTrace([]);
    setResult(null);

    try {
      const response = await submitTask(instruction);
      setTrace(response.trace);
      setResult(response.result);
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectHistory = (record) => {
    setTrace(record.trace);
    setResult(record.result);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Agentic AI Demo</h1>
        <p>
          A lightweight agent that routes your instruction to the right tool and
          shows each step of execution.
        </p>
      </header>

      <main className="app-main">
        <InstructionInput onSubmit={handleSubmit} loading={loading} />
        <ExecutionTrace trace={trace} result={result} error={error} />
        <HistoryPanel
          history={history}
          onSelect={handleSelectHistory}
          onExport={exportHistory}
          loading={historyLoading}
        />
      </main>
    </div>
  );
}
