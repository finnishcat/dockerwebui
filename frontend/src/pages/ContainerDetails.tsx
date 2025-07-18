// pages/ContainerDetails.tsx - Dettagli container + log realtime + azioni + stats
import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";

const ContainerDetails = () => {
  const { id } = useParams();
  const [logs, setLogs] = useState("");
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:8000/docker/stats/local/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Error loading stats");
      const data = await res.json();
      setStats(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: "restart" | "stop" | "remove") => {
    setActionLoading(true);
    setActionMsg(null);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://localhost:8000/docker/container/${action}/local/${id}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(`Error performing ${action} action`);
      setActionMsg(`Action ${action} completed successfully.`);
      if (action === "stop" || action === "remove") {
        setStats(null);
      } else {
        fetchStats();
      }
    } catch (err: any) {
      setError(err.message || "Errore sconosciuto");
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    ws.current = new WebSocket(`ws://localhost:8000/ws/logs/local/${id}?token=${token}`);
    ws.current.onmessage = (e) => setLogs((prev) => prev + e.data + "\n");
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => {
      ws.current?.close();
      clearInterval(interval);
    };
    // eslint-disable-next-line
  }, [id]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Container Details - {id}</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}
      {actionMsg && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">{actionMsg}</div>
      )}

      <div className="mb-4 space-x-2">
        <button
          className="bg-yellow-500 text-white px-4 py-2 rounded"
          onClick={() => handleAction("restart")}
          disabled={actionLoading}
        >
          Restart
        </button>
        <button
          className="bg-red-500 text-white px-4 py-2 rounded"
          onClick={() => handleAction("stop")}
          disabled={actionLoading}
        >
          Stop
        </button>
        <button
          className="bg-gray-600 text-white px-4 py-2 rounded"
          onClick={() => handleAction("remove")}
          disabled={actionLoading}
        >
          Remove
        </button>
      </div>

      {loading ? (
        <div className="text-center py-10">Loading stats...</div>
      ) : stats ? (
        <div className="mb-4 bg-white p-4 rounded-xl shadow">
          <p>
            <strong>CPU:</strong> {stats.cpu.toFixed(2)}%
          </p>
          <p>
            <strong>RAM:</strong> {stats.memory_usage} / {stats.memory_limit} MB
          </p>
          <p>
            <strong>Net I/O:</strong> {stats.network_rx} ↓ / {stats.network_tx} ↑
          </p>
        </div>
      ) : (
        <div className="mb-4 text-gray-500">No statistics available.</div>
      )}

      <h2 className="text-xl font-semibold mb-2">Realtime Log</h2>
      <pre className="bg-black text-green-400 p-4 rounded-xl h-[50vh] overflow-auto text-sm">
        {logs || "Waiting for logs..."}
      </pre>
    </div>
  );
};

export default ContainerDetails;
