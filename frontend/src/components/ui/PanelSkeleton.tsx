type PanelSkeletonProps = {
  lines?: number;
};

export function PanelSkeleton({ lines = 3 }: PanelSkeletonProps) {
  const widths = ["w-3/4", "w-1/2", "w-2/3", "w-5/6"];

  return (
    <div className="animate-pulse space-y-3" aria-hidden>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`h-4 rounded bg-line/50 ${widths[index % widths.length]}`}
        />
      ))}
    </div>
  );
}
