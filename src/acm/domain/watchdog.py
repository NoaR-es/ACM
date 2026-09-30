"""Watchdog de gobernanza (EPIC-13).

Una ejecución (`run`) de un proyecto:
1. **Integridad** (US-13.05): `PRAGMA integrity_check` y `PRAGMA foreign_key_check` de su base. Si falla, el proyecto
   queda en cuarentena (`projects.integrity_status = 'corrupt'`): se rechazan sus escrituras (US-13.11) y no se evalúa
   nada más sobre un estado corrupto. Una ejecución posterior que la encuentre sana levanta la cuarentena.
2. **Calidad de historias** (US-13.07): cada historia activa se evalúa a través de la interfaz de decisión común
   (`EngineRouter`, purpose `story.quality`; US-35.11 CA-01). Una respuesta no calibrada no se da por fallo: se marca
   REVIEW (ADR-015).
3. **Estructura**: requisitos huérfanos, épicas sin features, features sin historias (`BacklogService.audit`).
4. **Semáforo** (US-13.10): RED si hay algún CRITICAL; AMBER si hay WARNING o REVIEW; GREEN si no.
5. **Histórico** (US-13.13): cada ejecución se guarda en `watchdog_runs` de la base global.

`run_all` recorre todos los proyectos; la app lo lanza periódicamente (`ACM_WATCHDOG_INTERVAL_S`, US-13.06).
"""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import UTC, datetime
from typing import Any

from acm.domain.backlog import READY_GATE_QUESTIONS, BacklogService
from acm.domain.errors import AcmError, Forbidden, InvalidArgument
from acm.domain.projects import ProjectService
from acm.inference.ports import DecisionRequest
from acm.inference.router import EngineRouter

SEVERITIES = ("CRITICAL", "WARNING", "REVIEW", "INFO")
INACTIVE_STORY = ("CANCELLED", "DEPRECATED", "DONE")
HISTORY_MAX = 200

