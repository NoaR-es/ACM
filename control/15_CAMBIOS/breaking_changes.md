# Breaking changes

| Fecha | Cambio | Afecta a | Migración |
|-------|--------|----------|-----------|
| 2026-09-30 | Renumeración de épicas, features e historias de la definición v1.1 al backlog unificado (ADR-010) | Referencias documentales a IDs de B (ADR-003..009) | `01_PRODUCTO/id_mapping.md` |

| 0.9.0.dev0 | 2026-10-28 | Por stdio, sin `ACM_PRINCIPAL`, el agente ya no es `local-admin` (admin) sino un principal propio sin permisos de admin; los datos por defecto pasan de `./.acm-data` a `~/.acm`. | Fijar `ACM_PRINCIPAL=local-admin` y `ACM_DATA_DIR=<ruta anterior>` en la entrada del agente conserva el comportamiento anterior. Para entrar en proyectos existentes, el agente pide unirse y una persona aprueba |