// Mirrors Pydantic schemas from grievanceai backend (app/schemas.py + app/models.py)

export type GrievanceStatus =
  | 'new'
  | 'assigned'
  | 'in_progress'
  | 'escalated'
  | 'resolved'
  | 'closed'
  | 'reopened'

export type Priority = 'low' | 'medium' | 'high' | 'critical'

export type Category =
  | 'water_supply'
  | 'roads'
  | 'sanitation'
  | 'electricity'
  | 'streetlights'
  | 'drainage'
  | 'garbage'
  | 'parks'
  | 'other'

// GET /auth/me  →  Account
export interface Account {
  id: number
  name: string
  email: string
  role: 'citizen' | 'officer'
  department_id: number | null
}

// GET /admin/queue  →  QueueItem[]
// NOTE (Gap #2): The backend QueueItem schema does NOT expose the internal
// integer PK. PATCH /admin/grievance/{id} requires that PK. Until the backend
// adds an `id` field to QueueItem, the frontend cannot reliably call
// update/escalate without a workaround. We include id as optional here so
// that if the backend adds it later the client picks it up automatically.
export interface QueueItem {
  id?: number               // internal PK — not yet returned by backend (Gap #2)
  tracking_id: string
  status: GrievanceStatus
  category: Category
  priority: Priority
  department: string | null
  summary: string | null
  confidence: number
  needs_human_review: boolean
  created_at: string        // ISO datetime
  sla_due_at: string | null // ISO datetime
  parent_tracking_id: string | null
  report_count: number      // >1 means the backend merged repeat reports of this same issue
}

// GET /grievance/{tracking_id}/status  →  GrievanceStatusResponse
export interface TimelineEntry {
  status: GrievanceStatus
  note: string | null
  at: string // ISO datetime
}

export interface SubtaskEntry {
  tracking_id: string
  department: string | null
  status: GrievanceStatus
}

export interface MediaItem {
  type: string // "image" | "audio" | "video" | "other"
  url: string
}

export interface GrievanceStatusResponse {
  tracking_id: string
  status: GrievanceStatus
  category: Category
  priority: Priority
  department: string | null
  summary: string | null
  address: string | null
  confidence: number
  created_at: string
  sla_due_at: string | null
  report_count: number
  timeline: TimelineEntry[]
  subtasks: SubtaskEntry[]
  media: MediaItem[]
}

// PATCH /admin/grievance/{id}  →  QueueItem
export interface AdminUpdateRequest {
  status: GrievanceStatus
  note?: string
  changed_by?: string
}

// POST /admin/grievance/{id}/escalate  →  EscalateResponse
export interface EscalateRequest {
  reason?: string
  escalated_to?: string
  changed_by?: string
}

export interface EscalateResponse {
  tracking_id: string
  status: GrievanceStatus
  escalated_to: string | null
  reason: string | null
}

// POST /intake/web  →  IntakeResponse
export interface WebIntakeRequest {
  description: string
  address?: string
  lat?: number
  lng?: number
  language?: string
  media_url?: string
}

export interface IntakeResponse {
  tracking_id: string
  status: GrievanceStatus
  category: Category
  priority: Priority
  department: string | null
  summary: string | null
  merged: boolean
  split: boolean
  subtask_tracking_ids: string[]
}
