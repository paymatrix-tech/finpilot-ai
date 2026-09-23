import { Link, Outlet } from "react-router-dom";
import { useApiHealth } from "../../hooks/useApiHealth";

export function AppShell() {
  const healthQuery = useApiHealth();
  const apiOnline = healthQuery.data === true;
  const apiStatusLabel = healthQuery.isPending
    ? "Checking API…"
    : apiOnline
      ? "API connected"
      : "API unavailable";

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(15,92,86,0.12),transparent_32%),radial-gradient(circle_at_80%_0%,rgba(181,106,60,0.1),transparent_28%)]"
      />
      <header className="relative border-b border-line/80 bg-panel/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-5 py-4">
          <Link to="/" className="flex items-center gap-3 text-ink no-underline">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-accent font-display text-sm text-panel">
              Fp
            </span>
            <span>
              <span className="block font-display text-xl leading-none">FinPilot</span>
              <span className="text-xs tracking-[0.14em] text-muted uppercase">
                Payment investigation
              </span>
            </span>
          </Link>
          <p
            className={`text-xs font-medium tracking-wide uppercase ${
              apiOnline ? "text-accent" : "text-copper"
            }`}
            title={apiStatusLabel}
          >
            <span
              aria-hidden
              className={`mr-2 inline-block h-2 w-2 rounded-full ${
                apiOnline ? "bg-accent" : "bg-copper"
              }`}
            />
            {apiStatusLabel}
          </p>
        </div>
      </header>
      <main className="relative mx-auto w-full max-w-6xl px-5 py-8 sm:py-10">
        <Outlet />
      </main>
    </div>
  );
}
