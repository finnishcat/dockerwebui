// pages/Dashboard.tsx - Dashboard base con container list
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const [containers, setContainers] = useState([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchContainers = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/docker/containers/local", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Error loading containers");
        const data = await res.json();
        setContainers(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Unknown error");
      } finally {
        setLoading(false);
      }
    };
    fetchContainers();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Active Containers</h1>
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}
      {loading ? (
        <div className="text-center py-10">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {containers.map((c: any) => (
            <div
              key={c.id}
              className="p-4 bg-white rounded-xl shadow hover:shadow-lg transition cursor-pointer"
              onClick={() => navigate(`/container/${c.id}`)}
            >
              <h2 className="text-lg font-semibold">{c.name}</h2>
              <p className="text-sm text-gray-600">Image: {c.image?.[0] || "unknown"}</p>
              <p className="text-sm text-gray-600">Status: {c.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
