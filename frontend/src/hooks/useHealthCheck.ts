import { useEffect, useState } from "react";

import { fetchHealth } from "../services/apiClient";
import type { HealthResponse } from "../types/health";

type HealthStatus = "checking" | "online" | "offline";

type HealthState = {
  status: HealthStatus;
  payload?: HealthResponse;
};

export function useHealthCheck(): HealthState {
  const [state, setState] = useState<HealthState>({ status: "checking" });

  useEffect(() => {
    const controller = new AbortController();

    async function loadHealth() {
      try {
        const payload = await fetchHealth(controller.signal);
        setState({ status: "online", payload });
      } catch {
        if (!controller.signal.aborted) {
          setState({ status: "offline" });
        }
      }
    }

    void loadHealth();

    return () => {
      controller.abort();
    };
  }, []);

  return state;
}
