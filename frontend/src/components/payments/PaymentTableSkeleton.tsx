export function PaymentTableSkeleton() {
  return (
    <div className="space-y-0 divide-y divide-line/80">
      {Array.from({ length: 8 }).map((_, index) => (
        <div key={index} className="grid grid-cols-5 gap-4 px-5 py-4">
          <div className="h-4 w-24 animate-pulse rounded bg-line/80" />
          <div className="h-4 w-16 animate-pulse rounded bg-line/80" />
          <div className="h-4 w-16 animate-pulse rounded bg-line/80" />
          <div className="h-4 w-24 animate-pulse rounded bg-line/80" />
          <div className="h-4 w-12 animate-pulse rounded bg-line/80" />
        </div>
      ))}
    </div>
  );
}
