// pages/Login.tsx - Login con sfondo dinamico
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const backgrounds = [
  "https://source.unsplash.com/random/1920x1080?sea",
  "https://source.unsplash.com/random/1920x1080?mountains",
  "https://source.unsplash.com/random/1920x1080?forest"
];

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [bg, setBg] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const randomBg = backgrounds[Math.floor(Math.random() * backgrounds.length)];
    setBg(randomBg);
  }, []);

  const handleLogin = async () => {
    setError(null);
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password })
    });
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
    } else {
      setError("Login failed: invalid username or password.");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-cover bg-center" style={{ backgroundImage: `url(${bg})` }}>
      <div className="bg-white bg-opacity-80 p-8 rounded-xl shadow-lg">
        <h2 className="text-2xl mb-4 font-semibold text-center">Login</h2>
        {error && (
          <div className="mb-3 p-2 bg-red-100 text-red-700 rounded text-center">{error}</div>
        )}
        <input type="text" placeholder="Username" className="mb-3 w-full p-2 rounded" onChange={(e) => setUsername(e.target.value)} />
        <input type="password" placeholder="Password" className="mb-3 w-full p-2 rounded" onChange={(e) => setPassword(e.target.value)} />
        <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700" onClick={handleLogin}>Login</button>
      </div>
    </div>
  );
};

export default Login;