import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ListFilter,
  FilePlus,
  Shield,
  LogOut,
  Bell,
} from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/',       icon: LayoutDashboard, label: 'Overview'  },
  { to: '/queue',  icon: ListFilter,      label: 'Queue'     },
  { to: '/intake', icon: FilePlus,        label: 'New Intake'},
]

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex flex-col w-64 bg-white border-r border-gray-100">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-gray-100">
        <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-indigo-600">
          <Shield size={18} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-bold text-gray-900 leading-tight">GrievanceAI</p>
          <p className="text-[11px] text-gray-400 leading-tight">Officer Dashboard</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="px-3 pb-2 text-[10px] font-semibold text-gray-400 uppercase tracking-widest">
          Menu
        </p>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={18}
                  className={clsx(
                    'shrink-0',
                    isActive ? 'text-indigo-600' : 'text-gray-400',
                  )}
                />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="px-3 py-4 border-t border-gray-100 space-y-0.5">
        <button className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-all">
          <Bell size={18} className="text-gray-400 shrink-0" />
          Notifications
        </button>
        <button className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 transition-all">
          <LogOut size={18} className="text-gray-400 shrink-0" />
          Sign out
        </button>
      </div>

      {/* Officer pill */}
      <div className="px-4 pb-4">
        <div className="flex items-center gap-3 bg-gray-50 rounded-xl px-3 py-2.5">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
            OF
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-gray-800 truncate">Officer</p>
            <p className="text-[11px] text-gray-400 truncate">Smart City Portal</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
