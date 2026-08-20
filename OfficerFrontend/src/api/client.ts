import type {
  Account,
  AdminUpdateRequest,
  EscalateRequest,
  EscalateResponse,
  GrievanceStatusResponse,
  IntakeResponse,
  QueueItem,
  WebIntakeRequest,
  Category,
  GrievanceStatus,
  Priority,
} from './types'
import { MOCK_QUEUE, getMockDetail } from './mockData'

// Base URL — adjust if backend moves to a different host/port
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// Set to true to force mock mode regardless of backend status
const FORCE_MOCK = false

class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new ApiError(res.status, text)
  }
  return res.json() as Promise<T>
}

// Wraps a real API call with mock fallback on network error
async function withMockFallback<T>(realFn: () => Promise<T>, mockFn: () => T): Promise<T> {
  if (FORCE_MOCK) return mockFn()
  try {
    return await realFn()
  } catch (e) {
    // Fall back to mock only on network/fetch errors (backend not running)
    if (e instanceof TypeError || (e instanceof ApiError && e.status === 0)) {
      return mockFn()
    }
    throw e
  }
}

// ── Gap #2 fix: tracking_id → numeric id cache ───────────────────────────────
// PATCH /admin/grievance/{id} requires the internal integer PK, but QueueItem
// doesn't expose it yet. We cache whatever the backend returns (id field is
// optional in QueueItem) so that if/when the backend adds it we pick it up.
// Until then, update/escalate will surface a clear error rather than silently
// sending the wrong value.
const _idCache = new Map<string, number>() // tracking_id → numeric PK

function cacheIds(items: QueueItem[]) {
  for (const item of items) {
    if (item.id != null) _idCache.set(item.tracking_id, item.id)
  }
}

function resolveId(trackingId: string): number {
  const id = _idCache.get(trackingId)
  if (id == null) {
    throw new ApiError(
      0,
      `Cannot update "${trackingId}": the backend does not yet expose the internal ` +
      `numeric id in GET /admin/queue (Gap #2). Ask the backend team to add "id" ` +
      `to the QueueItem schema.`,
    )
  }
  return id
}

// ── Gap #7 fix: hardcoded department list ────────────────────────────────────
// There is no GET /departments endpoint. The 5 seeded departments and their
// known integer PKs are hardcoded here. Update if the backend seed changes.
export const DEPARTMENTS: { id: number; name: string }[] = [
  { id: 1, name: 'Water Board' },
  { id: 2, name: 'Roads' },
  { id: 3, name: 'Sanitation' },
  { id: 4, name: 'Electricity' },
  { id: 5, name: 'Parks' },
]

// ── Auth ─────────────────────────────────────────────────────────────────────
// Token/role are written to localStorage by the Landing app on login/signup.

const TOKEN_KEY = 'grievance_token'
const ROLE_KEY = 'grievance_role'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export async function getMe(): Promise<Account> {
  const token = getToken()
  if (!token) throw new ApiError(401, 'Not authenticated')
  return request<Account>('/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
}

export function signOut(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(ROLE_KEY)
  window.location.href = '/'
}

// ── Admin endpoints ──────────────────────────────────────────────────────────

export interface QueueFilters {
  department_id?: number
  status?: GrievanceStatus
  priority?: Priority
}

export function getQueue(filters?: QueueFilters): Promise<QueueItem[]> {
  const params = new URLSearchParams()
  if (filters?.department_id != null) params.set('department_id', String(filters.department_id))
  if (filters?.status) params.set('status', filters.status)
  if (filters?.priority) params.set('priority', filters.priority)
  const qs = params.toString()
  return withMockFallback(
    async () => {
      const items = await request<QueueItem[]>(`/admin/queue${qs ? `?${qs}` : ''}`)
      cacheIds(items) // cache any ids the backend returns
      return items
    },
    () => {
      let items = [...MOCK_QUEUE]
      if (filters?.status) items = items.filter(i => i.status === filters.status)
      if (filters?.priority) items = items.filter(i => i.priority === filters.priority)
      return items
    },
  )
}

export function updateGrievance(trackingId: string, payload: AdminUpdateRequest): Promise<QueueItem> {
  return withMockFallback(
    () => {
      const id = resolveId(trackingId) // throws with a clear message if id unknown
      return request<QueueItem>(`/admin/grievance/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
    },
    () => {
      // Mock: find and update the item in-memory
      const item = MOCK_QUEUE.find(i => i.tracking_id === trackingId)
      if (!item) throw new ApiError(404, `Grievance ${trackingId} not found`)
      item.status = payload.status
      return { ...item }
    },
  )
}

export function escalateGrievance(trackingId: string, payload: EscalateRequest): Promise<EscalateResponse> {
  return withMockFallback(
    () => {
      const id = resolveId(trackingId)
      return request<EscalateResponse>(`/admin/grievance/${id}/escalate`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    },
    () => {
      const item = MOCK_QUEUE.find(i => i.tracking_id === trackingId)
      if (!item) throw new ApiError(404, `Grievance ${trackingId} not found`)
      item.status = 'escalated'
      return {
        tracking_id: item.tracking_id,
        status: 'escalated' as GrievanceStatus,
        escalated_to: payload.escalated_to ?? null,
        reason: payload.reason ?? null,
      }
    },
  )
}

// ── Citizen / tracking endpoint (used by officer for lookup) ─────────────────

export function getGrievanceStatus(trackingId: string): Promise<GrievanceStatusResponse> {
  return withMockFallback(
    () => request<GrievanceStatusResponse>(`/grievance/${trackingId}/status`),
    () => getMockDetail(trackingId),
  )
}

// ── Intake endpoint ──────────────────────────────────────────────────────────

export function submitIntake(payload: WebIntakeRequest): Promise<IntakeResponse> {
  return withMockFallback(
    () => request<IntakeResponse>('/intake/web', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
    () => ({
      tracking_id: `GRV-${Math.floor(10000 + Math.random() * 90000)}`,
      status: 'new' as GrievanceStatus,
      category: 'other' as Category,
      priority: 'medium' as Priority,
      department: 'Roads',
      summary: payload.description.slice(0, 140),
      merged: false,
      split: false,
      subtask_tracking_ids: [],
    }),
  )
}

// ── Future: file upload stub (not yet implemented in backend) ────────────────
// When backend adds POST /intake/upload, replace this stub.
export async function uploadMedia(_file: File): Promise<{ url: string }> {
  // TODO: wire up to real endpoint (Gap #4 — media URLs not yet exposed)
  throw new ApiError(501, 'File upload endpoint not yet implemented on the backend.')
}

// ── Label helpers ─────────────────────────────────────────────────────────────

export const CATEGORY_LABELS: Record<Category, string> = {
  water_supply: 'Water Supply',
  roads: 'Roads',
  sanitation: 'Sanitation',
  electricity: 'Electricity',
  streetlights: 'Streetlights',
  drainage: 'Drainage',
  garbage: 'Garbage',
  parks: 'Parks',
  other: 'Other',
}

export const STATUS_LABELS: Record<GrievanceStatus, string> = {
  new: 'New',
  assigned: 'Assigned',
  in_progress: 'In Progress',
  escalated: 'Escalated',
  resolved: 'Resolved',
  closed: 'Closed',
  reopened: 'Reopened',
}

export const PRIORITY_LABELS: Record<Priority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
}

export { ApiError }
