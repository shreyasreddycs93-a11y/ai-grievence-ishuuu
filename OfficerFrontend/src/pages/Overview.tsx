import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  Shield,
  Flame,
} from 'lucide-react'
import { getQueue, CATEGORY_LABELS } from '../api/client'
import type { QueueItem, GrievanceStatus } from '../api/types'
import StatusBadge from '../components/ui/StatusBadge'
import PriorityBadge from '../components/ui/PriorityBadge'
import SLATimer from '../components/ui/SLATimer'
import Spinner from '../components/ui/Spinner'

interface Stats {
  total: number
  open: number
  resolved: number
  escalated: number
  needsReview: number
  overdueSLA: number
  byStatus: Record<GrievanceStatus, number>
}

function computeStats(items: QueueItem[]): Stats {
  const OPEN: GrievanceStatus[] = ['new', 'assigned', 'in_progress', 'reopened']
  const byStatus = {} as Record<GrievanceStatus, number>

  let open = 0, resolved = 0, escalated = 0, needsReview = 0, overdueSLA = 0

  for (const item of items) {
    byStatus[item.status] = (byStatus[item.status] ?? 0) + 1
    if (OPEN.includes(item.status)) open++
    if (item.status === 'resolved' || item.status === 'closed') resolved++
    if (item.status === 'escalated') escalated++
    if (item.needs_human_review) needsReview++
    if (item.sla_due_at && new Date(item.sla_due_at).getTime() < Date.now() && OPEN.includes(item.status)) {
      overdueSLA++
    }
  }

  return { total: items.length, open, resolved, escalated, needsReview, overdueSLA, byStatus }
}

