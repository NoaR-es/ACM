# Trabajo pendiente (ordenado)

1. **Operador:** SPIKE-005 con Ollama y Ollaya reales (IMP-004). Pasaría a VERIFIED US-22.01, 22.03, 22.04, 22.10, 22.11, 50.01..50.03, 50.09 y 50.10, y mediría la calidad de las decisiones del supervisor con modelos reales.
2. **Propuesta para SPRINT-009 (decide el operador):** dependencias entre historias (cierra US-05.02 CA-03) y tareas con su Kanban (EPIC-10, US-06.04).
3. Artefactos que la interfaz mostrará en cuanto existan en el producto:
   - documentación viva y ADR (EPIC-25);
   - bugs e incidentes (EPIC-29);
   - presencia de agentes (US-21.10/11).
4. Seguridad pendiente: US-20.07, expiración de tokens, retención (EPIC-44), VULN-002.
5. TD-001 y TD-003 (auditoría y eventos no atómicos con la operación).
6. Medir con carga: auditoría del Watchdog y del supervisor, polling de eventos por cliente WS y tamaño del bundle (~461 kB).
7. Resto de solapamientos (GAP-006) y refinamientos (GAP-001).
8. Automatizar las pruebas de mutación.
9. Generar los tipos TS desde OpenAPI (la API ya tiene 54 rutas HTTP; `05_CODIGO/types.md`).
