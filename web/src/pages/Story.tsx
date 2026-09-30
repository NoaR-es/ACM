// Detalle de historia (US-06.06): enunciado, criterios, trazabilidad, estado, historial y contexto compacto.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, post } from "../api";
import { Empty, ErrorBox, fmtDate, Loading, Section, StatusBadge } from "../components";
import { STATUS_LABEL, type StoryStatus } from "../theme";
import type { StoryDetail } from "../types";
import { useBacklog } from "./Project";

type Compact = {
  sections: { name: string; content: string; sources: string[]; summarized: boolean }[];
  delivered_tokens: number;
  full_equivalent_tokens: number;
  saved_tokens: number;
  estimation_method: string;
  summarized: boolean;
  not_summarized_reason: string;
};

export function StoryPage() {
  const { projectId = "", storyId = "" } = useParams();
  const queryClient = useQueryClient();
  const story = useQuery({
    queryKey: ["story", projectId, storyId],
    queryFn: () => api<StoryDetail>(`/projects/${projectId}/stories/${storyId}`),
  });
  const backlog = useBacklog(projectId);
  const [reason, setReason] = useState("");
  const [showContext, setShowContext] = useState(false);
  const context = useQuery({
    queryKey: ["context", projectId, storyId],
    queryFn: () => api<Compact>(`/projects/${projectId}/context/${storyId}`),
    enabled: showContext,
  });
  const move = useMutation({
    mutationFn: (to: StoryStatus) =>
      story.data?.status === "PLANNED" && to === "READY"
        ? post(`/projects/${projectId}/stories/${storyId}/ready`)
        : post(`/projects/${projectId}/stories/${storyId}/status`, { status: to, reason }),
    onSuccess: () => {
      setReason("");
      queryClient.invalidateQueries({ queryKey: ["story", projectId, storyId] });
    },
  });
  if (story.isPending) return <Loading what="historia" />;
  if (story.error) return <ErrorBox error={story.error} />;
  const s = story.data;
  const epic = backlog.data?.epics.find((e) => e.id === s.epic_id);
  const feature = epic?.features.find((f) => f.id === s.feature_id);
  const reqs = backlog.data?.requirements.filter((r) => s.requirement_ids.includes(r.id)) ?? [];
  const targets: StoryStatus[] = s.status === "PLANNED" ? ["READY", ...s.allowed_transitions] : s.allowed_transitions;
  return (
    <div className="page">
      <p className="breadcrumb">
        <Link to="/">Panel</Link> / <Link to={`/p/${projectId}`}>{projectId}</Link> /{" "}
        <Link to={`/p/${projectId}/backlog`}>{s.epic_id}</Link> / {s.feature_id} / {s.id}
      </p>
      <h1>
        {s.id} <StatusBadge status={s.status} /> {s.kind === "technical" && <span className="tag">técnica</span>}
      </h1>
      <Section title="Enunciado">
        <p className="statement">
          Como <strong>{s.as_a}</strong>, quiero <strong>{s.i_want}</strong>, para <strong>{s.so_that}</strong>.
        </p>
        {s.technical_reason && <p>Razón técnica: {s.technical_reason}</p>}
        <p className="small muted">
          Creada por {s.created_by} el {fmtDate(s.created_at)} · actualizada {fmtDate(s.updated_at)}
        </p>
      </Section>
      <Section title={`Criterios de aceptación (${s.acceptance_criteria.length})`}>
        {s.acceptance_criteria.length === 0 ? (
          <Empty>Sin criterios: no puede pasar a READY.</Empty>
        ) : (
          <ol className="criteria">
            {s.acceptance_criteria.map((c) => (
              <li key={c.code}>
                <strong>{c.code}</strong> {c.text}
              </li>
            ))}
          </ol>
        )}
      </Section>
      <div className="grid-2">
        <Section title="Trazabilidad">
          <dl className="kv">
            <dt>Requisitos</dt>
            <dd>{reqs.length ? reqs.map((r) => <div key={r.id}><strong>{r.id}</strong> {r.title}</div>) : s.requirement_ids.join(", ")}</dd>
            <dt>Épica</dt>
            <dd>{epic ? `${epic.id} — ${epic.title}` : s.epic_id}</dd>
            <dt>Feature</dt>
            <dd>{feature ? `${feature.id} — ${feature.title}` : s.feature_id}</dd>
          </dl>
        </Section>
        <Section title="Estado">
          {targets.length === 0 ? (
            <Empty>Estado terminal: no admite más cambios.</Empty>
          ) : (
            <>
              <label>
                Motivo (opcional){" "}
                <input value={reason} onChange={(e) => setReason(e.target.value)} maxLength={500} />
              </label>
              <div className="row">
                {targets.map((t) => (
                  <button key={t} type="button" onClick={() => move.mutate(t)} disabled={move.isPending}>
                    → {STATUS_LABEL[t]}
                  </button>
                ))}
              </div>
            </>
          )}
          {move.error && <ErrorBox error={move.error} />}
        </Section>
      </div>
      <Section title="Historial de estados">
        {s.history.length === 0 ? (
          <Empty>Sin cambios de estado todavía.</Empty>
        ) : (
          <ol className="timeline">
            {s.history.map((h, i) => (
              <li key={i}>
                <span className="small muted">{fmtDate(h.changed_at)}</span> {STATUS_LABEL[h.from_status as StoryStatus] ?? h.from_status} →{" "}
                <strong>{STATUS_LABEL[h.to_status as StoryStatus] ?? h.to_status}</strong> por {h.changed_by}
                {h.reason && <em> — {h.reason}</em>}
              </li>
            ))}
          </ol>
        )}
      </Section>
      <Section
        title="Contexto compacto para agentes (segundo cerebro)"
        actions={
          !showContext && (
            <button type="button" onClick={() => setShowContext(true)}>
              Generar
            </button>
          )
        }
      >
        {showContext && context.isPending && <Loading what="contexto" />}
        {context.error && <ErrorBox error={context.error} />}
        {context.data && (
          <>
            <p>
              Entregados <strong>{context.data.delivered_tokens}</strong> tokens frente a{" "}
              <strong>{context.data.full_equivalent_tokens}</strong> del contexto completo (ahorro{" "}
              {context.data.saved_tokens}; método <code>{context.data.estimation_method}</code>).{" "}
              {context.data.summarized ? "Resumido con modelo local." : context.data.not_summarized_reason}
            </p>
            {context.data.sections.map((sec) => (
              <details key={sec.name}>
                <summary>
                  {sec.name} <span className="muted small">fuentes: {sec.sources.join(", ") || "—"}</span>
                  {sec.summarized && <span className="tag">resumida</span>}
                </summary>
                <pre className="pre">{sec.content}</pre>
              </details>
            ))}
          </>
        )}
      </Section>
    </div>
  );
}
