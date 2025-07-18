import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleRegister = async () => {
    setError(null);
    setSuccess(null);
    const res = await fetch("http://localhost:8000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (res.ok) {
      setSuccess("Admin user created! You can now log in.");
      setTimeout(() => navigate("/"), 1500);
    } else {
      const data = await res.json();
      setError(data.detail || "Registration error.");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow-lg">
        <h2 className="text-2xl mb-4 font-semibold text-center">Create Admin</h2>
        {error && (
          <div className="mb-3 p-2 bg-red-100 text-red-700 rounded text-center">{error}</div>
        )}
        {success && (
          <div className="mb-3 p-2 bg-green-100 text-green-700 rounded text-center">{success}</div>
        )}
        <input
          type="text"
          placeholder="Username"
          className="mb-3 w-full p-2 rounded"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="mb-3 w-full p-2 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          onClick={handleRegister}
        >
          Create Admin
        </button>
      </div>
    </div>
  );
};

export default Register;