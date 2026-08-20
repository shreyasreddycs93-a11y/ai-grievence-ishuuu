import { useEffect, useState } from 'react'
import { Clock } from 'lucide-react'
import clsx from 'clsx'

interface Props {
  sla_due_at: string | null
}

function calcRemaining(dueAt: string | null): { label: string; urgent: boolean; overdue: boolean } {
  if (!dueAt) return { label: 'No SLA', urgent: false, overdue: false }

  const diff = new Date(dueAt).getTime() - Date.now()

  if (diff <= 0) {
    const abs = Math.abs(diff)
    const h = Math.floor(abs / 3_600_000)
    const m = Math.floor((abs % 3_600_000) / 60_000)
    return { label: `Overdue ${h}h ${m}m`, urgent: true, overdue: true }
  }

  const h = Math.floor(diff / 3_600_000)
  const m = Math.floor((diff % 3_600_000) / 60_000)

  if (h < 2) return { label: `${h}h ${m}m left`, urgent: true, overdue: false }
  if (h < 6) return { label: `${h}h ${m}m left`, urgent: false, overdue: false }
  return { label: `${h}h left`, urgent: false, overdue: false }
}

export default function SLATimer({ sla_due_at }: Props) {
  const [state, setState] = useState(() => calcRemaining(sla_due_at))

  useEffect(() => {
    setState(calcRemaining(sla_due_at))
    const interval = setInterval(() => setState(calcRemaining(sla_due_at)), 60_000)
    return () => clearInterval(interval)
  }, [sla_due_at])

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 text-xs font-medium',
        state.overdue ? 'text-red-600' : state.urgent ? 'text-orange-500' : 'text-gray-500',
      )}
    >
      <Clock size={12} />
      {state.label}
    </span>
  )
}
