export const appConfig = {
  appName: "MedVision AI",
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/+$/, ""),
} as const;
