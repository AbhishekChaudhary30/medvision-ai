import { appConfig } from "../config/env";
import type { HealthResponse } from "../types/health";

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${appConfig.apiBaseUrl}/api/v1/health`, { signal });

  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}
