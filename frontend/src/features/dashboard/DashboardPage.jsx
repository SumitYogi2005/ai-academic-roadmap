import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Map, Calendar, Bot, Plus, BookOpen, TrendingUp, Clock, Target } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import apiClient from '../../lib/axios'

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value ?? '—'}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  const { data: analyticsData } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => apiClient.get('/api/v1/analytics/summary').then((r) => r.data.data),
  })

  const { data: plansData } = useQuery({
    queryKey: ['plans'],
    queryFn: () => apiClient.get('/api/v1/study-plans').then((r) => r.data.data),
  })

  const roadmaps = analyticsData?.roadmaps || []
  const latestRoadmaps = roadmaps.slice(0, 3)

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white">
        <h2 className="text-xl font-semibold mb-1">
          Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}! 👋
        </h2>
        <p className="text-indigo-200 text-sm">Keep up the great work on your learning journey.</p>
        <div className="flex gap-3 mt-4">
          <Link to="/roadmaps/create"
            className="flex items-center gap-2 px-4 py-2 bg-white text-indigo-700 text-sm font-semibold rounded-lg hover:bg-indigo-50 transition-colors">
            <Plus size={16} /> New Roadmap
          </Link>
          <Link to="/study-planner"
            className="flex items-center gap-2 px-4 py-2 bg-indigo-500 bg-opacity-50 text-white text-sm font-semibold rounded-lg hover:bg-opacity-60 transition-colors">
            <Calendar size={16} /> Open Planner
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Map} label="Active Roadmaps" value={analyticsData?.active_roadmaps} color="bg-indigo-500" />
        <StatCard icon={BookOpen} label="Topics Completed" value={analyticsData?.completed_nodes} color="bg-green-500" />
        <StatCard icon={Clock} label="Today's Sessions" value={analyticsData?.today_sessions} color="bg-amber-500" />
        <StatCard icon={TrendingUp} label="Overall Progress" value={analyticsData ? `${analyticsData.overall_completion}%` : null} color="bg-purple-500" />
      </div>

      {/* Active Roadmaps */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Active Roadmaps</h3>
          <Link to="/roadmaps" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">View all</Link>
        </div>
        {latestRoadmaps.length === 0 ? (
          <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
            <Map size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 mb-4">No roadmaps yet. Create your first one!</p>
            <Link to="/roadmaps/create"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700">
              <Plus size={16} /> Create Roadmap
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {latestRoadmaps.map((rm) => (
              <Link key={rm.id} to={`/roadmaps/${rm.id}`}
                className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow block">
                <div className="flex items-start justify-between mb-3">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${rm.type === 'academic' ? 'bg-indigo-100 text-indigo-700' : 'bg-purple-100 text-purple-700'}`}>
                    {rm.type}
                  </span>
                  <span className="text-xs text-gray-400">{rm.total_nodes} nodes</span>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2">{rm.title}</h4>
                <div className="mt-auto">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Progress</span>
                    <span>{rm.completion_percentage}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${rm.completion_percentage}%` }} />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { to: '/roadmaps/create', icon: Map, label: 'New Roadmap', color: 'bg-indigo-50 text-indigo-600' },
            { to: '/study-planner', icon: Calendar, label: 'Study Planner', color: 'bg-green-50 text-green-600' },
            { to: '/assistant', icon: Bot, label: 'AI Assistant', color: 'bg-purple-50 text-purple-600' },
          ].map(({ to, icon: Icon, label, color }) => (
            <Link key={to} to={to}
              className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col items-center gap-3 hover:shadow-md transition-shadow text-center">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
                <Icon size={22} />
              </div>
              <span className="text-sm font-medium text-gray-700">{label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
