# Arquitectura de datos

> **Estado: PLANNED (modelo conceptual, definición §6).** No existe esquema ni base de datos.

| Grupo | Tabla conceptual | Propósito |
|-------|------------------|-----------|
| Product Graph | modules | Árbol jerárquico del producto |
| Product Graph | features | Funcionalidades y reglas de negocio |
| Product Graph | project_stack | Tecnologías y decisiones técnicas |
| Product Graph | project_metadata | Configuración y visión global |
| Agile Backlog | epics | Objetivos macro |
| Agile Backlog | user_stories | Valor funcional |
| Agile Backlog | requirements | Criterios verificables |
| Ejecución | sprints | Contenedores temporales |
| Ejecución | tasks | Trabajo técnico |
| Ejecución | implementation_plans | Planes de ejecución |
| Ejecución | plan_steps | Hitos |
| Ejecución | plan_validators | Validadores de hitos |
| Calidad | bugs | Errores y causa raíz |
| Calidad | tech_debt | Deuda técnica |
| Calidad | adrs | Decisiones arquitectónicas |
| Calidad | walkthrough_logs | Evidencias de ejecución |

Motor previsto: SQLite, una base por proyecto (US-01.01, EPIC-18). **SQLite es la fuente de verdad del producto y todo se aloja ahí** (ADR-011), incluida la memoria de proyecto de EPIC-02; cualquier exportación a archivos es una proyección no autoritativa. Modo WAL/locking: SPIKE-001. Migraciones: TECH-007.
Faltan en el modelo conceptual (a diseñar, GAP-005): auditoría, tokens/RBAC, snapshots, agentes/sesiones, locks, memoria de proyecto (EPIC-02), instancias/hilos/ejecuciones, lecciones, decisiones delegadas y registro de tokens ahorrados (US-35.09).
