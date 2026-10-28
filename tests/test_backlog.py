"""US-03.03, US-04.01, US-04.02, US-04.03 — ver control/01_PRODUCTO/refinements/."""

from __future__ import annotations

import pytest

from acm.domain.backlog import BacklogService
from acm.domain.errors import AlreadyExists, FailedPrecondition, InvalidArgument, NotFound
from acm.domain.projects import ProjectService
from tests.conftest import ADMIN

P = "alpha"


@pytest.fixture
def backlog(service: ProjectService) -> BacklogService:
    service.create(ADMIN, P, "Alpha")
    return BacklogService(service)


def _story(b: BacklogService, feature: str = "FEAT-01.01", req: str = "REQ-001", **kw) -> dict:
    args = {
        "as_a": "operador",
        "i_want": "crear proyectos",
        "so_that": "separar contextos",
        "requirement_ids": [req],
        "acceptance_criteria": ["Un nombre vacío se rechaza"],
    } | kw
    return b.create_story(
        ADMIN,
        P,
        feature,
        args.pop("as_a"),
        args.pop("i_want"),
        args.pop("so_that"),
        args.pop("requirement_ids"),
        **args,
    )


def _base(b: BacklogService) -> None:
    b.create_requirement(ADMIN, P, "Gestionar proyectos")
    b.create_epic(ADMIN, P, "Proyectos", "Gestionar proyectos", "Crear y abrir", ["REQ-001"])
    b.create_feature(ADMIN, P, "EPIC-01", "Creación")


# ---------------------------------------------------------------- US-03.03
def test_us0303_ca01_requisito_localiza_sus_epicas(backlog: BacklogService) -> None:
    backlog.create_requirement(ADMIN, P, "R1")
    backlog.create_epic(ADMIN, P, "E1", "o", "s", ["REQ-001"])
    backlog.create_epic(ADMIN, P, "E2", "o", "s")
    backlog.link_epic_requirements(ADMIN, P, "EPIC-02", ["REQ-001"])
    assert backlog.trace_requirement(ADMIN, P, "REQ-001")["epic_ids"] == ["EPIC-01", "EPIC-02"]


def test_us0303_ca02_epica_localiza_sus_features(backlog: BacklogService) -> None:
    _base(backlog)
    backlog.create_feature(ADMIN, P, "EPIC-01", "Configuración")
    epic = backlog.get_epic(ADMIN, P, "EPIC-01")
    assert [f["id"] for f in epic["features"]] == ["FEAT-01.01", "FEAT-01.02"]


def test_us0303_ca03_feature_localiza_sus_historias(backlog: BacklogService) -> None:
    _base(backlog)
    _story(backlog)
    _story(backlog, i_want="abrir proyectos")
    feature = backlog.get_epic(ADMIN, P, "EPIC-01")["features"][0]
    assert feature["story_ids"] == ["US-01.01", "US-01.02"]
    trace = backlog.trace_requirement(ADMIN, P, "REQ-001")
    assert trace["epics"][0]["features"][0]["story_ids"] == ["US-01.01", "US-01.02"]


def test_us0303_ca04_historia_identifica_requisitos(backlog: BacklogService) -> None:
    _base(backlog)
    backlog.create_requirement(ADMIN, P, "Aislar proyectos")
    _story(backlog, requirement_ids=["REQ-001", "REQ-002"])
    assert backlog.get_story(ADMIN, P, "US-01.01")["requirement_ids"] == ["REQ-001", "REQ-002"]
    trace = backlog.trace_requirement(ADMIN, P, "REQ-002")
    assert [s["id"] for s in trace["stories"]] == ["US-01.01"]


def test_us0303_ca05_requisitos_huerfanos_en_auditoria(backlog: BacklogService) -> None:
    _base(backlog)
    backlog.create_requirement(ADMIN, P, "Nunca implementado")
    _story(backlog)
    report = backlog.audit(ADMIN, P)
    assert report["orphan_requirements"] == ["REQ-002"] and not report["clean"]
    assert backlog.trace_requirement(ADMIN, P, "REQ-002")["orphan"] is True
    _story(backlog, req="REQ-002")
    assert backlog.audit(ADMIN, P)["clean"] is True


