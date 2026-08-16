import { useHealthCheck } from "../hooks/useHealthCheck";

const statusLabels = {
  checking: "Checking API",
  online: "API healthy",
  offline: "API offline",
} as const;

export function AppStatus() {
  const health = useHealthCheck();

  return (
    <section className="status-panel" aria-label="Application status">
      <div>
        <span className={`status-dot status-dot-${health.status}`} />
        <span className="status-label">{statusLabels[health.status]}</span>
      </div>
      <dl>
        <div>
          <dt>Service</dt>
          <dd>{health.payload?.service ?? "MedVision AI"}</dd>
        </div>
        <div>
          <dt>Environment</dt>
          <dd>{health.payload?.environment ?? "local"}</dd>
        </div>
        <div>
          <dt>API Version</dt>
          <dd>{health.payload?.version ?? "0.1.0"}</dd>
        </div>
      </dl>
    </section>
  );
}
