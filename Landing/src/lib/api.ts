import type { AuthResponse, Department } from '../types'

const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
  })
  const json = await res.json()
  if (!res.ok) {
    throw new Error((json as { error?: string }).error ?? `HTTP ${res.status}`)
  }
  return json as T
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function signup(payload: {
  name: string
  email: string
  password: string
  role: 'citizen' | 'officer'
  department_id?: number
  invite_code?: string
}): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/signup', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getDepartments(): Promise<Department[]> {
  return request<Department[]>('/departments')
}
