# Modules

**Estado del área:** ACTIVE (SPRINT-007). Los módulos del código y sus responsabilidades se documentan en `../05_CODIGO/modules.md`; aquí solo la regla de dependencias: `domain` no importa `web_api`, `mcp_server` ni `app`; las entradas (MCP, REST, CLI) llaman a los servicios de dominio; la inferencia se usa a través de los puertos (ADR-015).
