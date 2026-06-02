import React from "react";
import { Navigate } from "react-router-dom";

const RequireAuth = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/" />;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      localStorage.removeItem("token");
      return <Navigate to="/" />;
    }
  } catch {
    localStorage.removeItem("token");
    return <Navigate to="/" />;
  }
  return children;
};

export default RequireAuth;
