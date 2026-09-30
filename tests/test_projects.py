"""US-01.01, US-01.02, US-01.03 — ver control/01_PRODUCTO/refinements/."""

from __future__ import annotations

import shutil
import sqlite3
import threading
from pathlib import Path

import pytest

from acm.domain.errors import AlreadyExists, Forbidden, InvalidArgument, NotFound, StorageError
from acm.domain.projects import ProjectService
from tests.conftest import ADMIN, add_member


def _registered(data_dir: Path) -> list[str]:
    conn = sqlite3.connect(data_dir / "acm.db")
    ids = [r[0] for r in conn.execute("SELECT id FROM projects ORDER BY id")]
    conn.close()
    return ids


# ---------------------------------------------------------------- US-01.01
def test_us0101_ca01_crea_exactamente_un_proyecto(service: ProjectService, data_dir: Path) -> None:
    created = service.create(ADMIN, "alpha", "  Alpha  ", "primer proyecto")
    assert created["project_id"] == "alpha" and created["name"] == "Alpha"  # CA-01.04-01: nombre e identificador
    assert _registered(data_dir) == ["alpha"]
    assert (data_dir / "projects" / "alpha" / "project.db").is_file()  # CA-01.04-03: su base SQLite


@pytest.mark.parametrize("name", ["", "   ", None])
def test_us0101_ca02_nombre_vacio_rechazado_identifica_campo(service: ProjectService, data_dir: Path, name) -> None:
    with pytest.raises(InvalidArgument) as err:
        service.create(ADMIN, "alpha", name)
    assert err.value.field == "name"
    assert _registered(data_dir) == []
    assert not (data_dir / "projects" / "alpha").exists()


def test_us0101_limites_de_nombre_y_formato_de_key(service: ProjectService) -> None:
    service.create(ADMIN, "limite", "x" * 120)
    with pytest.raises(InvalidArgument) as err:
        service.create(ADMIN, "largo", "x" * 121)
    assert err.value.field == "name"
    for bad in ("Alpha", "al_pha", "a", "1abc", "con espacio"):
        with pytest.raises(InvalidArgument) as err:
            service.create(ADMIN, bad, "X")
        assert err.value.field == "key"


def test_us0101_ca03_duplicado_no_se_crea(service: ProjectService, data_dir: Path) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    with pytest.raises(AlreadyExists):
        service.create(ADMIN, "alpha", "Otro nombre")
    assert _registered(data_dir) == ["alpha"]


def test_us0101_ca03_creacion_concurrente_mismo_key(service: ProjectService, data_dir: Path) -> None:
    barrier = threading.Barrier(2)
    outcomes: list[str] = []

    def worker() -> None:
        barrier.wait()
        try:
            service.create(ADMIN, "carrera", "Carrera")
            outcomes.append("ok")
        except AlreadyExists:
            outcomes.append("duplicado")

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(outcomes) == ["duplicado", "ok"]
    assert _registered(data_dir) == ["carrera"]


