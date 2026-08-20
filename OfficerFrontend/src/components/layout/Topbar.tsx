import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { RefreshCw, WifiOff } from 'lucide-react'

const TITLES: Record<string, string> = {
  '/':       'Overview',
  '/queue':  'Grievance Queue',
  '/intake': 'New Intake',
}

interface Props {
  onRefresh?: () => void
  refreshing?: boolean
}

export default function Topbar({ onRefresh, refreshing }: Props) {
  const { pathname } = useLocation()
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)

  const base = '/' + pathname.split('/')[1]
  const title = TITLES[base] ?? 'GrievanceAI'

  useEffect(() => {
    fetch((import.meta.env.VITE_API_URL ?? 'http://localhost:8000') + '/health')
      .then(r => setBackendOnline(r.ok))
      .catch(() => setBackendOnline(false))
  }, [pathname])

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-20">
      <div className="h-14 flex items-center justify-between px-6">
        <div>
          <h1 className="text-sm font-semibold text-gray-900">{title}</h1>
          <p className="text-[11px] text-gray-400">Smart City Civic Portal · Officer View</p>
        </div>

        <div className="flex items-center gap-3">
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-indigo-600 transition-colors disabled:opacity-50"
            >
              <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
              Refresh
            </button>
          )}

          <div className="flex items-center gap-2 text-xs border-l border-gray-100 pl-3">
            {backendOnline === false ? (
              <>
                <WifiOff size={12} className="text-orange-400" />
                <span className="text-orange-500 font-medium">Demo mode</span>
              </>
            ) : backendOnline === true ? (
              <>
                <span className="inline-block w-2 h-2 rounded-full bg-emerald-400" />
                <span className="text-gray-500">Backend connected</span>
              </>
            ) : (
              <>
                <span className="inline-block w-2 h-2 rounded-full bg-gray-300 animate-pulse" />
                <span className="text-gray-400">Connecting…</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Demo mode banner */}
      {backendOnline === false && (
        <div className="bg-orange-50 border-t border-orange-100 px-6 py-1.5 text-[11px] text-orange-600 flex items-center gap-2">
          <WifiOff size={11} />
          Backend not reachable — showing demo data. Start the FastAPI server to use live data.
        </div>
      )}
    </header>
  )
}
