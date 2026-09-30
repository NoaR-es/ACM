# Autorización (SPRINT-001..004)

Se decide en el dominio, en cada operación y con los roles actuales (efecto inmediato, US-20.01 CA-03):
- **Plataforma:** crear proyectos, gestionar principales y roles globales, crear tokens ajenos, consultar auditoría, ahorro y motores → rol global `admin`.
- **Proyecto:** cualquier rol del proyecto lee y escribe el backlog; modificar la configuración → `owner` o `admin`; gestionar miembros → `owner` o `admin`.
- **Proyecto ajeno** → `NOT_FOUND` (no se revela su existencia).
- **Invariantes:** siempre hay al menos un admin y cada proyecto tiene al menos un owner.
- Todo rechazo es `FORBIDDEN` o `NOT_FOUND`, sin efectos, y queda auditado (US-20.02).

Detalle por herramienta: `permissions.md`.
