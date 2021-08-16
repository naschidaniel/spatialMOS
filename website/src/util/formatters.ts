export function formatDate(date: number | undefined): string {
  return date === undefined
    ? "–"
    : new Intl.DateTimeFormat("de-AT", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      }).format(date);
}

export function formatDateTime(date: number | undefined): string {
  return date === undefined
    ? "–"
    : new Intl.DateTimeFormat("de-AT", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
}
