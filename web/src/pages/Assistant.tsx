// Asistente local del proyecto (US-22.10, US-22.11): conversación con el modelo de Ollama en hilos que ACM conserva.
// El modelo consulta él mismo el proyecto con herramientas de solo lectura; aquí se ve qué herramientas usó.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, post } from "../api";
import { Empty, ErrorBox, fmtDate, Loading, Markdown, Section } from "../components";
import { submit, useAction } from "../forms";
import type { ChatMessage, ChatReply, ChatThread } from "../types";

export function AssistantView({ projectId }: { projectId: string }) {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [text, setText] = useState("");
  const threads = useQuery({
    queryKey: ["chat", projectId, "threads"],
    queryFn: () => api<{ threads: ChatThread[] }>(`/projects/${projectId}/chat/threads`),
  });
  const thread = useQuery({
    queryKey: ["chat", projectId, "thread", threadId],
    queryFn: () => api<{ messages: ChatMessage[]; title: string }>(`/projects/${projectId}/chat/threads/${threadId}`),
    enabled: threadId !== null,
  });
  const send = useAction(
    (message: string) => post<ChatReply>(`/projects/${projectId}/chat`, { message, thread_id: threadId }),
    [["chat", projectId]],
  );
  const ask = () => {
    const message = text.trim();
    if (!message) return;
    send.mutate(message, {
      onSuccess: (r) => {
        setThreadId(r.thread_id);
        setText("");
      },
    });
  };
  return (
    <div className="grid-docs">
      <Section title="Hilos">
        <button type="button" onClick={() => setThreadId(null)} className={threadId === null ? "primary" : ""}>
          + Nueva conversación
        </button>
        {threads.isPending && <Loading what="hilos" />}
        {threads.error && <ErrorBox error={threads.error} />}
        <ul className="nav-list">
          {threads.data?.threads.map((t) => (
            <li key={t.id}>
              <button type="button" className={`link${t.id === threadId ? " active" : ""}`} onClick={() => setThreadId(t.id)}>
                {t.id} · {t.title}
              </button>
              <span className="small muted"> {t.messages} mensajes · {fmtDate(t.updated_at)}</span>
            </li>
          ))}
        </ul>
      </Section>
      <Section title={threadId ? `Conversación ${threadId}` : "Nueva conversación con el modelo local"}>
        <p className="small muted">
          El modelo local de Ollama consulta por sí mismo el backlog, las historias, los sprints y la gobernanza del
          proyecto (solo lectura, con tus permisos). ACM conserva el hilo: no hace falta repetir el contexto.
        </p>
        <div className="chat" aria-live="polite">
          {threadId === null && !send.isPending && <Empty>Pregunta, por ejemplo: «¿Qué historias están bloqueadas y por qué?»</Empty>}
          {thread.data?.messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role}`}>
              {m.role === "user" && <strong>{m.principal}: </strong>}
              {m.role === "assistant" && m.tool_calls.length > 0 ? (
                <span className="small muted">
                  Consulta ACM: {m.tool_calls.map((c) => c.function.name).join(", ")}
                </span>
              ) : m.role === "tool" ? (
                <details>
                  <summary className="small">Resultado de {m.tool_name}</summary>
                  <pre className="pre small">{m.content.slice(0, 2000)}</pre>
                </details>
              ) : m.role === "assistant" ? (
                <>
                  <span className="small muted">{m.model}</span>
                  <Markdown text={m.content} />
                </>
              ) : (
                m.content
              )}
            </div>
          ))}
          {send.isPending && <p className="muted" role="status">El modelo local está pensando…</p>}
        </div>
        <form className="form" aria-label="Mensaje al asistente" onSubmit={submit(ask)}>
          <label className="field">
            <span className="field-label">Mensaje</span>
            <textarea value={text} onChange={(e) => setText(e.target.value)} maxLength={20000} />
          </label>
          <button className="primary" disabled={send.isPending || !text.trim()}>Enviar</button>
        </form>
        {send.error && <ErrorBox error={send.error} />}
        {send.data && send.data.tool_calls.length > 0 && (
          <p className="small muted">Última respuesta: usó {send.data.tool_calls.map((c) => c.name).join(", ")}.</p>
        )}
      </Section>
    </div>
  );
}
