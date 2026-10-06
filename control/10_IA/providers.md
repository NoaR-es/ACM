# Proveedores

| Proveedor | Tipo | Uso en ACM | Estado |
|-----------|------|------------|--------|
| Ollama (local) | Inferencia generativa y *tool calling*; decisión sin calibrar | EPIC-22: contexto compacto, informe del supervisor, agente interno, respaldo de decisiones | IMPLEMENTED (sin instancia real, IMP-004) |
| Ollaya (local) | Inferencia decisional (modelos JEV) por `POST /api/decide` | EPIC-50, destino por defecto de las decisiones (ADR-006, ADR-021) | IMPLEMENTED (sin instancia real, IMP-004) |
| TypeSafe API (cloud) | Jev hospedado, `api.typesafe.ai/v1/systemone` | Alternativa configurable (ADR-006); coste por token de entrada | PLANNED |