STORY_FINDINGS = {
    "has_statement": ("STORY_INCOMPLETE_STATEMENT", "falta rol, objetivo o beneficio"),
    "has_requirements": ("STORY_WITHOUT_REQUIREMENT", "sin requisito de origen: cambio no trazable"),
    "has_acceptance_criteria": ("STORY_WITHOUT_CRITERIA", "sin criterios de aceptación"),
    "technical_reason_ok": ("TECHNICAL_WITHOUT_REASON", "historia técnica sin razón explícita"),
}
STRUCTURE_FINDINGS = {
    "orphan_requirements": ("ORPHAN_REQUIREMENT", "requisito sin ninguna historia que lo implemente"),
    "epics_without_features": ("EPIC_WITHOUT_FEATURES", "épica sin features activas"),
    "features_without_stories": ("FEATURE_WITHOUT_STORIES", "feature sin historias"),
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _finding(code: str, severity: str, target: str, message: str, source: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "severity": severity, "target": target, "message": message, "source": source, **extra}


def semaphore(findings: list[dict[str, Any]]) -> str:
    severities = {f["severity"] for f in findings}
    if "CRITICAL" in severities:
        return "RED"
    if severities & {"WARNING", "REVIEW"}:
        return "AMBER"
    return "GREEN"


class WatchdogService:
    def __init__(self, projects: ProjectService, backlog: BacklogService, engines: EngineRouter):
        self.projects = projects
        self.backlog = backlog
        self.engines = engines

    # ------------------------------------------------------------------ US-13.05
    def _integrity(self, project_id: str) -> list[dict[str, Any]]:
        try:
            with self.projects.project_db(project_id).read() as conn:
                checks = [str(r[0]) for r in conn.execute("PRAGMA integrity_check(20)")]
                fks = conn.execute("PRAGMA foreign_key_check").fetchall()
        except (sqlite3.DatabaseError, AcmError) as exc:
            return [_finding("DB_UNREADABLE", "CRITICAL", project_id, f"no se pudo leer la base: {exc}", "integrity")]
        findings = []
        if checks != ["ok"]:
            findings.append(_finding("SQLITE_INTEGRITY", "CRITICAL", project_id, "; ".join(checks), "integrity"))
        for table, rowid, parent, _fkid in fks:
            findings.append(
                _finding(
                    "SQLITE_FOREIGN_KEY",
                    "CRITICAL",
                    f"{table}#{rowid}",
                    f"fila de {table} que referencia a {parent} inexistente",
                    "integrity",
                )
            )
        return findings

    def _set_integrity(self, project_id: str, findings: list[dict[str, Any]]) -> str:
        status = "corrupt" if findings else "ok"
        detail = "; ".join(f"{f['code']}: {f['target']}" for f in findings[:5])
        with self.projects.global_db.write() as conn:
            conn.execute(
                "UPDATE projects SET integrity_status = ?, integrity_detail = ?, integrity_checked_at = ? WHERE id = ?",
                (status, detail, _now(), project_id),
            )
        return status

    # ------------------------------------------------------------------ US-13.07 (interfaz de decisión)
    def _story_quality(self, principal: str, project_id: str) -> tuple[list[dict[str, Any]], set[str]]:
        with self.projects.project_db(project_id).read() as conn:
            ids = [
                r[0] for r in conn.execute("SELECT id, status FROM stories ORDER BY id") if r[1] not in INACTIVE_STORY
            ]
        findings: list[dict[str, Any]] = []
        engines: set[str] = set()
        for story_id in ids:
            story = self.backlog.get_story(principal, project_id, story_id)
            request = DecisionRequest(
                state=story, questions=READY_GATE_QUESTIONS, purpose="story.quality", project_id=project_id
            )
            try:
                result = self.engines.decide(principal, request).result
            except AcmError as exc:
                findings.append(
                    _finding("STORY_NOT_EVALUATED", "REVIEW", story_id, f"no se pudo evaluar: {exc}", "decision")
                )
                continue
            engines.add(result.engine)
            for key, answer in result.answers.items():
                if float(answer.value) >= 0.5:
                    continue
                code, message = STORY_FINDINGS[key]
                # Un motor no calibrado no decide por sí solo que algo está mal: pide revisión (ADR-015).
                severity = "WARNING" if answer.calibrated else "REVIEW"
                findings.append(
                    _finding(
                        code, severity, story_id, message, "decision", engine=result.engine, probability=answer.value
                    )
                )
        return findings, engines

    def _structure(self, principal: str, project_id: str) -> list[dict[str, Any]]:
        report = self.backlog.audit(principal, project_id)
        return [
            _finding(code, "INFO", target, message, "structure")
            for key, (code, message) in STRUCTURE_FINDINGS.items()
            for target in report[key]
        ]

    # ------------------------------------------------------------------ US-13.12
    def run(self, principal: str, project_id: str, trigger: str = "manual") -> dict[str, Any]:
        self.projects._project_role(principal, project_id)  # NOT_FOUND si no es accesible
        if trigger not in ("manual", "scheduled"):
            raise InvalidArgument("debe ser 'manual' o 'scheduled'", field="trigger")
        start = time.perf_counter()
        findings = self._integrity(project_id)
        integrity = self._set_integrity(project_id, findings)
        engines: set[str] = set()
        if integrity == "ok":
            quality, engines = self._story_quality(principal, project_id)
            findings += quality + self._structure(principal, project_id)
        counts = {s.lower(): sum(f["severity"] == s for f in findings) for s in SEVERITIES}
        light = semaphore(findings)
        ts = _now()
        with self.projects.global_db.write() as conn:
            cur = conn.execute(
                "INSERT INTO watchdog_runs(project_id, ts, trigger, principal, semaphore, findings_json, critical, "
                "warning, review, info, engines_json, duration_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    project_id,
                    ts,
                    trigger,
                    principal,
                    light,
                    json.dumps(findings, ensure_ascii=False),
                    counts["critical"],
                    counts["warning"],
                    counts["review"],
                    counts["info"],
                    json.dumps(sorted(engines)),
                    round((time.perf_counter() - start) * 1000, 3),
                ),
            )
            run_id = int(cur.lastrowid)
        self.projects.events.append(
            "watchdog.run",
            principal=principal,
            project_id=project_id,
            entity_type="project",
            entity_id=project_id,
            data={"run_id": run_id, "semaphore": light, "integrity": integrity, "counts": counts},
        )
        return {
            "project_id": project_id,
            "run_id": run_id,
            "ts": ts,
            "trigger": trigger,
            "semaphore": light,
            "integrity": integrity,
            "counts": counts,
            "engines": sorted(engines),
            "findings": findings,
        }

    def run_all(self, principal: str, trigger: str = "scheduled") -> list[dict[str, Any]]:
        """US-13.06: audita todos los proyectos. Un fallo en uno no detiene a los demás."""
        with self.projects.global_db.read() as conn:
            if self.projects._principal_role(conn, principal) != "admin":
                raise Forbidden("solo un admin puede auditar todos los proyectos")
            ids = [r[0] for r in conn.execute("SELECT id FROM projects ORDER BY id")]
        summaries = []
        for project_id in ids:
            try:
                run = self.run(principal, project_id, trigger)
                summaries.append({"project_id": project_id, "run_id": run["run_id"], "semaphore": run["semaphore"]})
            except AcmError as exc:
                summaries.append({"project_id": project_id, "error": str(exc)})
        return summaries

    # ------------------------------------------------------------------ US-13.13 / US-13.10
    def history(self, principal: str, project_id: str, limit: Any = 20) -> dict[str, Any]:
        self.projects._project_role(principal, project_id)
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= HISTORY_MAX:
            raise InvalidArgument(f"debe ser un entero entre 1 y {HISTORY_MAX}", field="limit")
        with self.projects.global_db.read() as conn:
            rows = conn.execute(
                "SELECT * FROM watchdog_runs WHERE project_id = ? ORDER BY id DESC LIMIT ?", (project_id, limit)
            ).fetchall()
        runs = []
        for r in rows:
            run = dict(r)
            run["findings"] = json.loads(run.pop("findings_json"))
            run["engines"] = json.loads(run.pop("engines_json"))
            runs.append(run)
        return {"project_id": project_id, "runs": runs}

    def status(self, principal: str, project_id: str) -> dict[str, Any]:
        """Indicadores de gobernanza del proyecto: semáforo y recuentos de la última ejecución."""
        self.projects._project_role(principal, project_id)
        with self.projects.global_db.read() as conn:
            project = conn.execute(
                "SELECT integrity_status, integrity_detail, integrity_checked_at FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            last = conn.execute(
                "SELECT id, ts, trigger, semaphore, critical, warning, review, info FROM watchdog_runs "
                "WHERE project_id = ? ORDER BY id DESC LIMIT 1",
                (project_id,),
            ).fetchone()
        return {
            "project_id": project_id,
            "semaphore": last["semaphore"] if last else "UNKNOWN",
            "last_run": dict(last) if last else None,
            "integrity": dict(project),
            "writable": project["integrity_status"] != "corrupt",
        }

    # ------------------------------------------------------------------ US-13.03
    def health(self, principal: str, catalog: Any = None) -> dict[str, Any]:
        """Estado de cada componente, recalculado en cada llamada (CA-04)."""
        with self.projects.global_db.read() as conn:
            if self.projects._principal_role(conn, principal) != "admin":
                raise Forbidden("solo un admin puede consultar la salud global")
            projects = conn.execute(
                "SELECT id, integrity_status, integrity_detail, integrity_checked_at FROM projects ORDER BY id"
            ).fetchall()
            global_check = [str(r[0]) for r in conn.execute("PRAGMA quick_check")]
        pragmas = self.projects.global_db.pragmas()
        components = []

        def add(name: str, kind: str, status: str, detail: str = "") -> None:
            components.append({"name": name, "kind": kind, "status": status, "detail": detail})

        global_ok = global_check == ["ok"] and str(pragmas["journal_mode"]).lower() == "wal" and pragmas["foreign_keys"]
        add(
            "sqlite:global",
            "database",
            "ok" if global_ok else "error",
            f"quick_check={global_check[:3]}, journal_mode={pragmas['journal_mode']}, "
            f"foreign_keys={pragmas['foreign_keys']}",
        )
        for p in projects:
            status = {"ok": "ok", "unknown": "degraded", "corrupt": "error"}[p["integrity_status"]]
            detail = p["integrity_detail"] or (
                "sin auditar todavía" if status == "degraded" else "integridad verificada"
            )
            add(f"sqlite:project:{p['id']}", "database", status, f"{detail} (comprobado: {p['integrity_checked_at']})")
        if catalog is not None:
            rejected = getattr(catalog, "rejected", {})
            add(
                "skills",
                "catalog",
                "degraded" if rejected else "ok",
                f"{len(catalog.skills)} activas" + (f"; rechazadas: {sorted(rejected)}" if rejected else ""),
            )
        for engine in self.engines.registry.refresh():
            if engine["registered"]:
                add(
                    f"inference:{engine['name']}",
                    "inference",
                    "ok" if engine["status"] == "ok" else "error",
                    engine["detail"],
                )
        overall = "ok"
        if any(c["status"] != "ok" for c in components):
            overall = "degraded"
        if not global_ok:
            overall = "error"
        return {"status": overall, "checked_at": _now(), "components": components}
