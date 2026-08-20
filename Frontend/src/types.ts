export type Language = 'en' | 'hi' | 'kn';

export type GrievanceStatus =
  | 'new'
  | 'assigned'
  | 'in_progress'
  | 'escalated'
  | 'resolved'
  | 'closed'
  | 'reopened';

export interface TimelineEntry {
  status: string;
  note: string;
  at: string;
}

export interface Subtask {
  id?: string;
  department: string;
  status: string;
  category?: string;
  priority?: string;
  summary?: string;
  timeline?: TimelineEntry[];
}

export interface GrievanceStatusResponse {
  tracking_id: string;
  status: GrievanceStatus;
  category: string;
  priority: string;
  department: string;
  summary: string;
  created_at: string;
  sla_due_at: string;
  timeline: TimelineEntry[];
  subtasks: Subtask[];
}

export interface IntakeResponse {
  tracking_id: string;
  status?: string;
  message?: string;
}

export interface VerifyResponse {
  confirmed: boolean;
  message?: string;
}

export interface MyGrievanceItem {
  tracking_id: string;
  status: GrievanceStatus;
  category: string;
  priority: string;
  department: string | null;
  summary: string | null;
  created_at: string;
}

export interface MediaUploadResponse {
  media_url: string;
  kind: 'image' | 'audio';
  transcript?: string | null;
  description?: string | null;
}

export type Screen = 'home' | 'report' | 'track' | 'my-complaints';
