import type { ReactNode } from "react";

import { appConfig } from "../config/env";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Clinical AI research workspace</p>
          <h1>{appConfig.appName}</h1>
        </div>
        <p className="phase-badge">Phase 1</p>
      </header>
      <main>{children}</main>
      <footer>
        Research and educational clinical decision-support prototype. Not for definitive diagnosis.
      </footer>
    </div>
  );
}
