import axios from "axios";

console.log('process.env.NEXT_PUBLIC_API_URL', process.env.NEXT_PUBLIC_API_URL);
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Optional: Add a request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); // Or use cookies/session as needed
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;