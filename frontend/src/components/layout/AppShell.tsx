import { Link, Outlet } from "react-router-dom";

export function AppShell() {
  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(15,92,86,0.12),transparent_32%),radial-gradient(circle_at_80%_0%,rgba(181,106,60,0.1),transparent_28%)]"
      />
      <header className="relative border-b border-line/80 bg-panel/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-5 py-4">
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
        </div>
      </header>
      <main className="relative mx-auto w-full max-w-6xl px-5 py-8 sm:py-10">
        <Outlet />
      </main>
    </div>
  );
}
