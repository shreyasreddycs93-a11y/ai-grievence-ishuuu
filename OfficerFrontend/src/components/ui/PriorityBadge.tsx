import Badge from './Badge'
import type { Priority } from '../../api/types'

const CONFIG: Record<Priority, { label: string; variant: 'green' | 'yellow' | 'orange' | 'red' }> = {
  low:      { label: 'Low',      variant: 'green'  },
  medium:   { label: 'Medium',   variant: 'yellow' },
  high:     { label: 'High',     variant: 'orange' },
  critical: { label: 'Critical', variant: 'red'    },
}

interface Props {
  priority: Priority
  size?: 'sm' | 'md'
}

export default function PriorityBadge({ priority, size }: Props) {
  const { label, variant } = CONFIG[priority] ?? { label: priority, variant: 'yellow' }
  return <Badge variant={variant} size={size}>{label}</Badge>
}
