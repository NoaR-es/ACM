// Canal en vivo (US-06.03, US-21.02/03): WebSocket autenticado, reanudación por seq y recarga de datos afectados.
import { useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { useAuth } from "./auth";
import { affectedKeys, authMessage, backoff, receive, type LiveState, type ServerMessage } from "./liveCore";
import type { AcmEvent } from "./types";

export type LiveStatus = "offline" | "connecting" | "live" | "reconnecting";
type Live = {
  status: LiveStatus;
  events: AcmEvent[];
  lastSeq: number | null;
  changedAt: (projectId: string, entityId: string) => number | undefined;
  announcement: string;
};

const LiveContext = createContext<Live | null>(null);
const KEEP_EVENTS = 300;

function describe(e: AcmEvent): string {
  const status = typeof e.data.status === "string" ? ` → ${e.data.status}` : "";
  return `${e.project_id ?? "plataforma"}: ${e.type} ${e.entity_id}${status} (${e.principal})`;
}

export function LiveProvider({ children }: { children: ReactNode }) {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<LiveStatus>("offline");
  const [events, setEvents] = useState<AcmEvent[]>([]);
  const [changed, setChanged] = useState<Record<string, number>>({});
  const [announcement, setAnnouncement] = useState("");
  const state = useRef<LiveState>({ lastSeq: null, needsResync: false });

  useEffect(() => {
    if (!token) {
      setStatus("offline");
      return;
    }
    let socket: WebSocket | null = null;
    let attempt = 0;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    const connect = () => {
      setStatus(attempt === 0 ? "connecting" : "reconnecting");
      const proto = location.protocol === "https:" ? "wss" : "ws";
      socket = new WebSocket(`${proto}://${location.host}/api/v1/ws`);
      socket.onopen = () => socket?.send(authMessage(token, state.current));
      socket.onmessage = (msg) => {
        const data = JSON.parse(msg.data) as ServerMessage;
        if (data.type === "ready") {
          attempt = 0;
          setStatus("live");
          if (state.current.lastSeq === null) queryClient.invalidateQueries();
        }
        const out = receive(state.current, data);
        state.current = out.state;
        if (out.resync) queryClient.invalidateQueries();
        if (out.apply) {
          const e = out.apply;
          for (const key of affectedKeys(e)) queryClient.invalidateQueries({ queryKey: key });
          setEvents((prev) => [e, ...prev].slice(0, KEEP_EVENTS));
          if (e.project_id) setChanged((prev) => ({ ...prev, [`${e.project_id}/${e.entity_id}`]: Date.now() }));
          if (e.type !== "activity") setAnnouncement(describe(e));
        }
      };
      socket.onclose = (ev) => {
        if (stopped) return;
        if (ev.code === 4401) {
          window.dispatchEvent(new CustomEvent("acm:unauthenticated"));
          return;
        }
        setStatus("reconnecting");
        timer = setTimeout(connect, backoff(attempt++));
      };
    };
    connect();
    return () => {
      stopped = true;
      if (timer) clearTimeout(timer);
      socket?.close();
    };
  }, [token, queryClient]);

  const value: Live = {
    status,
    events,
    lastSeq: state.current.lastSeq,
    changedAt: (p, id) => changed[`${p}/${id}`],
    announcement,
  };
  return <LiveContext.Provider value={value}>{children}</LiveContext.Provider>;
}

export function useLive(): Live {
  const ctx = useContext(LiveContext);
  if (!ctx) throw new Error("useLive fuera de LiveProvider");
  return ctx;
}
