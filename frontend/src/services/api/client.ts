import axios from "axios";

// Hardcode to Hugging Face to ignore Vercel's cached Render VITE_API_URL
const API_URL = "https://abhishek1130-medvision-api.hf.space/call";

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Mock interceptor to handle mock responses for paths that don't exist in Gradio
apiClient.interceptors.request.use((config) => {
  // Add a fake token just in case
  if (config.headers) {
    config.headers.Authorization = `Bearer mock-token-123`;
  }
  return config;
});

// We don't need the 401 interceptor since we don't have a backend auth anymore
