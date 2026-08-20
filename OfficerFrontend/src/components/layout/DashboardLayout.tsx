import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'

interface Props {
  onRefresh?: () => void
  refreshing?: boolean
}

export default function DashboardLayout({ onRefresh, refreshing }: Props) {
  return (
    <div className="min-h-screen bg-[#F8F9FB]">
      <Sidebar />
      <div className="pl-64 flex flex-col min-h-screen">
        <Topbar onRefresh={onRefresh} refreshing={refreshing} />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
        <footer className="text-center py-4 text-[11px] text-gray-400 border-t border-gray-100">
          GrievanceAI · Smart India Hackathon · Built for citizens, powered by AI
        </footer>
      </div>
    </div>
  )
}
