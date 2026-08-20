import Badge from './Badge'
import type { GrievanceStatus } from '../../api/types'

const CONFIG: Record<GrievanceStatus, { label: string; variant: 'indigo' | 'green' | 'yellow' | 'red' | 'orange' | 'gray' | 'purple' | 'default' }> = {
  new:         { label: 'New',         variant: 'indigo'  },
  assigned:    { label: 'Assigned',    variant: 'purple'  },
  in_progress: { label: 'In Progress', variant: 'yellow'  },
  escalated:   { label: 'Escalated',   variant: 'red'     },
  resolved:    { label: 'Resolved',    variant: 'green'   },
  closed:      { label: 'Closed',      variant: 'gray'    },
  reopened:    { label: 'Reopened',    variant: 'orange'  },
}

interface Props {
  status: GrievanceStatus
  size?: 'sm' | 'md'
}

export default function StatusBadge({ status, size }: Props) {
  const { label, variant } = CONFIG[status] ?? { label: status, variant: 'default' }
  return <Badge variant={variant} size={size} dot>{label}</Badge>
}
