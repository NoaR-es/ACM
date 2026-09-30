# Audit trail

**Estado del área:** ACTIVE (SPRINT-007). Cada invocación MCP y cada mutación REST quedan en `mcp_audit` (acm.db): principal, `token_id`, operación, argumentos con secretos redactados, resultado truncado y duración (US-14.10/11). Solo lo consulta un admin (MCP `acm_audit_list` y la consola de Actividad). No es atómico con la operación (TD-001).
