import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaUser, FaLock, FaSignInAlt } from "react-icons/fa";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isUsernameFocused, setIsUsernameFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError(null);
    const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
    const res = await fetch(`${API_URL}/auth/login`, {
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-800 relative">
      <div className="absolute inset-0 bg-gradient-to-br from-black/60 via-blue-900/40 to-blue-700/30 backdrop-blur-sm z-0" />
      <div className="relative z-10 w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center shadow-lg mb-2 border-4 border-white/70">
            <span className="text-blue-600 text-4xl"><FaUser /></span>
          </div>
          <h2 className="text-3xl font-extrabold text-white drop-shadow mb-1 text-center">Sign in to DockerWebUI</h2>
          <p className="text-blue-100 text-sm mb-2 text-center">Manage your Docker containers with style</p>
        </div>
        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl">
          {error && (
            <div className="mb-4 p-3 bg-red-200/80 text-red-800 rounded text-center font-semibold animate-shake shadow">
              {error}
            </div>
          )}
          <div className="mb-5 relative">
            <FaUser className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-400 text-lg" />
            <input
              type="text"
              id="username"
              className="peer w-full pl-10 pr-3 py-3 pt-5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white/70 placeholder-transparent transition"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onFocus={() => setIsUsernameFocused(true)}
              onBlur={() => setIsUsernameFocused(false)}
              autoFocus
              placeholder="Username"
              required
            />
            <label
              htmlFor="username"
              className={`absolute left-10 pointer-events-none transition-all duration-200 \
                ${(username || isUsernameFocused)
                  ? '-top-5 text-xs text-blue-500'
                  : 'top-1/2 -translate-y-1/2 text-base text-gray-400'}`}
            >
              Username
            </label>
          </div>
          <div className="mb-7 relative">
            <FaLock className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-400 text-lg" />
            <input
              type="password"
              id="password"
              className="peer w-full pl-10 pr-3 py-3 pt-5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white/70 placeholder-transparent transition"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onFocus={() => setIsPasswordFocused(true)}
              onBlur={() => setIsPasswordFocused(false)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
              placeholder="Password"
              required
            />
            <label
              htmlFor="password"
              className={`absolute left-10 pointer-events-none transition-all duration-200 \
                ${(password || isPasswordFocused)
                  ? '-top-5 text-xs text-blue-500'
                  : 'top-1/2 -translate-y-1/2 text-base text-gray-400'}`}
            >
              Password
            </label>
          </div>
          <button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-bold py-3 rounded-lg shadow-lg flex items-center justify-center gap-2 text-lg transition-all duration-200 active:scale-95 focus:outline-none focus:ring-2 focus:ring-blue-400"
            onClick={handleLogin}
          >
            <FaSignInAlt className="text-xl" /> Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