def test_us0101_ca04_fallo_de_almacenamiento_no_deja_registro_parcial(
    service: ProjectService, data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_register(*_a, **_k):
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(service, "_register", fail_register)
    with pytest.raises(StorageError, match="no se ha creado nada"):
        service.create(ADMIN, "alpha", "Alpha")
    assert _registered(data_dir) == []
    assert not (data_dir / "projects" / "alpha").exists()

    def fail_init(*_a, **_k):
        raise sqlite3.OperationalError("disk full")

    monkeypatch.setattr(service, "_init_project_db", fail_init)
    with pytest.raises(StorageError, match="no se ha creado nada"):
        service.create(ADMIN, "beta", "Beta")
    assert _registered(data_dir) == []
    assert not (data_dir / "projects" / "beta").exists()
    monkeypatch.undo()
    service.create(ADMIN, "alpha", "Alpha")  # el error es recuperable: reintentar funciona
    assert _registered(data_dir) == ["alpha"]


def test_us0101_ca05_proyecto_creado_se_abre_desde_listado(service: ProjectService) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    listed = service.list_for(ADMIN)
    assert [p["project_id"] for p in listed] == ["alpha"]  # CA-01.04-04: disponible para consulta
    opened = service.open(ADMIN, listed[0]["project_id"])
    assert opened["project_id"] == "alpha" and opened["name"] == "Alpha"


def test_us0101_contexto_fisico_creado(service: ProjectService, data_dir: Path) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    project_dir = data_dir / "projects" / "alpha"
    assert project_dir.is_dir()  # CA-01.04-02: contexto físico
    conn = sqlite3.connect(project_dir / "project.db")
    assert conn.execute("SELECT value FROM project_meta WHERE key='project_id'").fetchone() == ("alpha",)
    conn.close()


def test_us0101_no_admin_no_puede_crear(service: ProjectService, data_dir: Path) -> None:
    service.ensure_principal("bob", "user")
    with pytest.raises(Forbidden):
        service.create("bob", "alpha", "Alpha")
    with pytest.raises(Forbidden):
        service.create("desconocido", "alpha", "Alpha")
    assert _registered(data_dir) == []


# ---------------------------------------------------------------- US-01.02
def test_us0102_ca01_listado_solo_proyectos_con_acceso(service: ProjectService, data_dir: Path) -> None:
    for key in ("alpha", "beta", "gamma"):
        service.create(ADMIN, key, key.title())
    add_member(data_dir, "beta", "bob")
    service.ensure_principal("carol", "user")
    assert [p["project_id"] for p in service.list_for(ADMIN)] == ["alpha", "beta", "gamma"]
    assert [p["project_id"] for p in service.list_for("bob")] == ["beta"]
    assert service.list_for("carol") == []


def test_us0102_ca02_abrir_carga_contexto(service: ProjectService) -> None:
    service.create(ADMIN, "alpha", "Alpha", "desc")
    ctx = service.open(ADMIN, "alpha")
    assert {"project_id", "name", "description", "created_at", "created_by", "role", "schema_version", "config"} <= set(
        ctx
    )
    assert ctx["description"] == "desc" and ctx["role"] == "admin"
    assert {p["key"] for p in ctx["config"]} == {"sqlite.synchronous", "context.max_tokens", "decision.engine_order"}


def test_us0102_ca04_proyecto_inexistente_o_sin_base(service: ProjectService, data_dir: Path) -> None:
    with pytest.raises(NotFound):
        service.open(ADMIN, "noexiste")
    service.create(ADMIN, "alpha", "Alpha")
    service.close()
    shutil.rmtree(data_dir / "projects" / "alpha")  # la base desaparece fuera de ACM
    fresh = ProjectService(data_dir)
    with pytest.raises(NotFound, match="base del proyecto no encontrada"):
        fresh.open(ADMIN, "alpha")
    fresh.close()


def test_us0102_ca05_cambiar_de_proyecto_no_mezcla_datos(service: ProjectService) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    service.create(ADMIN, "beta", "Beta")
    service.set_config(ADMIN, "alpha", {"context.max_tokens": 1000})
    service.set_config(ADMIN, "beta", {"context.max_tokens": 2000})

    def max_tokens(ctx: dict) -> int:
        return next(p["value"] for p in ctx["config"] if p["key"] == "context.max_tokens")

    a1, b, a2 = service.open(ADMIN, "alpha"), service.open(ADMIN, "beta"), service.open(ADMIN, "alpha")
    assert (a1["project_id"], max_tokens(a1)) == ("alpha", 1000)
    assert (b["project_id"], b["name"], max_tokens(b)) == ("beta", "Beta", 2000)
    assert a1 == a2


def test_us0102_no_miembro_recibe_not_found(service: ProjectService) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    service.ensure_principal("bob", "user")
    with pytest.raises(NotFound) as err:
        service.open("bob", "alpha")
    assert "no existe o no es accesible" in str(err.value)


# ---------------------------------------------------------------- US-01.03
def test_us0103_ca01_parametros_con_valor_actual(service: ProjectService) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    service.set_config(ADMIN, "alpha", {"context.max_tokens": 3000})
    params = {p["key"]: p for p in service.get_config(ADMIN, "alpha")["parameters"]}
    assert params["context.max_tokens"]["value"] == 3000 and params["context.max_tokens"]["default"] == 8000
    assert params["sqlite.synchronous"]["value"] == "FULL"
    for p in params.values():
        assert {"value", "default", "type", "allowed", "requires_reload", "description", "consumer"} <= set(p)


def test_us0103_ca02_invalidos_rechazados_sin_guardar(service: ProjectService) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    invalid = [
        ({"no.existe": 1}, "no.existe"),
        ({"context.max_tokens": 255}, "context.max_tokens"),
        ({"context.max_tokens": 200001}, "context.max_tokens"),
        ({"context.max_tokens": "8000"}, "context.max_tokens"),
        ({"sqlite.synchronous": "OFF"}, "sqlite.synchronous"),
        ({"decision.engine_order": []}, "decision.engine_order"),
        ({"decision.engine_order": ["rules", "rules"]}, "decision.engine_order"),
        ({"decision.engine_order": ["gpt"]}, "decision.engine_order"),
        # petición mixta: uno válido y uno inválido → no se guarda nada
        ({"context.max_tokens": 5000, "sqlite.synchronous": "OFF"}, "sqlite.synchronous"),
    ]
    for changes, field in invalid:
        with pytest.raises(InvalidArgument) as err:
            service.set_config(ADMIN, "alpha", changes)
        assert err.value.field == field
    params = {p["key"]: p["value"] for p in service.get_config(ADMIN, "alpha")["parameters"]}
    assert params == {
        "sqlite.synchronous": "FULL",
        "context.max_tokens": 8000,
        "decision.engine_order": ["rules", "jev", "ollama"],
    }
    service.set_config(ADMIN, "alpha", {"context.max_tokens": 256})  # límites aceptados
    service.set_config(ADMIN, "alpha", {"context.max_tokens": 200000})


def test_us0103_ca03_configuracion_persistida(service: ProjectService, data_dir: Path) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    service.set_config(ADMIN, "alpha", {"decision.engine_order": ["ollama"], "context.max_tokens": 1234})
    service.close()
    fresh = ProjectService(data_dir)
    params = {p["key"]: p["value"] for p in fresh.get_config(ADMIN, "alpha")["parameters"]}
    assert params["decision.engine_order"] == ["ollama"] and params["context.max_tokens"] == 1234
    fresh.close()


def test_us0103_ca04_cambios_que_requieren_recarga(service: ProjectService) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    result = service.set_config(ADMIN, "alpha", {"sqlite.synchronous": "NORMAL", "context.max_tokens": 4000})
    assert sorted(result["changed"]) == ["context.max_tokens", "sqlite.synchronous"]
    assert result["requires_reload"] == ["sqlite.synchronous"]
    # El consumidor (capa de datos) aplica el nuevo valor a las conexiones nuevas.
    seen: list[str] = []
    t = threading.Thread(target=lambda: seen.append(service.project_db("alpha").pragmas()["synchronous"]))
    t.start()
    t.join()
    assert seen == ["NORMAL"]
    again = service.set_config(ADMIN, "alpha", {"sqlite.synchronous": "NORMAL"})
    assert again["changed"] == [] and again["requires_reload"] == []


def test_us0103_ca05_configuracion_exclusiva_del_proyecto(service: ProjectService, data_dir: Path) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    service.create(ADMIN, "beta", "Beta")
    service.set_config(ADMIN, "alpha", {"context.max_tokens": 999})
    beta = {p["key"]: p["value"] for p in service.get_config(ADMIN, "beta")["parameters"]}
    assert beta["context.max_tokens"] == 8000
    conn = sqlite3.connect(data_dir / "projects" / "beta" / "project.db")
    assert conn.execute("SELECT COUNT(*) FROM config").fetchone()[0] == 0
    conn.close()


def test_us0103_member_no_puede_modificar(service: ProjectService, data_dir: Path) -> None:
    service.create(ADMIN, "alpha", "Alpha")
    add_member(data_dir, "alpha", "bob", "member")
    assert service.get_config("bob", "alpha")["project_id"] == "alpha"  # leer sí
    with pytest.raises(Forbidden):
        service.set_config("bob", "alpha", {"context.max_tokens": 1000})
