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
};
export type Kanban = {
  projects: string[];
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
