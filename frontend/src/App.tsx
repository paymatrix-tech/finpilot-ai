import { useEffect, useState } from "react";

type Health = {
  status: string;
  service: string;
  database: string;
};

type LoadState =
  | { kind: "loading" }
  | { kind: "ready"; health: Health }
  | { kind: "error"; message: string };

export function App() {
  const [state, setState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function loadHealth() {
      try {
        const response = await fetch("/health");
        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }
        const health = (await response.json()) as Health;
        if (!cancelled) {
          setState({ kind: "ready", health });
        }
      } catch (error) {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : "Request failed";
          setState({ kind: "error", message });
        }
      }
    }

    void loadHealth();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main>
      <p className="eyebrow">Payment investigation</p>
      <h1>FinPilot</h1>
      <p className="lede">Local stack status for the Day 1 foundation.</p>
      <section aria-live="polite">
        {state.kind === "loading" && <p>Checking API…</p>}
        {state.kind === "error" && (
          <p className="error">API unreachable. {state.message}</p>
        )}
        {state.kind === "ready" && (
          <dl>
            <div>
              <dt>API</dt>
              <dd>{state.health.status}</dd>
            </div>
            <div>
              <dt>Service</dt>
              <dd>{state.health.service}</dd>
            </div>
            <div>
              <dt>Database</dt>
              <dd>{state.health.database}</dd>
            </div>
          </dl>
        )}
      </section>
    </main>
  );
}
