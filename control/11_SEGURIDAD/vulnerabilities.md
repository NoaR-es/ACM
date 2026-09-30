# Vulnerabilidades y riesgos

| ID | Fecha | Descripción | Severidad | Mitigación | Estado |
|----|-------|-------------|-----------|------------|--------|
| VULN-001 | 2026-09-30 | El HTTP de ACM (`/mcp`, `/api`) no tiene autenticación: cualquiera que alcance el puerto actúa como `ACM_PRINCIPAL` (admin). | ALTA si se expone | Escucha en 127.0.0.1 por defecto; no definir `ACM_HOST` con una interfaz pública hasta EPIC-20 | OPEN (hasta EPIC-20) |
