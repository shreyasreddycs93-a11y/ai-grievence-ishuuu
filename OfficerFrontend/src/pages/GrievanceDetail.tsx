import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  AlertTriangle,
  MapPin,
  Building2,
  Calendar,
  GitBranch,
  CheckCircle2,
  ArrowUpCircle,
  Image as ImageIcon,
  Mic,
  BrainCircuit,
} from 'lucide-react'
import { getGrievanceStatus, updateGrievance, escalateGrievance, CATEGORY_LABELS } from '../api/client'
import type { GrievanceStatusResponse, GrievanceStatus } from '../api/types'
import StatusBadge from '../components/ui/StatusBadge'
import PriorityBadge from '../components/ui/PriorityBadge'
import SLATimer from '../components/ui/SLATimer'
import Modal from '../components/ui/Modal'
import Spinner from '../components/ui/Spinner'
import clsx from 'clsx'

const STATUSES: GrievanceStatus[] = [
  'new', 'assigned', 'in_progress', 'escalated', 'resolved', 'closed', 'reopened',
]

const STATUS_TIMELINE_COLORS: Record<GrievanceStatus, string> = {
  new: 'bg-indigo-500',
  assigned: 'bg-purple-500',
  in_progress: 'bg-yellow-500',
  escalated: 'bg-red-500',
  resolved: 'bg-emerald-500',
  closed: 'bg-gray-400',
  reopened: 'bg-orange-500',
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export default function GrievanceDetail() {
  const { trackingId } = useParams<{ trackingId: string }>()
  const navigate = useNavigate()

  const [data, setData] = useState<GrievanceStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Update status modal
  const [updateOpen, setUpdateOpen] = useState(false)
  const [newStatus, setNewStatus] = useState<GrievanceStatus>('in_progress')
  const [updateNote, setUpdateNote] = useState('')
  const [updateLoading, setUpdateLoading] = useState(false)
  const [updateError, setUpdateError] = useState<string | null>(null)

  // Escalate modal
  const [escalateOpen, setEscalateOpen] = useState(false)
  const [escalateReason, setEscalateReason] = useState('')
  const [escalateTo, setEscalateTo] = useState('')
  const [escalateLoading, setEscalateLoading] = useState(false)
  const [escalateError, setEscalateError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!trackingId) return
    setLoading(true)
    setError(null)
    try {
      const d = await getGrievanceStatus(trackingId)
      setData(d)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load grievance')
    } finally {
      setLoading(false)
    }
  }, [trackingId])

  useEffect(() => { load() }, [load])

  // updateGrievance resolves the numeric PK from the id cache internally.
  // If the backend hasn't returned an id yet (Gap #2), it throws a clear error.
  async function handleUpdateStatus() {
    if (!trackingId) return
    setUpdateLoading(true)
    setUpdateError(null)
    try {
      await updateGrievance(trackingId, {
        status: newStatus,
        note: updateNote || undefined,
        changed_by: 'officer',
      })
      setUpdateOpen(false)
      setUpdateNote('')
      await load()
    } catch (e: unknown) {
      setUpdateError(e instanceof Error ? e.message : 'Update failed')
    } finally {
      setUpdateLoading(false)
    }
  }

  async function handleEscalate() {
    if (!trackingId) return
    setEscalateLoading(true)
    setEscalateError(null)
    try {
      await escalateGrievance(trackingId, {
        reason: escalateReason || undefined,
        escalated_to: escalateTo || undefined,
        changed_by: 'officer',
      })
      setEscalateOpen(false)
      setEscalateReason('')
      setEscalateTo('')
      await load()
    } catch (e: unknown) {
      setEscalateError(e instanceof Error ? e.message : 'Escalation failed')
    } finally {
      setEscalateLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex flex-col items-center gap-4 py-20 text-gray-500">
        <AlertTriangle size={36} className="text-red-400" />
        <p className="text-sm font-medium">{error ?? 'Grievance not found'}</p>
        <button
          onClick={() => navigate('/queue')}
          className="text-sm text-indigo-600 hover:underline"
        >
          ← Back to queue
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      {/* Back */}
      <button
        onClick={() => navigate('/queue')}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-indigo-600 transition-colors"
      >
        <ArrowLeft size={15} />
        Back to queue
      </button>

      {/* Header card */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-xs font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-lg">
                {data.tracking_id}
              </span>
              {data.status === 'escalated' && (
                <span className="flex items-center gap-1 text-xs text-red-600 bg-red-50 px-2 py-0.5 rounded-lg">
                  <AlertTriangle size={11} /> Escalated
                </span>
              )}
            </div>
            <h2 className="text-lg font-bold text-gray-900 mt-2 leading-snug max-w-xl">
              {data.summary ?? 'No summary available'}
            </h2>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2 shrink-0">
            <button
              onClick={() => { setNewStatus(data.status); setUpdateOpen(true) }}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition"
            >
              <CheckCircle2 size={15} />
              Update Status
            </button>
            {data.status !== 'escalated' && data.status !== 'closed' && (
              <button
                onClick={() => setEscalateOpen(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition border border-red-200"
              >
                <ArrowUpCircle size={15} />
                Escalate
              </button>
            )}
          </div>
        </div>

        {/* Meta grid */}
        <div className="mt-5 grid grid-cols-2 sm:grid-cols-5 gap-4">
          <MetaCard icon={<Building2 size={15} />} label="Department" value={data.department ?? '—'} />
          <MetaCard icon={<Calendar size={15} />} label="Submitted" value={formatDate(data.created_at)} />
          <MetaCard
            icon={<MapPin size={15} />}
            label="Location"
            value={data.address ?? 'Not provided'}
          />
          <MetaCard
            icon={<GitBranch size={15} />}
            label="Category"
            value={CATEGORY_LABELS[data.category]}
          />
          <MetaCard
            icon={<BrainCircuit size={15} />}
            label="AI Confidence"
            value={`${Math.round(data.confidence * 100)}%`}
            valueClassName={data.confidence < 0.6 ? 'text-orange-600' : 'text-emerald-600'}
          />
        </div>

        {/* Badges row */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <StatusBadge status={data.status} size="md" />
          <PriorityBadge priority={data.priority} size="md" />
          <SLATimer sla_due_at={data.sla_due_at} />
        </div>
      </div>

      {/* Attached media */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Attached Media {data.media.length > 0 && `(${data.media.length})`}
        </h3>
        {data.media.length === 0 ? (
          <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center gap-3 border-2 border-dashed border-gray-200 rounded-xl px-4 py-5 text-gray-400">
              <ImageIcon size={20} className="text-gray-300" />
              <p className="text-xs font-medium text-gray-500">No photo attached</p>
            </div>
            <div className="flex items-center gap-3 border-2 border-dashed border-gray-200 rounded-xl px-4 py-5 text-gray-400">
              <Mic size={20} className="text-gray-300" />
              <p className="text-xs font-medium text-gray-500">No voice note attached</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {data.media.map((m, i) =>
              m.type === 'image' ? (
                <a
                  key={i}
                  href={m.url}
                  target="_blank"
                  rel="noreferrer"
                  className="block overflow-hidden rounded-xl border border-gray-200 hover:opacity-90 transition"
                >
                  <img src={m.url} alt="Attached complaint media" className="w-full h-40 object-cover" />
                </a>
              ) : m.type === 'audio' ? (
                <div key={i} className="flex flex-col gap-2 border border-gray-200 rounded-xl px-4 py-4">
                  <div className="flex items-center gap-2 text-xs font-medium text-gray-500">
                    <Mic size={15} className="text-gray-400" />
                    Voice note
                  </div>
                  <audio controls src={m.url} className="w-full h-9" />
                </div>
              ) : (
                <a
                  key={i}
                  href={m.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-3 border border-gray-200 rounded-xl px-4 py-4 text-indigo-600 hover:bg-indigo-50/50 transition text-xs font-medium"
                >
                  View attachment ({m.type})
                </a>
              ),
            )}
          </div>
        )}
      </div>

      {/* Subtasks */}
      {data.subtasks.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Sub-tickets ({data.subtasks.length})
          </h3>
          <div className="space-y-2">
            {data.subtasks.map(sub => (
              <div
                key={sub.tracking_id}
                className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-indigo-50/50 transition"
                onClick={() => navigate(`/queue/${sub.tracking_id}`)}
              >
                <span className="font-mono text-xs font-semibold text-indigo-600">
                  {sub.tracking_id}
                </span>
                <span className="text-xs text-gray-500">{sub.department ?? '—'}</span>
                <StatusBadge status={sub.status} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Status Timeline</h3>
        {data.timeline.length === 0 ? (
          <p className="text-xs text-gray-400">No history yet.</p>
        ) : (
          <ol className="relative border-l-2 border-gray-100 ml-2 space-y-5">
            {[...data.timeline].reverse().map((entry, i) => (
              <li key={i} className="ml-5">
                <span
                  className={clsx(
                    'absolute -left-[9px] w-4 h-4 rounded-full border-2 border-white',
                    STATUS_TIMELINE_COLORS[entry.status] ?? 'bg-gray-300',
                  )}
                />
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge status={entry.status} />
                  <span className="text-[11px] text-gray-400">{formatDate(entry.at)}</span>
                </div>
                {entry.note && (
                  <p className="mt-1 text-xs text-gray-500 max-w-md">{entry.note}</p>
                )}
              </li>
            ))}
          </ol>
        )}
      </div>

      {/* Update Status Modal */}
      <Modal open={updateOpen} onClose={() => setUpdateOpen(false)} title="Update Status">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1.5">New status</label>
            <select
              value={newStatus}
              onChange={e => setNewStatus(e.target.value as GrievanceStatus)}
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
            >
              {STATUSES.map(s => (
                <option key={s} value={s}>{s.replace('_', ' ')}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1.5">
              Note <span className="font-normal text-gray-400">(optional)</span>
            </label>
            <textarea
              value={updateNote}
              onChange={e => setUpdateNote(e.target.value)}
              rows={3}
              placeholder="Add a note for the record…"
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
            />
          </div>
          {updateError && (
            <p className="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{updateError}</p>
          )}
          <div className="flex gap-2 pt-1">
            <button
              onClick={handleUpdateStatus}
              disabled={updateLoading}
              className="flex-1 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition disabled:opacity-60"
            >
              {updateLoading ? 'Saving…' : 'Save update'}
            </button>
            <button
              onClick={() => setUpdateOpen(false)}
              className="px-4 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </div>
      </Modal>

      {/* Escalate Modal */}
      <Modal open={escalateOpen} onClose={() => setEscalateOpen(false)} title="Escalate Grievance">
        <div className="space-y-4">
          <p className="text-xs text-gray-500">
            Manual escalation bypasses the SLA timer — use this for VIP complaints,
            media attention, or legal threats.
          </p>
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1.5">Escalate to</label>
            <input
              type="text"
              value={escalateTo}
              onChange={e => setEscalateTo(e.target.value)}
              placeholder="e.g. Senior Officer, Commissioner…"
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1.5">Reason</label>
            <textarea
              value={escalateReason}
              onChange={e => setEscalateReason(e.target.value)}
              rows={3}
              placeholder="Why is this being escalated?"
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
            />
          </div>
          {escalateError && (
            <p className="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{escalateError}</p>
          )}
          <div className="flex gap-2 pt-1">
            <button
              onClick={handleEscalate}
              disabled={escalateLoading}
              className="flex-1 py-2.5 rounded-xl bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition disabled:opacity-60"
            >
              {escalateLoading ? 'Escalating…' : 'Confirm escalation'}
            </button>
            <button
              onClick={() => setEscalateOpen(false)}
              className="px-4 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

function MetaCard({
  icon, label, value, valueClassName,
}: {
  icon: React.ReactNode
  label: string
  value: string
  valueClassName?: string
}) {
  return (
    <div className="bg-gray-50 rounded-xl px-4 py-3">
      <div className="flex items-center gap-1.5 text-gray-400 text-[11px] font-semibold uppercase tracking-wide mb-1">
        {icon}
        {label}
      </div>
      <p className={clsx('text-sm font-medium text-gray-800 truncate', valueClassName)}>{value}</p>
    </div>
  )
}
