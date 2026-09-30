<!-- GENERADO por control/tools/derive_backlog.py desde 01_PRODUCTO/backlog_completo_v1.md (A) y 01_PRODUCTO/product_definition_v3.md (B). No editar a mano: editar las fuentes o el mapeo del script y regenerar. -->

# Historias técnicas transversales y Spikes (fuente B)

> Los IDs `TECH-XXX` designan **historias técnicas**, no deuda técnica (la deuda usa `TD-NNN`, ADR-002).

## Historias técnicas

| ID | Título | Descripción | Estado |
|----|--------|-------------|--------|
| TECH-001 | Motor de eventos interno | Implementar un sistema centralizado de eventos para propagar cambios ACM. | PLANNED |
| TECH-002 | Bus WebSocket | Implementar distribución de eventos a clientes conectados. | PLANNED |
| TECH-003 | Gestión WAL SQLite | Configurar y validar el modo de concurrencia apropiado. | VERIFIED |
| TECH-004 | Sistema de transacciones | Implementar transacciones seguras para operaciones ACM. | VERIFIED |
| TECH-005 | Sistema de locking | Implementar control optimista de recursos. | PLANNED |
| TECH-006 | Índices SQLite | Diseñar índices sobre las relaciones críticas. | PLANNED |
| TECH-007 | Migraciones de esquema | Implementar evolución versionada del esquema. | VERIFIED |
| TECH-008 | Integridad referencial | Activar y verificar claves foráneas. | VERIFIED |
| TECH-009 | Triggers ACM | Implementar los triggers necesarios para automatización de estados. | PLANNED |
| TECH-010 | API MCP | Implementar exposición de herramientas. | IN_PROGRESS |
| TECH-011 | Registro de herramientas | Implementar descubrimiento y metadatos de herramientas. | PLANNED |
| TECH-012 | Sistema de autenticación | Implementar validación de credenciales. | PLANNED |
| TECH-013 | RBAC | Implementar autorización por roles. | PLANNED |
| TECH-014 | Auditoría | Implementar registro inmutable de operaciones. | PLANNED |
| TECH-015 | RAG ingestion pipeline | Implementar pipeline de indexación. | PLANNED |
| TECH-016 | Embeddings | Implementar generación y actualización incremental. | PLANNED |
| TECH-017 | Reranking | Implementar recuperación híbrida y reranking. | PLANNED |
| TECH-018 | Ollama adapter | Implementar conexión con Ollama. | PLANNED |
| TECH-019 | Model router | Implementar selección y failover de modelos. | PLANNED |
| TECH-020 | JEV adapter | Implementar integración con el motor JEV. | PLANNED |
| TECH-021 | Snapshot engine | Implementar snapshots coordinados. | PLANNED |
| TECH-022 | Git integration | Implementar asociación entre snapshots y commits. | PLANNED |
| TECH-023 | Sandbox engine | Implementar entornos efímeros. | PLANNED |
| TECH-024 | Execution engine | Implementar ejecución de walkthroughs. | PLANNED |
| TECH-025 | Documentation generator | Implementar generación documental. | PLANNED |
| TECH-026 | Graph engine | Implementar representación de dependencias. | PLANNED |
| TECH-027 | Telemetry engine | Implementar métricas y eventos. | PLANNED |
| TECH-028 | Notification engine | Implementar Webhooks y alertas. | PLANNED |
| TECH-029 | CLI | Implementar interfaz administrativa. | IN_PROGRESS |
| TECH-030 | Plugin system | Implementar extensión segura del servidor. | PLANNED |

## Spikes

| ID | Título | Pregunta | Estado |
|----|--------|----------|--------|
| SPIKE-001 | Modelo de concurrencia SQLite | Determinar límites reales de concurrencia y estrategia WAL/locking. | VERIFIED |
| SPIKE-002 | Arquitectura MCP multi-proyecto | Determinar aislamiento óptimo entre proyectos y sesiones. | VERIFIED |
| SPIKE-003 | ChromaDB | Evaluar persistencia, aislamiento y rendimiento. | PLANNED |
| SPIKE-004 | RAG híbrido | Evaluar combinación SQL + vector + reranking. | PLANNED |
| SPIKE-005 | Ollama multiagente | Evaluar gestión de múltiples inferencias concurrentes. | PLANNED |
| SPIKE-006 | JEV | Definir contrato real de integración. | PLANNED |
| SPIKE-007 | Sandbox | Determinar tecnología de aislamiento. | PLANNED |
| SPIKE-008 | Snapshots | Determinar estrategia incremental y restauración consistente. | PLANNED |
| SPIKE-009 | Cifrado | Determinar modelo de gestión de claves. | PLANNED |
| SPIKE-010 | Observabilidad | Determinar esquema de eventos y retención. | PLANNED |
| SPIKE-011 | Streaming de razonamiento | Determinar qué información puede mostrarse de forma segura y qué debe representarse como trazas/eventos en lugar de exponer razonamiento interno privado. | PLANNED |
| SPIKE-012 | WebAuthn/FIDO2 | Evaluar si las operaciones críticas requieren segundo factor hardware. | PLANNED |
