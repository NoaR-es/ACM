// Tests del Markdown seguro (US-45.02): saneado de HTML ejecutable y frontmatter.
import { describe, expect, it } from "vitest";
import { renderMarkdown, splitFrontmatter } from "./markdown";

describe("documentación en Markdown", () => {
  it("renderiza títulos, tablas y código", () => {
    const html = renderMarkdown("# Título\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n`acm_decide`");
    expect(html).toContain("<h1");
    expect(html).toContain("<table>");
    expect(html).toContain("<code>acm_decide</code>");
  });

  it("elimina HTML ejecutable (XSS)", () => {
    const html = renderMarkdown('<img src=x onerror="alert(1)"><script>alert(2)</script>[x](javascript:alert(3))');
    expect(html).not.toContain("onerror");
    expect(html).not.toContain("<script");
    expect(html).not.toContain("javascript:");
  });

  it("separa el frontmatter", () => {
    const { frontmatter, body } = splitFrontmatter("---\nname: acm-schema\nversion: 1.4.0\n---\n\n# ACM");
    expect(frontmatter).toContain("version: 1.4.0");
    expect(body.trim()).toBe("# ACM");
  });
});
