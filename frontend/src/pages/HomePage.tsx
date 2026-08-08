import { AppStatus } from "../components/AppStatus";

export function HomePage() {
  return (
    <div className="workspace-grid">
      <section className="intro-panel" aria-labelledby="intro-title">
        <p className="section-label">Foundation ready</p>
        <h2 id="intro-title">Explainable medical image analysis architecture</h2>
        <p>
          MedVision AI is currently scoped to repository foundations, API health, configuration,
          Docker, testing, documentation, and clean boundaries for future ML work.
        </p>
      </section>
      <AppStatus />
    </div>
  );
}