# ---------------------------------------------------------------- US-04.01
def test_us0401_ca01_id_unico_generado(backlog: BacklogService) -> None:
    ids = [backlog.create_epic(ADMIN, P, f"E{i}", "o", "s")["id"] for i in range(3)]
    assert ids == ["EPIC-01", "EPIC-02", "EPIC-03"]
    backlog.create_epic(ADMIN, P, "Importada", "o", "s", epic_id="EPIC-07")
    assert backlog.create_epic(ADMIN, P, "Siguiente", "o", "s")["id"] == "EPIC-08"


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("objective", {"objective": "  ", "scope": "s"}),
        ("scope", {"objective": "o", "scope": ""}),
        ("title", {"objective": "o", "scope": "s", "title": ""}),
    ],
)
def test_us0401_ca02_objetivo_y_alcance_obligatorios(backlog: BacklogService, field: str, kwargs: dict) -> None:
    with pytest.raises(InvalidArgument) as err:
        backlog.create_epic(ADMIN, P, kwargs.pop("title", "Épica"), kwargs["objective"], kwargs["scope"])
    assert err.value.field == field
    assert backlog.list_epics(ADMIN, P)["epics"] == []


def test_us0401_ca03_asociar_requisitos(backlog: BacklogService) -> None:
    backlog.create_requirement(ADMIN, P, "R1")
    backlog.create_requirement(ADMIN, P, "R2")
    epic = backlog.create_epic(ADMIN, P, "E", "o", "s", ["REQ-001"])
    assert epic["requirement_ids"] == ["REQ-001"]
    assert backlog.link_epic_requirements(ADMIN, P, "EPIC-01", ["REQ-002"])["requirement_ids"] == ["REQ-001", "REQ-002"]
    with pytest.raises(NotFound):
        backlog.create_epic(ADMIN, P, "E2", "o", "s", ["REQ-001", "REQ-999"])
    assert [e["id"] for e in backlog.list_epics(ADMIN, P)["epics"]] == ["EPIC-01"]  # nada creado


def test_us0401_ca04_contiene_features(backlog: BacklogService) -> None:
    _base(backlog)
    assert [f["id"] for f in backlog.get_epic(ADMIN, P, "EPIC-01")["features"]] == ["FEAT-01.01"]


def test_us0401_ca05_id_explicito_duplicado_rechazado(backlog: BacklogService) -> None:
    backlog.create_epic(ADMIN, P, "E", "o", "s", epic_id="EPIC-05")
    with pytest.raises(AlreadyExists):
        backlog.create_epic(ADMIN, P, "Otra", "o", "s", epic_id="EPIC-05")
    with pytest.raises(InvalidArgument):
        backlog.create_epic(ADMIN, P, "Otra", "o", "s", epic_id="EPIC-5")


# ---------------------------------------------------------------- US-04.02
def test_us0402_ca01_feature_con_identificador(backlog: BacklogService) -> None:
    _base(backlog)
    f = backlog.create_feature(ADMIN, P, "EPIC-01", "Otra")
    assert f["id"] == "FEAT-01.02" and f["epic_id"] == "EPIC-01" and f["status"] == "ACTIVE"


def test_us0402_ca02_feature_pertenece_a_una_epica(backlog: BacklogService) -> None:
    _base(backlog)
    with pytest.raises(NotFound):
        backlog.create_feature(ADMIN, P, "EPIC-09", "Huérfana")
    with pytest.raises(InvalidArgument) as err:
        backlog.create_feature(ADMIN, P, "EPIC-01", "Mal numerada", feature_id="FEAT-02.01")
    assert err.value.field == "feature_id"


def test_us0402_ca03_confirmar_cobertura_del_objetivo(backlog: BacklogService) -> None:
    backlog.create_epic(ADMIN, P, "Vacía", "o", "s")
    with pytest.raises(FailedPrecondition):
        backlog.confirm_epic_coverage(ADMIN, P, "EPIC-01")
    backlog.create_feature(ADMIN, P, "EPIC-01", "F")
    epic = backlog.confirm_epic_coverage(ADMIN, P, "EPIC-01")
    assert epic["coverage_confirmed_by"] == ADMIN and epic["coverage_confirmed_at"]


