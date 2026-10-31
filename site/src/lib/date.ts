// "2026-11-01" → "1er novembre 2026"
export const frDate = (iso: string) =>
  new Date(`${iso}T12:00:00Z`)
    .toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" })
    .replace(/^1 /, "1er ");

// "2026-10-30" → "30 oct. 2026"
export const frDateShort = (iso: string) =>
  new Date(`${iso}T12:00:00Z`)
    .toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" })
    .replace(/^1 /, "1er ");
