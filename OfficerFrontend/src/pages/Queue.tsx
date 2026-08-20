import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, SlidersHorizontal, AlertTriangle, ChevronRight } from 'lucide-react'
import { getQueue, DEPARTMENTS } from '../api/client'
import type { QueueItem, GrievanceStatus, Priority } from '../api/types'
import StatusBadge from '../components/ui/StatusBadge'
import PriorityBadge from '../components/ui/PriorityBadge'
import SLATimer from '../components/ui/SLATimer'
import Spinner from '../components/ui/Spinner'
import { CATEGORY_LABELS } from '../api/client'
import clsx from 'clsx'

const STATUSES: GrievanceStatus[] = ['new', 'assigned', 'in_progress', 'escalated', 'resolved', 'closed', 'reopened']
const PRIORITIES: Priority[] = ['low', 'medium', 'high', 'critical']

export default function Queue() {
  const navigate = useNavigate()
  const [items, setItems] = useState<QueueItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState<GrievanceStatus | ''>('')
  const [filterPriority, setFilterPriority] = useState<Priority | ''>('')
  const [filterDeptId, setFilterDeptId] = useState<number | undefined>()
  const [showFilters, setShowFilters] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getQueue({
        status: filterStatus || undefined,
        priority: filterPriority || undefined,
        department_id: filterDeptId,
      })
      setItems(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load queue')
    } finally {
      setLoading(false)
    }
  }, [filterStatus, filterPriority, filterDeptId])

  useEffect(() => { load() }, [load])

  const filtered = items.filter(item =>
    !search ||
    item.tracking_id.toLowerCase().includes(search.toLowerCase()) ||
    (item.summary ?? '').toLowerCase().includes(search.toLowerCase()) ||
    (item.department ?? '').toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-4">
      {/* Search + filter bar */}
      <div className="bg-white rounded-2xl border border-gray-100 p-4 flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by tracking ID, summary, department…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 transition"
            />
          </div>
          <button
            onClick={() => setShowFilters(v => !v)}
            className={clsx(
              'flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border transition',
              showFilters
                ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
            )}
          >
            <SlidersHorizontal size={15} />
            Filters
            {(filterStatus || filterPriority || filterDeptId) && (
              <span className="ml-1 w-2 h-2 rounded-full bg-indigo-600" />
            )}
          </button>
          <button
            onClick={load}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 transition disabled:opacity-60"
          >
            Refresh
          </button>
        </div>

        {showFilters && (
          <div className="flex flex-wrap gap-3 pt-1">
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Department</label>
              <select
                value={filterDeptId ?? ''}
                onChange={e => setFilterDeptId(e.target.value ? Number(e.target.value) : undefined)}
                className="text-sm border border-gray-200 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              >
                <option value="">All departments</option>
                {DEPARTMENTS.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Status</label>
              <select
                value={filterStatus}
                onChange={e => setFilterStatus(e.target.value as GrievanceStatus | '')}
                className="text-sm border border-gray-200 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              >
                <option value="">All statuses</option>
                {STATUSES.map(s => (
                  <option key={s} value={s}>{s.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Priority</label>
              <select
                value={filterPriority}
                onChange={e => setFilterPriority(e.target.value as Priority | '')}
                className="text-sm border border-gray-200 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              >
                <option value="">All priorities</option>
                {PRIORITIES.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            {(filterStatus || filterPriority || filterDeptId) && (
              <div className="flex items-end">
                <button
                  onClick={() => { setFilterStatus(''); setFilterPriority(''); setFilterDeptId(undefined) }}
                  className="text-xs text-indigo-600 hover:underline"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Count */}
      {!loading && !error && (
        <p className="text-xs text-gray-400 px-1">
          {filtered.length} grievance{filtered.length !== 1 ? 's' : ''}
          {search && ` matching "${search}"`}
        </p>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl px-5 py-4 text-sm">
          <AlertTriangle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-16">
          <Spinner size="lg" />
        </div>
      )}

      {/* Empty */}
      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-16 text-gray-400 bg-white rounded-2xl border border-gray-100">
          <p className="text-sm font-medium">No grievances found</p>
          <p className="text-xs mt-1">Try adjusting your filters</p>
        </div>
      )}

      {/* Table */}
      {!loading && filtered.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50/60">
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Tracking ID</th>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Summary</th>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Category</th>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Department</th>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Priority</th>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">AI Confidence</th>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Status</th>
                  <th className="text-left px-5 py-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">SLA</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody>
                {filtered.map((item, i) => (
                  <tr
                    key={item.tracking_id}
                    onClick={() => navigate(`/queue/${item.tracking_id}`)}
                    className={clsx(
                      'border-b border-gray-50 cursor-pointer transition-colors hover:bg-indigo-50/40',
                      i % 2 === 0 ? 'bg-white' : 'bg-gray-50/30',
                    )}
                  >
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-indigo-600">{item.tracking_id}</span>
                        {item.needs_human_review && (
                          <span title="Needs human review" className="text-orange-400">
                            <AlertTriangle size={12} />
                          </span>
                        )}
                        {item.parent_tracking_id && (
                          <span className="text-[10px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-full">sub</span>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 max-w-[220px]">
                      <p className="truncate text-gray-700">{item.summary ?? '—'}</p>
                    </td>
                    <td className="px-5 py-3.5 text-gray-500">{CATEGORY_LABELS[item.category]}</td>
                    <td className="px-5 py-3.5 text-gray-600">{item.department ?? <span className="text-gray-300">—</span>}</td>
                    <td className="px-5 py-3.5"><PriorityBadge priority={item.priority} /></td>
                    <td className="px-5 py-3.5">
                      <span className={clsx(
                        'text-xs font-semibold',
                        item.confidence < 0.6 ? 'text-orange-600' : 'text-emerald-600',
                      )}>
                        {Math.round(item.confidence * 100)}%
                      </span>
                    </td>
                    <td className="px-5 py-3.5"><StatusBadge status={item.status} /></td>
                    <td className="px-5 py-3.5"><SLATimer sla_due_at={item.sla_due_at} /></td>
                    <td className="px-4 py-3.5 text-gray-300">
                      <ChevronRight size={16} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
