// Documentación en Markdown (skills, US-15.08..10) renderizada y saneada: nunca HTML ejecutable (XSS).
import DOMPurify from "dompurify";
import { marked } from "marked";

/** Separa el frontmatter YAML (--- … ---) del cuerpo. */
export function splitFrontmatter(text: string): { frontmatter: string; body: string } {
  const m = /^---\n([\s\S]*?)\n---\n?/.exec(text);
  return m ? { frontmatter: m[1], body: text.slice(m[0].length) } : { frontmatter: "", body: text };
}

export function renderMarkdown(text: string): string {
  const html = marked.parse(text, { async: false, gfm: true }) as string;
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
}
