# Casos de prueba

| ID | Tipo | Descripción | Comando | Relacionado |
|----|------|-------------|---------|-------------|
| TEST-CTRL-001 | Integridad | Inventarios de backlog sincronizados con las fuentes A y B e invariantes de unificación y estados | `python3 control/tools/derive_backlog.py --check` | TASK-000-02, TASK-000-09 |
| TEST-SPIKE-001 | Benchmark | Concurrencia SQLite E1–E5 | `python3 spikes/spike_001_sqlite/bench.py` | SPIKE-001, ADR-013 |
| TEST-SPIKE-002a | Integración (SDK en proceso + stdio) | Instructions, extensión Skills, `skills/list`/`get`, digests, error -32602, herramientas de respaldo, stdio | `spikes/.venv/bin/python spikes/spike_002_mcp/test_proto.py` | SPIKE-002, ADR-008, ADR-014 |
| TEST-SPIKE-002b | Integración (HTTP real) | MCP + API + WebSocket en un proceso; evento MCP → WebSocket | `spikes/.venv/bin/python spikes/spike_002_mcp/test_asgi_topology.py` | SPIKE-002, ADR-014 |
| TEST-SPIKE-002c | Integración (HTTP real) | Aislamiento: estado de sesión frente a `project_id` explícito | `spikes/.venv/bin/python spikes/spike_002_mcp/test_session_isolation.py` | SPIKE-002, ADR-014 |
