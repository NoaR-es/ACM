// Paleta de ACM (ADR-019): colores con contraste WCAG 2.1 AA verificado por tests (theme.test.ts).
// Texto: ≥ 4.5:1 sobre su fondo. Elementos gráficos (bordes de proyecto, semáforo): ≥ 3:1 sobre la superficie.

export type ThemeName = "light" | "dark";
export type Pair = { bg: string; fg: string };

export const STATUS_ORDER = [
  "PLANNED",
  "READY",
  "IN_PROGRESS",
  "BLOCKED",
  "IMPLEMENTED",
  "TESTING",
  "FAILED",
  "VERIFIED",
  "DONE",
  "CANCELLED",
  "DEPRECATED",
] as const;
export type StoryStatus = (typeof STATUS_ORDER)[number];

export const STATUS_LABEL: Record<StoryStatus, string> = {
  PLANNED: "Planificada",
  READY: "Lista (READY)",
  IN_PROGRESS: "En curso",
  BLOCKED: "Bloqueada",
  IMPLEMENTED: "Implementada",
  TESTING: "En pruebas",
  FAILED: "Fallida",
  VERIFIED: "Verificada",
  DONE: "Hecha (DONE)",
  CANCELLED: "Cancelada",
  DEPRECATED: "Obsoleta",
};

type Base = {
  bg: string;
  surface: string;
  surface2: string;
  text: string;
  muted: string;
  border: string;
  accent: string;
  accentText: string;
  danger: string;
  focus: string;
};

export type Palette = Base & {
  status: Record<StoryStatus, Pair>;
  semaphore: Record<"GREEN" | "AMBER" | "RED" | "UNKNOWN", Pair>;
  severity: Record<"CRITICAL" | "WARNING" | "REVIEW" | "INFO", Pair>;
  projects: { stripe: string; chip: Pair }[];
};

export const PALETTES: Record<ThemeName, Palette> = {
  light: {
    bg: "#f4f6f9",
    surface: "#ffffff",
    surface2: "#eef1f5",
    text: "#1b1f24",
    muted: "#4b5563",
    border: "#c9d1db",
    accent: "#0b5cad",
    accentText: "#ffffff",
    danger: "#b42318",
    focus: "#0b5cad",
    status: {
      PLANNED: { bg: "#e5e7eb", fg: "#1f2937" },
      READY: { bg: "#dbeafe", fg: "#1e3a8a" },
      IN_PROGRESS: { bg: "#ede9fe", fg: "#4c1d95" },
      BLOCKED: { bg: "#fee2e2", fg: "#7f1d1d" },
      IMPLEMENTED: { bg: "#ccfbf1", fg: "#134e4a" },
      TESTING: { bg: "#fef3c7", fg: "#78350f" },
      FAILED: { bg: "#fecaca", fg: "#7f1d1d" },
      VERIFIED: { bg: "#dcfce7", fg: "#14532d" },
      DONE: { bg: "#bbf7d0", fg: "#14532d" },
      CANCELLED: { bg: "#f3f4f6", fg: "#374151" },
      DEPRECATED: { bg: "#e2e8f0", fg: "#1e293b" },
    },
    semaphore: {
      GREEN: { bg: "#15803d", fg: "#ffffff" },
      AMBER: { bg: "#b45309", fg: "#ffffff" },
      RED: { bg: "#b91c1c", fg: "#ffffff" },
      UNKNOWN: { bg: "#4b5563", fg: "#ffffff" },
    },
    severity: {
      CRITICAL: { bg: "#fee2e2", fg: "#7f1d1d" },
      WARNING: { bg: "#fef3c7", fg: "#78350f" },
      REVIEW: { bg: "#ede9fe", fg: "#4c1d95" },
      INFO: { bg: "#e0f2fe", fg: "#0c4a6e" },
    },
    projects: [
      { stripe: "#2563eb", chip: { bg: "#dbeafe", fg: "#1e3a8a" } },
      { stripe: "#c2410c", chip: { bg: "#ffedd5", fg: "#7c2d12" } },
      { stripe: "#7e22ce", chip: { bg: "#f3e8ff", fg: "#581c87" } },
      { stripe: "#0f766e", chip: { bg: "#ccfbf1", fg: "#134e4a" } },
      { stripe: "#be185d", chip: { bg: "#fce7f3", fg: "#831843" } },
      { stripe: "#4d7c0f", chip: { bg: "#ecfccb", fg: "#365314" } },
      { stripe: "#0e7490", chip: { bg: "#cffafe", fg: "#164e63" } },
      { stripe: "#a16207", chip: { bg: "#fef9c3", fg: "#713f12" } },
    ],
  },
  dark: {
    bg: "#0d1117",
    surface: "#161b22",
    surface2: "#1f2630",
    text: "#e6edf3",
    muted: "#a8b3bf",
    border: "#3a4552",
    accent: "#6cb6ff",
    accentText: "#0d1117",
    danger: "#ff7b72",
    focus: "#6cb6ff",
    status: {
      PLANNED: { bg: "#374151", fg: "#f3f4f6" },
      READY: { bg: "#1e3a8a", fg: "#dbeafe" },
      IN_PROGRESS: { bg: "#4c1d95", fg: "#ede9fe" },
      BLOCKED: { bg: "#7f1d1d", fg: "#fee2e2" },
      IMPLEMENTED: { bg: "#134e4a", fg: "#ccfbf1" },
      TESTING: { bg: "#78350f", fg: "#fef3c7" },
      FAILED: { bg: "#991b1b", fg: "#fee2e2" },
      VERIFIED: { bg: "#14532d", fg: "#dcfce7" },
      DONE: { bg: "#166534", fg: "#dcfce7" },
      CANCELLED: { bg: "#1f2937", fg: "#d1d5db" },
      DEPRECATED: { bg: "#1e293b", fg: "#e2e8f0" },
    },
    semaphore: {
      GREEN: { bg: "#3fb950", fg: "#0d1117" },
      AMBER: { bg: "#d29922", fg: "#0d1117" },
      RED: { bg: "#f85149", fg: "#0d1117" },
      UNKNOWN: { bg: "#8b949e", fg: "#0d1117" },
    },
    severity: {
      CRITICAL: { bg: "#7f1d1d", fg: "#fee2e2" },
      WARNING: { bg: "#78350f", fg: "#fef3c7" },
      REVIEW: { bg: "#4c1d95", fg: "#ede9fe" },
      INFO: { bg: "#0c4a6e", fg: "#e0f2fe" },
    },
    projects: [
      { stripe: "#60a5fa", chip: { bg: "#1e3a8a", fg: "#dbeafe" } },
      { stripe: "#fb923c", chip: { bg: "#7c2d12", fg: "#ffedd5" } },
      { stripe: "#c084fc", chip: { bg: "#581c87", fg: "#f3e8ff" } },
      { stripe: "#2dd4bf", chip: { bg: "#134e4a", fg: "#ccfbf1" } },
      { stripe: "#f472b6", chip: { bg: "#831843", fg: "#fce7f3" } },
      { stripe: "#a3e635", chip: { bg: "#365314", fg: "#ecfccb" } },
      { stripe: "#22d3ee", chip: { bg: "#164e63", fg: "#cffafe" } },
      { stripe: "#facc15", chip: { bg: "#713f12", fg: "#fef9c3" } },
    ],
  },
};

