# Interfaces de inferencia del núcleo (preparadas para JEV)

Estado: **DESIGN (ACCEPTED en ADR-015)** — no implementado. Tarea: TASK-000-13.
Historias: US-35.11 (interfaz de decisión común), US-47.01 (recursos abstractos), US-35.08..US-35.10 (segundo cerebro), US-22.01..US-22.03 (Ollama), EPIC-50 (adaptador JEV).
Decisiones previas: ADR-006 (contrato JEV/Ollaya), ADR-012 (JEV preparado desde el inicio, segundo cerebro).

## 1. Principio

El núcleo de ACM **nunca llama directamente** a Ollama, Ollaya ni a ningún proveedor. Depende de dos puertos:

| Puerto | Qué resuelve | Implementaciones |
|--------|--------------|------------------|
| `DecisionEngine` | Preguntas tipadas sobre un estado → respuestas con probabilidad | `RulesDecisionEngine` (MVP), `OllamaDecisionEngine` (MVP), `JevDecisionEngine` (Ollaya/TypeSafe, EPIC-50) |
| `GenerationEngine` | Texto generado (resúmenes, redacción) | `OllamaGenerationEngine` (MVP) |

Un `EngineRouter` elige la implementación según el tipo de tarea, la disponibilidad y la política configurada, y aplica el fallback. Watchdog, gates, el servicio de contexto y las herramientas MCP de decisión delegada **solo** usan el router.

Conectar JEV = registrar `JevDecisionEngine` en el router. Los consumidores no cambian (CA de US-35.11).

## 2. Contrato de decisión (espejo del wire de TypeSafe System One / Ollaya)

Se adopta el modelo de datos de ADR-006 para que el adaptador JEV sea una traducción 1:1:

```python
QuestionType = Literal["choice", "score", "noul"]

@dataclass(frozen=True)
class Question:
    type: QuestionType
    instructions: str
    criteria: dict[str, str] | list[str] | None  # choice: {opción: descripción}; score: niveles 2..10; noul: {"true":..,"false":..} opcional

@dataclass(frozen=True)
class DecisionRequest:
    state: str | dict                 # texto o JSON (historia, cambio, bug…)
    questions: dict[str, Question]    # 1..256 preguntas (límite de Ollaya)
    purpose: str                      # p. ej. "watchdog.invest", "agent.delegated" — para routing y auditoría
    project_id: str                   # aislamiento (EPIC-24)

@dataclass(frozen=True)
class Answer:
    type: QuestionType
    value: str | float                # choice → opción; score → valor continuo; noul → probabilidad de "true"
    probabilities: dict[str, float] | None
    confidence: float | None
    calibrated: bool                  # True solo si el motor da probabilidades calibradas (JEV)

@dataclass(frozen=True)
class DecisionResult:
    answers: dict[str, Answer]
    engine: str                       # "rules" | "ollama:<modelo>" | "jev:<modelo>"
    usage: dict[str, int]             # input_tokens, output_tokens (si el motor los da)
    duration_ms: float
    fallback_from: str | None         # motor que falló antes, si hubo fallback (US-39.02)

class DecisionEngine(Protocol):
    name: str
    def supports(self, request: DecisionRequest) -> bool: ...
    async def decide(self, request: DecisionRequest) -> DecisionResult: ...
    async def health(self) -> EngineHealth: ...
```

Reglas del contrato:
- `calibrated=False` obliga a los consumidores a no tratar la confianza como probabilidad real. Por ejemplo, el Watchdog no bloquea automáticamente por umbral con un motor no calibrado: marca "revisar".
- Errores tipados: `EngineUnavailable`, `InvalidRequest`, `InputTooLong`, `TooManyOptions` y `Overloaded` (→ `QUEUE_FULL` de Ollaya, reintentable, US-39.01). Se corresponden con los códigos de Ollaya documentados en `10_IA/inference_engines.md`.
- Toda decisión se registra (motor, duración, uso, propósito, proyecto) para US-23.01, US-35.09 y la auditoría.

## 3. Implementaciones

| Implementación | Alcance | Cómo decide | Limitaciones |
|----------------|---------|-------------|--------------|
| `RulesDecisionEngine` | MVP | Reglas deterministas registradas por `purpose` (p. ej. "¿tiene la historia CA?", "¿hay tareas huérfanas?") | Solo cubre preguntas con regla; `supports()` devuelve False para el resto |
| `OllamaDecisionEngine` | MVP | Prompt con el estado y las preguntas, y salida JSON restringida a las opciones válidas | Confianza **no calibrada**. Latencia de un LLM generativo. Si Ollama expone log-probabilidades, se usarán para estimarla (**sin verificar**: SPIKE-005). |
| `JevDecisionEngine` | EPIC-50 | `POST /api/decide` de Ollaya (o `/v1/systemone` de TypeSafe) | Requiere Ollaya o clave de TypeSafe. Proyecto de ~2 semanas: versión fijada y pruebas de contrato (ADR-006) |

Orden de preferencia por defecto del router para decisiones: `rules` (si `supports`) → `jev` (si está registrado y sano) → `ollama` → error `EngineUnavailable`. Es configurable por proyecto y por `purpose` (US-33.02).

## 4. Contrato de generación

```python
@dataclass(frozen=True)
class GenerationRequest:
    messages: list[dict[str, str]]    # [{"role": "system"|"user", "content": ...}]
    purpose: str                      # "context.compact", "doc.summary", …
    project_id: str
    max_output_tokens: int
    json_schema: dict | None = None   # salida estructurada cuando se necesite

@dataclass(frozen=True)
class GenerationResult:
    text: str
    engine: str
    usage: dict[str, int]
    duration_ms: float
    fallback_from: str | None

class GenerationEngine(Protocol):
    name: str
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...
    async def health(self) -> EngineHealth: ...
```

## 5. Segundo cerebro: contexto compacto y tokens ahorrados

`ContextService.compact(task_id, budget_tokens)`:
1. Construye el contexto estructurado desde SQLite (historia, CA, dependencias, ADR, stack: EPIC-35).
2. Añade fragmentos RAG (EPIC-16).
3. Si el tamaño supera `budget_tokens` y hay un `GenerationEngine` sano, resume por secciones conservando las referencias a la fuente (CA de US-35.08). Si no hay motor, devuelve el contexto sin resumir con `compacted=False`.
4. Registra `delivered_tokens` y `full_equivalent_tokens` (US-35.09).

**Método de estimación de tokens:** ACM no conoce el tokenizador del agente externo. Se registra una estimación con un método explícito y versionado: por defecto `chars/4`, sustituible por un tokenizador concreto si se configura. El informe muestra siempre el método usado (CA de US-35.09).

## 6. Recursos de inferencia abstractos (US-47.01)

`EngineRegistry` guarda cada motor con: nombre, tipo (`decision` | `generation`), proveedor (`rules` | `ollama` | `ollaya` | `typesafe`), endpoint, modelos, estado de salud y límites de concurrencia (la cola de Ollaya devuelve `QUEUE_FULL`; Ollama tiene límites por hardware: SPIKE-005). Los motores se registran por configuración y sus datos persisten en SQLite (ADR-011). Las tareas no conocen implementaciones concretas (CA-01 y CA-02 de US-47.01).

## 7. Pendiente de verificar

- SPIKE-005: si Ollama da log-probabilidades o salida estructurada suficientemente fiable para decisiones, y su concurrencia real.
- SPIKE-006: latencia y calibración de Ollaya con preguntas de gobernanza reales de ACM.
