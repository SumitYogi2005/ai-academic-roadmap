import { Menu, Bell } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

const PAGE_TITLES = {
  '/dashboard': 'Dashboard',
  '/roadmaps': 'My Roadmaps',
  '/roadmaps/create': 'Create Roadmap',
  '/study-planner': 'Study Planner',
  '/assistant': 'AI Assistant',
  '/analytics': 'Analytics',
  '/settings': 'Settings',
}

export default function AppHeader({ onMenuClick }) {
  const location = useLocation()
  const user = useAuthStore((s) => s.user)

  const title =
    PAGE_TITLES[location.pathname] ||
    (location.pathname.startsWith('/roadmaps/') ? 'Roadmap' : 'AI Academic Roadmap')

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 flex-shrink-0">
      {/* Mobile menu button */}
      <button
        onClick={onMenuClick}
        className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 lg:hidden"
      >
        <Menu size={20} />
      </button>

      <h1 className="text-lg font-semibold text-gray-900 flex-1">{title}</h1>

      <div className="flex items-center gap-3">
        <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 relative">
          <Bell size={20} />
        </button>
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-semibold text-sm">
          {user?.full_name?.[0]?.toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  )
}
