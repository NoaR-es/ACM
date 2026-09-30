# Visión de producto

> Resumen. Texto íntegro: `01_PRODUCTO/product_definition_v3.md` §1, §17, §18 y `01_PRODUCTO/backlog_completo_v1.md`.

ACM es una **memoria operativa verificable del desarrollo software**: un motor de estado, conocimiento, gobernanza,
ejecución y trazabilidad que permite a múltiples agentes IA trabajar de forma autónoma sobre múltiples proyectos
sin perder contexto ni trazabilidad.

Debe poder responder en cualquier momento: qué está ocurriendo, quién lo hace, por qué, qué requisito lo justifica,
qué riesgos existen, qué código está afectado, qué evidencia demuestra que funciona y qué debería ocurrir después.

## Cadena de trazabilidad objetivo
Visión → Módulo → Feature → Épica → Historia → Requisito/AC → Sprint → Tarea → Plan → Código → Commit → Walkthrough → Log → Bug → Causa raíz → ADR → Documentación.

## Segundo cerebro del agente IA (v1.2, ADR-012)
ACM usa modelos locales —Ollama para generar y JEV (modelos de decisión en Ollaya) para decidir— para entregar al agente contexto compacto y decisiones ya resueltas. Así el agente gasta **menos tokens** y trabaja con **mejor contexto**. El ahorro de tokens es una métrica de valor del producto (US-35.09).

## Fuente de verdad (ADR-011)
En el producto ACM todo el estado vive en **SQLite**. (En el desarrollo de ACM, la fuente de verdad es `control/` de este repositorio.)

## Interfaz con agentes
ACM implementa su propio servidor MCP y, al conectarse, cada agente descarga las skills de ACM para saber usarlo (v1.1, ADR-008).

## Nota de dogfooding
Este directorio `control/` es la versión manual (Markdown) de lo que ACM automatizará (SQLite + MCP).
Cuando ACM sea operativo, se evaluará migrar este control al propio ACM (registrar como ADR en su momento).
