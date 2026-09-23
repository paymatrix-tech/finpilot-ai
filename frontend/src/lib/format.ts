const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function formatAmount(amount: string, code: string): string {
  const value = Number(amount);
  if (Number.isNaN(value) || code !== "USD") {
    return `${amount} ${code}`;
  }
  return currency.format(value);
}
