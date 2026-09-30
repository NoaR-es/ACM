# Data privacy

**Estado del área:** ACTIVE (SPRINT-007). Datos personales: solo identificadores y nombres de principales. Tokens: solo se guarda su sha256 y un prefijo (ADR-017); nunca aparecen en auditoría ni eventos. En el navegador el token está en sessionStorage. Datos locales en `ACM_DATA_DIR`; nada sale a terceros salvo el Ollama que se configure.
