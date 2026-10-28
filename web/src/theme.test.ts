// Tests de la paleta (US-31.07): contraste WCAG AA de texto, franjas y semáforo en ambos temas.
import { describe, expect, it } from "vitest";
import { contrast, cssVariables, PALETTES, projectIndex, STATUS_ORDER, type ThemeName } from "./theme";

const THEMES: ThemeName[] = ["light", "dark"];
const AA_TEXT = 4.5;
const AA_GRAPHIC = 3;

describe("contraste WCAG AA de la paleta (US-07-A11Y)", () => {
  it("calcula el contraste de referencia (negro/blanco = 21)", () => {
    expect(contrast("#000000", "#ffffff")).toBeCloseTo(21, 5);
    expect(contrast("#ffffff", "#ffffff")).toBeCloseTo(1, 5);
  });

  for (const name of THEMES) {
    const p = PALETTES[name];
    it(`${name}: texto base, atenuado y acento sobre fondo y superficies`, () => {
      for (const bg of [p.bg, p.surface, p.surface2]) {
        expect(contrast(p.text, bg)).toBeGreaterThanOrEqual(AA_TEXT);
        expect(contrast(p.muted, bg)).toBeGreaterThanOrEqual(AA_TEXT);
        expect(contrast(p.accent, bg)).toBeGreaterThanOrEqual(AA_TEXT);
        expect(contrast(p.danger, bg)).toBeGreaterThanOrEqual(AA_TEXT);
      }
      expect(contrast(p.accentText, p.accent)).toBeGreaterThanOrEqual(AA_TEXT);
    });

    it(`${name}: cada estado, semáforo y severidad legible`, () => {
      for (const s of STATUS_ORDER) expect(contrast(p.status[s].fg, p.status[s].bg), s).toBeGreaterThanOrEqual(AA_TEXT);
      for (const [k, v] of Object.entries(p.semaphore)) expect(contrast(v.fg, v.bg), k).toBeGreaterThanOrEqual(AA_TEXT);
      for (const [k, v] of Object.entries(p.severity)) expect(contrast(v.fg, v.bg), k).toBeGreaterThanOrEqual(AA_TEXT);
    });

    it(`${name}: colores de proyecto (etiqueta legible y franja visible)`, () => {
      for (const c of p.projects) {
        expect(contrast(c.chip.fg, c.chip.bg)).toBeGreaterThanOrEqual(AA_TEXT);
        expect(contrast(c.stripe, p.surface)).toBeGreaterThanOrEqual(AA_GRAPHIC);
      }
      expect(p.projects.length).toBe(PALETTES.light.projects.length);
      expect(new Set(p.projects.map((c) => c.stripe)).size).toBe(p.projects.length);
    });

    it(`${name}: semáforo distinguible de la superficie`, () => {
      for (const v of Object.values(p.semaphore)) expect(contrast(v.bg, p.surface)).toBeGreaterThanOrEqual(AA_GRAPHIC);
    });
  }

  it("las variables CSS cubren todos los estados y proyectos", () => {
    const vars = cssVariables(PALETTES.light);
    for (const s of STATUS_ORDER) expect(vars[`--status-${s}-bg`]).toBeDefined();
    expect(vars["--project-7-stripe"]).toBeDefined();
  });

  it("cada proyecto conserva su color con independencia del orden de la lista", () => {
    expect(projectIndex("beta", ["gamma", "alpha", "beta"])).toBe(projectIndex("beta", ["alpha", "beta", "gamma"]));
    expect(projectIndex("alpha", ["alpha", "beta"])).not.toBe(projectIndex("beta", ["alpha", "beta"]));
  });
});
