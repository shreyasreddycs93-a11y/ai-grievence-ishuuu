export type Role = 'citizen' | 'officer'
export type AuthMode = 'login' | 'signup'

export interface Department {
  id: number
  name: string
  sla_hours: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  account: {
    id: number
    name: string
    email: string
    role: Role
    department_id: number | null
  }
}