export default function Overview() {
  const navigate = useNavigate()
  const [items, setItems] = useState<QueueItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setItems(await getQueue())
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl px-5 py-4 text-sm max-w-lg">
        <AlertTriangle size={16} className="shrink-0" />
        {error}
        <button onClick={load} className="ml-auto text-xs underline">Retry</button>
      </div>
    )
  }

  const stats = computeStats(items)

  // Top 5 critical/high priority open items
  const urgent = items
    .filter(i => ['new', 'assigned', 'in_progress', 'reopened'].includes(i.status))
    .filter(i => i.priority === 'critical' || i.priority === 'high')
    .slice(0, 5)

  // Top 5 flagged for human review
  const flagged = items.filter(i => i.needs_human_review).slice(0, 5)

  // Category breakdown
  const catCount: Record<string, number> = {}
  for (const item of items) {
    catCount[item.category] = (catCount[item.category] ?? 0) + 1
  }
  const topCategories = Object.entries(catCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)

  const resolutionRate = stats.total > 0
    ? Math.round((stats.resolved / stats.total) * 100)
    : 0

  return (
    <div className="space-y-6">

      {/* Hero banner */}
      <div className="bg-indigo-600 rounded-2xl px-6 py-5 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Shield size={14} className="text-indigo-200" />
            <span className="text-xs text-indigo-200 font-semibold uppercase tracking-wide">
              Officer Dashboard
            </span>
          </div>
          <h2 className="text-white text-xl font-bold">Good to see you, Officer.</h2>
          <p className="text-indigo-200 text-sm mt-0.5">
            {stats.open} open grievance{stats.open !== 1 ? 's' : ''} need your attention today.
          </p>
        </div>
        <button
          onClick={() => navigate('/queue')}
          className="flex items-center gap-2 bg-white text-indigo-700 text-sm font-semibold px-4 py-2.5 rounded-xl hover:bg-indigo-50 transition shrink-0"
        >
          View queue <ArrowRight size={14} />
        </button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<TrendingUp size={18} className="text-indigo-600" />}
          iconBg="bg-indigo-100"
          label="Total Grievances"
          value={stats.total}
        />
        <StatCard
          icon={<Clock size={18} className="text-yellow-600" />}
          iconBg="bg-yellow-100"
          label="Open"
          value={stats.open}
          sub={`${resolutionRate}% resolved`}
        />
        <StatCard
          icon={<CheckCircle2 size={18} className="text-emerald-600" />}
          iconBg="bg-emerald-100"
          label="Resolved / Closed"
          value={stats.resolved}
        />
        <StatCard
          icon={<AlertTriangle size={18} className="text-red-600" />}
          iconBg="bg-red-100"
          label="Escalated"
          value={stats.escalated}
          alert={stats.escalated > 0}
        />
      </div>

      {/* Secondary stat cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl border border-gray-100 p-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center shrink-0">
            <Flame size={18} className="text-orange-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900">{stats.overdueSLA}</p>
            <p className="text-xs text-gray-500 mt-0.5">Overdue SLA</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 p-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center shrink-0">
            <Shield size={18} className="text-purple-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900">{stats.needsReview}</p>
            <p className="text-xs text-gray-500 mt-0.5">Need human review</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Urgent items */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-800">Urgent — High &amp; Critical</h3>
            <button
              onClick={() => navigate('/queue')}
              className="text-xs text-indigo-600 hover:underline flex items-center gap-1"
            >
              View all <ArrowRight size={11} />
            </button>
          </div>
          {urgent.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-6">No urgent items right now.</p>
          ) : (
            <div className="space-y-2">
              {urgent.map(item => (
                <div
                  key={item.tracking_id}
                  onClick={() => navigate(`/queue/${item.tracking_id}`)}
                  className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-indigo-50/50 transition"
                >
                  <span className="font-mono text-xs font-semibold text-indigo-600 shrink-0">
                    {item.tracking_id}
                  </span>
                  <p className="text-xs text-gray-700 flex-1 truncate">{item.summary ?? '—'}</p>
                  <div className="flex items-center gap-2 shrink-0">
                    <PriorityBadge priority={item.priority} />
                    <SLATimer sla_due_at={item.sla_due_at} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Category breakdown */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">By Category</h3>
          {topCategories.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-6">No data yet.</p>
          ) : (
            <div className="space-y-2.5">
              {topCategories.map(([cat, count]) => (
                <div key={cat}>
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>{CATEGORY_LABELS[cat as keyof typeof CATEGORY_LABELS] ?? cat}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-500 rounded-full transition-all"
                      style={{ width: `${Math.round((count / stats.total) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Flagged for review */}
      {flagged.length > 0 && (
        <div className="bg-white rounded-2xl border border-orange-100 p-5">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={15} className="text-orange-500" />
            <h3 className="text-sm font-semibold text-gray-800">Needs Human Review</h3>
            <span className="ml-auto text-xs text-gray-400">{flagged.length} items</span>
          </div>
          <div className="space-y-2">
            {flagged.map(item => (
              <div
                key={item.tracking_id}
                onClick={() => navigate(`/queue/${item.tracking_id}`)}
                className="flex items-center gap-3 px-4 py-3 bg-orange-50/50 rounded-xl cursor-pointer hover:bg-orange-50 transition"
              >
                <span className="font-mono text-xs font-semibold text-indigo-600 shrink-0">
                  {item.tracking_id}
                </span>
                <p className="text-xs text-gray-700 flex-1 truncate">{item.summary ?? '—'}</p>
                <div className="flex items-center gap-2 shrink-0">
                  <StatusBadge status={item.status} />
                  <PriorityBadge priority={item.priority} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({
  icon, iconBg, label, value, sub, alert,
}: {
  icon: React.ReactNode
  iconBg: string
  label: string
  value: number
  sub?: string
  alert?: boolean
}) {
  return (
    <div className={`bg-white rounded-2xl border p-5 ${alert && value > 0 ? 'border-red-200' : 'border-gray-100'}`}>
      <div className={`w-10 h-10 rounded-xl ${iconBg} flex items-center justify-center mb-3`}>
        {icon}
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500 mt-0.5">{label}</p>
      {sub && <p className="text-[11px] text-gray-400 mt-0.5">{sub}</p>}
    </div>
  )
}
