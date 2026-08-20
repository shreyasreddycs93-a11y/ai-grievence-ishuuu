import { useState, useEffect } from 'react'
import {
  BrainCircuit,
  Users,
  Landmark,
  ArrowLeft,
  Eye,
  EyeOff,
  Loader2,
} from 'lucide-react'
import type { Role, AuthMode, Department } from './types'
import { login, signup, getDepartments } from './lib/api'

// Same-origin paths — the backend serves all three apps off one port (see
// Backend/app/main.py). Override via env only if serving them separately.
const CITIZEN_URL = import.meta.env.VITE_CITIZEN_URL ?? '/citizen/'
const OFFICER_URL = import.meta.env.VITE_OFFICER_URL ?? '/officer/'

interface Props {
  initialRole: Role
  onBack: () => void
}

export default function AuthScreen({ initialRole, onBack }: Props) {
  const [role, setRole] = useState<Role>(initialRole)
  const [mode, setMode] = useState<AuthMode>('login')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [departments, setDepartments] = useState<Department[]>([])

  // form fields
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [departmentId, setDepartmentId] = useState<number | ''>('')
  const [inviteCode, setInviteCode] = useState('')

  // Load departments for officer signup
  useEffect(() => {
    if (role === 'officer' && mode === 'signup' && departments.length === 0) {
      getDepartments()
        .then(setDepartments)
        .catch(() => {
          // fallback static list when backend not reachable
          setDepartments([
            { id: 1, name: 'Water Board', sla_hours: 24 },
            { id: 2, name: 'Roads', sla_hours: 48 },
            { id: 3, name: 'Sanitation', sla_hours: 24 },
            { id: 4, name: 'Electricity', sla_hours: 12 },
            { id: 5, name: 'Parks', sla_hours: 72 },
          ])
        })
    }
  }, [role, mode, departments.length])

  function resetForm() {
    setName('')
    setEmail('')
    setPassword('')
    setDepartmentId('')
    setInviteCode('')
    setError('')
  }

  function handleRoleSwitch(r: Role) {
    setRole(r)
    resetForm()
  }

  function handleModeSwitch(m: AuthMode) {
    setMode(m)
    resetForm()
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      let data

      if (mode === 'login') {
        data = await login(email, password)
      } else {
        if (!name.trim()) { setError('Name is required'); setLoading(false); return }
        if (role === 'officer' && !departmentId) { setError('Please select a department'); setLoading(false); return }
        if (role === 'officer' && !inviteCode.trim()) { setError('Invite code is required for officer accounts'); setLoading(false); return }

        data = await signup({
          name: name.trim(),
          email,
          password,
          role,
          ...(role === 'officer' && departmentId ? { department_id: Number(departmentId) } : {}),
          ...(role === 'officer' ? { invite_code: inviteCode.trim() } : {}),
        })
      }

      localStorage.setItem('grievance_token', data.access_token)
      localStorage.setItem('grievance_role', data.account.role)

      // redirect to the appropriate app
      window.location.href = data.account.role === 'officer' ? OFFICER_URL : CITIZEN_URL
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F8F9FB] font-['Inter',sans-serif] flex flex-col">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center gap-3">
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft size={16} />
            Back
          </button>
          <span className="text-gray-200">|</span>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
              <BrainCircuit size={15} className="text-white" />
            </div>
            <span className="font-bold text-gray-900">CivicSahayak</span>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">

          {/* Role toggle */}
          <div className="flex rounded-xl border border-gray-200 bg-white p-1 mb-6 shadow-sm">
            <button
              onClick={() => handleRoleSwitch('citizen')}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                role === 'citizen'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Users size={16} />
              Citizen
            </button>
            <button
              onClick={() => handleRoleSwitch('officer')}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                role === 'officer'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Landmark size={16} />
              Officer
            </button>
          </div>

          {/* Card */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
            {/* Mode tabs */}
            <div className="flex border-b border-gray-100 mb-7">
              <button
                onClick={() => handleModeSwitch('login')}
                className={`flex-1 pb-3 text-sm font-semibold border-b-2 transition-colors ${
                  mode === 'login'
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                }`}
              >
                Log in
              </button>
              <button
                onClick={() => handleModeSwitch('signup')}
                className={`flex-1 pb-3 text-sm font-semibold border-b-2 transition-colors ${
                  mode === 'signup'
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                }`}
              >
                Create account
              </button>
            </div>

            <h1 className="text-xl font-bold text-gray-900 mb-1">
              {mode === 'login' ? 'Welcome back' : 'Create your account'}
            </h1>
            <p className="text-sm text-gray-500 mb-6">
              {role === 'citizen'
                ? mode === 'login'
                  ? 'Sign in to track and manage your complaints.'
                  : 'Register to submit and track civic complaints.'
                : mode === 'login'
                  ? 'Sign in to access your officer dashboard.'
                  : 'Create an officer account with your department invite code.'}
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name — signup only */}
              {mode === 'signup' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Full name
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="Priya Sharma"
                    className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                  />
                </div>
              )}

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Email address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={8}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder={mode === 'signup' ? 'Min. 8 characters' : '••••••••'}
                    className="w-full px-3.5 py-2.5 pr-10 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Officer-only: department + invite code */}
              {role === 'officer' && mode === 'signup' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Department
                    </label>
                    <select
                      required
                      value={departmentId}
                      onChange={e => setDepartmentId(Number(e.target.value))}
                      className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition bg-white"
                    >
                      <option value="">Select your department</option>
                      {departments.map(d => (
                        <option key={d.id} value={d.id}>{d.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Officer invite code
                    </label>
                    <input
                      type="text"
                      required
                      value={inviteCode}
                      onChange={e => setInviteCode(e.target.value)}
                      placeholder="Provided by your department admin"
                      className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      Contact your department administrator for the invite code.
                    </p>
                  </div>
                </>
              )}

              {/* Error */}
              {error && (
                <div className="rounded-lg bg-red-50 border border-red-100 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors mt-2 shadow-md shadow-indigo-100"
              >
                {loading && <Loader2 size={16} className="animate-spin" />}
                {loading
                  ? 'Please wait…'
                  : mode === 'login'
                    ? 'Sign in'
                    : 'Create account'}
              </button>
            </form>
          </div>

          <p className="text-center text-xs text-gray-400 mt-5">
            CivicSahayak · Smart India Hackathon 2026
          </p>
        </div>
      </div>
    </div>
  )
}
