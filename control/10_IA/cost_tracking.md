# Seguimiento de coste

- **Motores actuales:** reglas (sin coste) y Ollama local (sin coste por token; consume hardware propio).
- **Qué se registra:** cada llamada de inferencia en `inference_calls` (tokens de entrada y salida si el motor los informa; Ollama da `prompt_eval_count`/`eval_count`). Cada entrega de contexto en `context_deliveries` (tokens entregados frente al equivalente completo, método `chars/4@v1`), consultable con `acm_savings_report` (US-35.09).
- **Coste monetario:** no aplica todavía. Se medirá con proveedores de pago (JEV vía TypeSafe, EPIC-50; EPIC-23).
