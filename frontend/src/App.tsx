// App.tsx - Entry point del frontend React
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ContainerDetails from "./pages/ContainerDetails";
import Images from "./pages/Images";
import RequireAuth from "./components/RequireAuth";
import "./styles.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/container/:id" element={<RequireAuth><ContainerDetails /></RequireAuth>} />
        <Route path="/images" element={<RequireAuth><Images /></RequireAuth>} />
      </Routes>
    </Router>
  );
}

export default App;