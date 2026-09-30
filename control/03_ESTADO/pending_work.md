# Trabajo pendiente (ordenado)

1. Comprobar la CI en GitHub del commit de SPRINT-007 (jobs `web` y `test`) y registrarla.
2. **Propuesta para SPRINT-008 (decide el operador):** edición desde la interfaz, es decir, crear y editar requisitos, épicas, features, historias y CA. Exige rutas REST de escritura (hoy solo existen por MCP).
3. Artefactos que la interfaz mostrará en cuanto existan en el producto:
   - sprints y objetivos (EPIC-05);
   - tareas y su Kanban (EPIC-10, US-06.04);
   - documentación viva y ADR (EPIC-25);
   - bugs e incidentes (EPIC-29);
   - presencia de agentes (US-21.10/11).
4. **Operador:** SPIKE-005 con un Ollama real (IMP-004).
5. Adaptador JEV (EPIC-50) cuando haya acceso a Ollaya/TypeSafe.
6. Seguridad pendiente: US-20.07, expiración de tokens, retención (EPIC-44), VULN-002.
7. TD-001 y TD-003 (auditoría y eventos no atómicos con la operación).
8. Medir con carga: auditoría del Watchdog, polling de eventos por cliente WS y tamaño del bundle (423 kB).
9. Resto de solapamientos (GAP-006) y refinamientos (GAP-001).
10. Automatizar las pruebas de mutación.
11. Generar los tipos TS desde OpenAPI si la API crece (`05_CODIGO/types.md`).