// ---------------------------------------------------------------- contraste WCAG 2.1
function channel(c: number): number {
  const s = c / 255;
  return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
}

export function luminance(hex: string): number {
  const m = /^#([0-9a-f]{6})$/i.exec(hex);
  if (!m) throw new Error(`color inválido: ${hex}`);
  const n = parseInt(m[1], 16);
  return 0.2126 * channel((n >> 16) & 255) + 0.7152 * channel((n >> 8) & 255) + 0.0722 * channel(n & 255);
}

export function contrast(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Color estable por proyecto: el mismo proyecto conserva su color en todas las vistas. */
export function projectIndex(projectId: string, allIds: string[]): number {
  const sorted = [...allIds].sort();
  const i = sorted.indexOf(projectId);
  return (i < 0 ? 0 : i) % PALETTES.light.projects.length;
}

export function cssVariables(p: Palette): Record<string, string> {
  const vars: Record<string, string> = {
    "--bg": p.bg,
    "--surface": p.surface,
    "--surface2": p.surface2,
    "--text": p.text,
    "--muted": p.muted,
    "--border": p.border,
    "--accent": p.accent,
    "--accent-text": p.accentText,
    "--danger": p.danger,
    "--focus": p.focus,
  };
  for (const s of STATUS_ORDER) {
    vars[`--status-${s}-bg`] = p.status[s].bg;
    vars[`--status-${s}-fg`] = p.status[s].fg;
  }
  for (const [k, v] of Object.entries(p.semaphore)) {
    vars[`--sem-${k}-bg`] = v.bg;
    vars[`--sem-${k}-fg`] = v.fg;
  }
  for (const [k, v] of Object.entries(p.severity)) {
    vars[`--sev-${k}-bg`] = v.bg;
    vars[`--sev-${k}-fg`] = v.fg;
  }
  p.projects.forEach((c, i) => {
    vars[`--project-${i}-stripe`] = c.stripe;
    vars[`--project-${i}-bg`] = c.chip.bg;
    vars[`--project-${i}-fg`] = c.chip.fg;
  });
  return vars;
}
