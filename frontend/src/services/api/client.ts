import axios from "axios";

import { appConfig } from "../../config/env";

// Use the standardized config (which checks VITE_API_BASE_URL)
const API_URL = `${appConfig.apiBaseUrl}/api/v1`;

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle 401s
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      // Could trigger a custom event here to log the user out
      window.dispatchEvent(new Event("auth-unauthorized"));
    }
    return Promise.reject(error);
  }
);
