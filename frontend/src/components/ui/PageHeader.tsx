import type { ReactNode } from "react";

type PageHeaderProps = {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  meta?: ReactNode;
  align?: "left" | "center";
};

export function PageHeader({
  eyebrow,
  title,
  description,
  meta,
  align = "left",
}: PageHeaderProps) {
  const centered = align === "center";

  return (
    <header className={`space-y-3 ${centered ? "text-center" : ""}`}>
      {eyebrow && (
        <p className="text-xs font-semibold tracking-[0.16em] text-muted uppercase">{eyebrow}</p>
      )}
      <h1
        className={`font-display text-3xl font-medium tracking-tight text-balance sm:text-4xl ${
          centered ? "mx-auto max-w-lg" : ""
        }`}
      >
        {title}
      </h1>
      {description && (
        <p
          className={`text-sm leading-relaxed text-muted sm:text-[15px] ${
            centered ? "mx-auto max-w-md" : "max-w-2xl"
          }`}
        >
          {description}
        </p>
      )}
      {meta && <div className={`text-sm text-muted ${centered ? "" : ""}`}>{meta}</div>}
    </header>
  );
}
