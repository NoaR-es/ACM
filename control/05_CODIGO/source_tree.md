# Árbol de fuentes

```text
/
├── CLAUDE.md                          # Constitución del agente
├── .gitignore                         # __pycache__, *.pyc, .venv/
├── control/                           # Sistema de control (fuente de verdad del desarrollo, ADR-011)
│   └── tools/
│       ├── derive_backlog.py          # Backlog unificado A+B, inventarios y validación
│       └── item_status.json           # Estados de historias/TECH/SPIKE distintos de PLANNED
└── spikes/                            # Experimentos (NO es código de producto)
    ├── README.md
    ├── spike_001_sqlite/bench.py      # SPIKE-001 (+ results.json)
    └── spike_002_mcp/                 # SPIKE-002: prototipo MCP + extensión Skills + tests
        ├── acm_mcp_proto.py
        ├── skills/acm-schema/SKILL.md, skills/acm-invest/SKILL.md  (muestras del spike)
        ├── test_proto.py, test_asgi_topology.py, test_session_isolation.py
```

No existe código de producto todavía (sin `pyproject.toml` ni paquete `acm/`).
