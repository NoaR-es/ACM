# User documentation

**Estado del área:** ACTIVE (SPRINT-009).

Interfaz web (`http://<host>:8765/`):
- **Acceso:** pega un token `acm_…`; queda en la pestaña hasta cerrarla.
- **Panel:** tus proyectos con semáforo, estados y cambios en vivo.
- **Kanban:** elige uno o varios proyectos; mezclados o por carril; arrastra o usa «Mover a…» con teclado. Un movimiento no permitido se explica.
- **Proyecto:** resumen, backlog (requisitos, épicas, features, historias, CA), trazabilidad, Kanban, gobernanza, miembros y configuración.
- **Historia:** criterios, enlaces, transiciones, historial y contexto compacto.
- **Actividad** (admin): feed en vivo y consola filtrable.
- **Documentación:** skills, flujo de estados y API.
- **Sistema** (admin): salud, motores, ahorro, principales y tokens.
- **Tema:** claro, oscuro o del sistema (selector de la cabecera).

Novedades de SPRINT-008 (2026-10-06):
- **Todo se puede hacer desde la interfaz:** crear proyectos (Panel), requisitos, épicas, features, historias y criterios (pestaña Backlog y ficha de historia), miembros y configuración del proyecto, principales y tokens (Sistema; el secreto de un token se muestra una sola vez y se puede copiar). Los errores aparecen junto al campo que los causa.
- **Sprints** (pestaña Sprints): crear con objetivo, fechas y capacidad; planificar historias; iniciar (si está sobrecargado, se avisa y se puede forzar); cerrar decidiendo adónde va lo no terminado; cancelar. Un sprint activo muestra su tablero.
- **Supervisor** (Gobernanza): informe de lo hecho, lo pendiente y las incongruencias, con las acciones propuestas o aplicadas, su motor y su confianza. Toda acción aplicada se puede deshacer. Se controla con `supervisor.mode` (`off`, `propose`, `apply_safe`) y `supervisor.min_confidence_pct` en la configuración del proyecto.
- **Modelos** (Sistema → Modelos, admin): modelos detectados en Ollama y Ollaya con la guía de uso de cada familia; elige uno de Ollama y uno de Ollaya por propósito (y uno por defecto).
- **Asistente** (pestaña del proyecto): conversa con el modelo local sobre el proyecto; consulta los datos con herramientas de solo lectura y conserva el hilo.

Novedades de SPRINT-009 (2026-10-28):
- **Conectar un agente:** añade a su configuración MCP la entrada estándar (`uvx --from git+https://github.com/NoaR-es/ACM acm mcp-stdio`); el README da el formato de Claude Code, Cursor, Antigravity, Codex y Hermes. No hay que instalar, clonar ni crear tokens. La interfaz abre sola en `http://127.0.0.1:8765/` y entra sin token en tu equipo.
- **Solicitudes de acceso (Panel):** cuando un agente pide unirse a un proyecto, aparece aquí en tiempo real. Aprueba con escritura, solo lectura o rechaza. Hasta que apruebes, el agente no ve el proyecto. Para retirar a un agente: proyecto → Miembros → Retirar.
- **Kanban:** cada historia muestra «Asignada a» el agente (y su sesión) que la tiene.
- **Parar la interfaz en segundo plano:** `acm stop`.
