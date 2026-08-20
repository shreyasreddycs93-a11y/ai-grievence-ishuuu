import clsx from 'clsx'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'indigo' | 'green' | 'yellow' | 'red' | 'orange' | 'gray' | 'purple'
  size?: 'sm' | 'md'
  dot?: boolean
}

const VARIANTS = {
  default: 'bg-gray-100 text-gray-700',
  indigo: 'bg-indigo-100 text-indigo-700',
  green: 'bg-emerald-100 text-emerald-700',
  yellow: 'bg-yellow-100 text-yellow-700',
  red: 'bg-red-100 text-red-700',
  orange: 'bg-orange-100 text-orange-700',
  gray: 'bg-gray-100 text-gray-500',
  purple: 'bg-purple-100 text-purple-700',
}

const DOT_VARIANTS = {
  default: 'bg-gray-400',
  indigo: 'bg-indigo-500',
  green: 'bg-emerald-500',
  yellow: 'bg-yellow-500',
  red: 'bg-red-500',
  orange: 'bg-orange-500',
  gray: 'bg-gray-400',
  purple: 'bg-purple-500',
}

export default function Badge({ children, variant = 'default', size = 'sm', dot }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full font-medium',
        size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3 py-1 text-sm',
        VARIANTS[variant],
      )}
    >
      {dot && (
        <span className={clsx('h-1.5 w-1.5 rounded-full', DOT_VARIANTS[variant])} />
      )}
      {children}
    </span>
  )
}
