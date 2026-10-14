// Tipos de la API REST v1 de ACM (06_API/rest_api.md).
import type { StoryStatus } from "./theme";

export type Criterion = { code: string; text: string };
export type Story = {
  id: string;
  project_id?: string;
  epic_id: string;
  feature_id: string;
  kind: "user_story" | "technical";
  as_a: string;
  i_want: string;
  so_that: string;
  technical_reason: string;
  status: StoryStatus;
  created_at: string;
  created_by: string;
  updated_at: string;
  requirement_ids: string[];
  acceptance_criteria: Criterion[];
  sprint_id: string | null;
};
export type StoryDetail = Story & {
  history: { from_status: string; to_status: string; reason: string; changed_at: string; changed_by: string }[];
  allowed_transitions: StoryStatus[];
};
export type Requirement = { id: string; title: string; description: string; created_at: string; created_by: string };
export type Feature = {
  id: string;
  epic_id: string;
  title: string;
  description: string;
  status: "ACTIVE" | "SPLIT";
  split_into: string;
  story_ids: string[];
};
export type Epic = {
  id: string;
  title: string;
  objective: string;
  scope: string;
  coverage_confirmed_at: string | null;
  coverage_confirmed_by: string | null;
  requirement_ids: string[];
  features: Feature[];
};
export type Gaps = Record<string, string[] | boolean | string> & { clean: boolean };
export type Backlog = { project_id: string; requirements: Requirement[]; epics: Epic[]; stories: Story[]; gaps: Gaps };
export type Semaphore = "GREEN" | "AMBER" | "RED" | "UNKNOWN";
export type Finding = {
  code: string;
  severity: "CRITICAL" | "WARNING" | "REVIEW" | "INFO";
  target: string;
  message: string;
  source: string;
  engine?: string;
  confidence?: number | null;
};
export type WatchdogRun = {
  id: number;
  ts: string;
  trigger: string;
  principal: string;
  semaphore: Semaphore;
  critical: number;
  warning: number;
  review: number;
  info: number;
  findings: Finding[];
  engines: string[];
  duration_ms: number;
  report: string;
  report_engine: string;
  actions: SupervisorAction[];
  summary: SupervisorSummary;
};
// Supervisor ágil autónomo (SPRINT-008, US-13.14/13.15)
export type SupervisorAction = {
  type: string;
  target: string;
  reason: string;
  engine: string;
  calibrated: boolean;
  confidence: number | null;
  safe: boolean;
  applied: boolean;
  error?: string;
  from?: string;
  to?: string;
  sprint_id?: string;
};
export type SupervisorSummary = {
  done?: string[];
  verified?: string[];
  in_progress?: string[];
  blocked?: string[];
  pending?: string[];
  active_sprint?: {
    id: string;
    goal: string;
    end_date: string;
    done: number;
    stories: number;
    completion_pct: number;
    risk?: string;
    risk_engine?: string;
  } | null;
  notes?: string[];
};
// Sprints (EPIC-05)
export type Sprint = {
  id: string;
  name: string;
  goal: string;
  start_date: string;
  end_date: string;
  capacity: number | null;
  status: "PLANNED" | "ACTIVE" | "CLOSED" | "CANCELLED";
  story_ids: string[];
  history: { story_id: string; outcome: string; ended_at: string; status: StoryStatus }[];
  stories_by_status: Partial<Record<StoryStatus, number>>;
  load: number;
  overloaded: boolean;
  summary: {
    text?: string;
    done?: string[];
    not_done?: string[];
    completion_pct?: number;
    carried_over_to?: string | null;
  };
  created_at: string;
  started_at: string | null;
  closed_at: string | null;
  warnings?: string[];
};
// Modelos (US-50.09/10)
export type ModelGuide = { summary: string; best_for: string; size: string; notes: string; types: string[] };
export type AvailableModel = {
  name: string;
  details: Record<string, unknown>;
  default?: boolean;
  purposes?: string[];
  note?: string;
  guide?: ModelGuide | null;
};
export type ModelCatalog = {
  purposes: Record<string, string>;
  seen_purposes: string[];
  usage: Record<string, string>;
  ollama: { configured: boolean; hint?: string; endpoint?: string; selected?: string | null; source?: string; available?: AvailableModel[]; error?: string };
  jev: {
    configured: boolean;
    hint?: string;
    endpoint?: string;
    default_model?: string | null;
    source?: string;
    models_by_purpose?: Record<string, string>;
    available?: AvailableModel[];
    error?: string;
    guide?: { source: string; choosing: string[]; acm_suggestions: Record<string, string> };
  };
};
// Conversación con el modelo local (US-22.10/11)
export type ChatThread = { id: string; title: string; created_by: string; created_at: string; updated_at: string; messages: number };
export type ChatMessage = {
  role: "user" | "assistant" | "tool";
  content: string;
  tool_name: string;
  tool_calls: { function: { name: string; arguments: unknown } }[];
  model: string;
  principal: string;
  created_at: string;
};
export type ChatReply = {
  thread_id: string;
  reply: string;
  model: string;
  tool_calls: { name: string; arguments: Record<string, unknown>; ok: boolean }[];
  context_messages: number;
};
export type Governance = {
  project_id: string;
  semaphore: Semaphore;
  last_run: Omit<WatchdogRun, "findings" | "engines" | "principal" | "duration_ms"> | null;
  integrity: { integrity_status: string; integrity_detail: string; integrity_checked_at: string | null };
  writable: boolean;
  history?: WatchdogRun[];
};
export type PortfolioProject = {
  project_id: string;
  name: string;
  description: string;
  created_at: string;
  created_by: string;
  governance: Governance;
  stories_by_status: Record<StoryStatus, number>;
  stories: number;
};
export type Card = {
  project_id: string;
  id: string;
  status: StoryStatus;
  i_want: string;
  as_a: string;
  so_that: string;
  kind: string;
  feature_id: string;
  epic_id: string;
  requirement_ids: string[];
  updated_at: string;
  criteria: number;
  sprint_id: string | null;
  assigned_to: string | null; // agente (y sesión) que tiene la historia asignada, si lo hay
};
export type JoinRequest = {
  request_id: number;
  project_id: string;
  project_name: string;
  principal_id: string;
  kind: "user" | "agent";
  access: "read" | "write";
  message: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  created_at: string;
  decided_at: string | null;
  decided_by: string | null;
  granted_role: "member" | "viewer" | null;
};
export type Kanban = {
  projects: string[];
  sprint?: string | null;
  columns: StoryStatus[];
  transitions: Record<StoryStatus, StoryStatus[]>;
  cards: Card[];
  latest_event_seq: number;
};
export type Me = {
  id: string;
  role: "admin" | "user";
  kind: "user" | "agent";
  created_at: string;
  projects: { project_id: string; role: string }[];
  active_tokens: number;
};
export type AcmEvent = {
  seq: number;
  ts: string;
  type: string;
  project_id: string | null;
  principal: string;
  entity_type: string;
  entity_id: string;
  data: Record<string, unknown>;
};