def test_us0402_ca04_dividir_feature(backlog: BacklogService) -> None:
    _base(backlog)
    for want in ("a", "b", "c"):
        _story(backlog, i_want=want)
    with pytest.raises(InvalidArgument):  # una historia sin asignar
        backlog.split_feature(
            ADMIN,
            P,
            "FEAT-01.01",
            [{"title": "X", "story_ids": ["US-01.01"]}, {"title": "Y", "story_ids": ["US-01.02"]}],
        )
    result = backlog.split_feature(
        ADMIN,
        P,
        "FEAT-01.01",
        [
            {"title": "X", "story_ids": ["US-01.01", "US-01.03"]},
            {"title": "Y", "description": "resto", "story_ids": ["US-01.02"]},
        ],
    )
    assert result["split_into"] == ["FEAT-01.02", "FEAT-01.03"]
    feats = {f["id"]: f for f in backlog.get_epic(ADMIN, P, "EPIC-01")["features"]}
    assert feats["FEAT-01.01"]["status"] == "SPLIT" and feats["FEAT-01.01"]["story_ids"] == []
    assert feats["FEAT-01.02"]["story_ids"] == ["US-01.01", "US-01.03"]
    assert feats["FEAT-01.03"]["story_ids"] == ["US-01.02"]
    with pytest.raises(FailedPrecondition):
        _story(backlog, feature="FEAT-01.01")
    with pytest.raises(FailedPrecondition):
        backlog.split_feature(
            ADMIN, P, "FEAT-01.01", [{"title": "A", "story_ids": []}, {"title": "B", "story_ids": []}]
        )


# ---------------------------------------------------------------- US-04.03
@pytest.mark.parametrize("field", ["as_a", "i_want", "so_that"])
def test_us0403_ca01_actor_accion_valor_obligatorios(backlog: BacklogService, field: str) -> None:
    _base(backlog)
    with pytest.raises(InvalidArgument) as err:
        _story(backlog, **{field: " "})
    assert err.value.field == field


def test_us0403_ca02_requisito_de_origen_obligatorio(backlog: BacklogService) -> None:
    _base(backlog)
    with pytest.raises(InvalidArgument) as err:
        _story(backlog, requirement_ids=[])
    assert err.value.field == "requirement_ids"
    with pytest.raises(NotFound):
        _story(backlog, requirement_ids=["REQ-404"])
    assert backlog.get_epic(ADMIN, P, "EPIC-01")["features"][0]["story_ids"] == []


def test_us0403_ca03_criterios_de_aceptacion(backlog: BacklogService) -> None:
    _base(backlog)
    story = _story(backlog, acceptance_criteria=["C1", "C2"])
    assert [c["code"] for c in story["acceptance_criteria"]] == ["CA-01", "CA-02"]
    story = backlog.add_criteria(ADMIN, P, "US-01.01", ["C3"])
    assert [c["code"] for c in story["acceptance_criteria"]] == ["CA-01", "CA-02", "CA-03"]
    with pytest.raises(InvalidArgument):
        backlog.add_criteria(ADMIN, P, "US-01.01", ["  "])


def test_us0403_ca04_incompleta_no_pasa_a_ready(backlog: BacklogService) -> None:
    _base(backlog)
    _story(backlog, acceptance_criteria=[])
    with pytest.raises(FailedPrecondition, match="sin criterios de aceptación"):
        backlog.mark_ready(ADMIN, P, "US-01.01")
    assert backlog.get_story(ADMIN, P, "US-01.01")["status"] == "PLANNED"
    backlog.add_criteria(ADMIN, P, "US-01.01", ["Dado un nombre vacío, entonces se rechaza"])
    assert backlog.mark_ready(ADMIN, P, "US-01.01")["status"] == "READY"
    with pytest.raises(FailedPrecondition, match="READY"):
        backlog.mark_ready(ADMIN, P, "US-01.01")


def test_us0403_ca05_tarea_tecnica_requiere_razon(backlog: BacklogService) -> None:
    _base(backlog)
    with pytest.raises(InvalidArgument) as err:
        _story(backlog, kind="technical")
    assert err.value.field == "technical_reason"
    with pytest.raises(InvalidArgument):
        _story(backlog, kind="task")
    tech = _story(backlog, kind="technical", technical_reason="Migración necesaria para US-18.03")
    assert tech["kind"] == "technical"
    assert _story(backlog)["kind"] == "user_story"
