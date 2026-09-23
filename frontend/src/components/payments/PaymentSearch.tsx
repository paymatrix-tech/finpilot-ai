type PaymentSearchProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export function PaymentSearch({ value, onChange, onSubmit }: PaymentSearchProps) {
  return (
    <form
      className="relative"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label htmlFor="payment-search" className="sr-only">
        Search by ID, gateway, or error code
      </label>
      <span className="pointer-events-none absolute top-1/2 left-4 -translate-y-1/2 text-muted">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
          <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="1.8" />
          <path d="M20 20L16.5 16.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      </span>
      <input
        id="payment-search"
        type="search"
        placeholder="Search PAY-1001, R01, ExamplePay…"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-2xl border border-line bg-panel py-3.5 pr-24 pl-12 text-[15px] shadow-[0_10px_30px_rgba(28,25,21,0.04)] outline-none transition placeholder:text-muted/70 focus:border-accent focus:ring-4 focus:ring-accent/10"
      />
      <kbd className="absolute top-1/2 right-4 hidden -translate-y-1/2 rounded-md border border-line bg-page px-1.5 py-0.5 text-[11px] text-muted sm:inline">
        Enter
      </kbd>
    </form>
  );
}
