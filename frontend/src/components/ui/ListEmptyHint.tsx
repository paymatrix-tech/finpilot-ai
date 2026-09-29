type ListEmptyHintProps = {
  children: string;
};

export function ListEmptyHint({ children }: ListEmptyHintProps) {
  return (
    <p className="rounded-2xl border border-dashed border-line bg-page/80 px-4 py-6 text-center text-sm text-muted">
      {children}
    </p>
  );
}
