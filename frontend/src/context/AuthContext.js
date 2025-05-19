"use client";

import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState(null);
  const [role, setRole] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUsername = localStorage.getItem("username");
    const storedRole = localStorage.getItem("role");
    if (storedToken) setToken(storedToken);
    if (storedUsername) setUsername(JSON.parse(storedUsername));
    if (storedRole) setRole(JSON.parse(storedRole));
  }, []);

  const login = (token, username, role) => {
    setToken(token);
    setUsername(username);
    setRole(role);
    localStorage.setItem("token", token);
    localStorage.setItem("username", JSON.stringify(username));
    localStorage.setItem("role", JSON.stringify(role));
  };

  const logout = () => {
    setToken(null);
    setUsername(null);
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
  };

  return (
    <AuthContext.Provider value={{ token, username, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}