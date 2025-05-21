"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from 'next/navigation';
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const router = useRouter();
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState(null);
  const [role, setRole] = useState(null);

  const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      if (!decoded.exp) return true;
      return Date.now() >= decoded.exp * 1000;
    } catch {
      return true;
    }
  };

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUsername = localStorage.getItem("username");
    const storedRole = localStorage.getItem("role");
    if (storedToken && !isTokenExpired(storedToken)) {
      setToken(storedToken);
      if (storedUsername) setUsername(JSON.parse(storedUsername));
      if (storedRole) setRole(JSON.parse(storedRole));
    } else {
      setToken(null);
      setUsername(null);
      setRole(null);
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      localStorage.removeItem("role");
      
      if (storedToken && isTokenExpired(storedToken)) {
        router.push("/login");
      }
    }
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