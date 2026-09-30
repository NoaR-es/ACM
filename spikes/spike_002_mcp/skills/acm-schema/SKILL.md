---
name: acm-schema
description: Explica el modelo de trabajo de ACM (proyecto, épicas, features, historias, criterios, tareas) y el orden en que un agente debe usar sus herramientas. Úsala antes de operar sobre un proyecto ACM.
version: 0.0.1-spike
---

# ACM — modelo de trabajo (muestra del SPIKE-002)

1. Selecciona siempre el proyecto de forma explícita antes de cualquier otra operación.
2. Jerarquía: proyecto → épica → feature → historia → criterios de aceptación (CA-NN) → tareas.
3. Una historia solo pasa a READY si tiene criterios de aceptación verificables.
4. Una historia solo pasa a DONE si todos sus CA están en PASS con evidencia registrada.
