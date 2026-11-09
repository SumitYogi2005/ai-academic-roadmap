import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, BookOpen, Map, Clock } from 'lucide-react'
import apiClient from '../../lib/axios'

const COLORS = ['#10b981', '#f59e0b', '#e5e7eb']

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => apiClient.get('/api/v1/analytics/summary').then((r) => r.data.data),
  })

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )

  const roadmaps = analytics?.roadmaps || []
  const barData = roadmaps.map((r) => ({
    name: r.title.length > 20 ? r.title.slice(0, 20) + '…' : r.title,
    completed: r.completed_nodes,
    remaining: r.total_nodes - r.completed_nodes,
  }))

  const pieData = [
    { name: 'Completed', value: analytics?.completed_nodes || 0 },
    { name: 'In Progress', value: Math.max(0, (analytics?.total_nodes || 0) - (analytics?.completed_nodes || 0) - 1) },
    { name: 'Not Started', value: Math.max(0, (analytics?.total_nodes || 0) - (analytics?.completed_nodes || 0)) },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Progress Analytics</h2>
        <p className="text-sm text-gray-500 mt-0.5">Your learning journey at a glance</p>
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Map, label: 'Active Roadmaps', value: analytics?.active_roadmaps || 0, color: 'bg-indigo-500' },
          { icon: BookOpen, label: 'Topics Completed', value: analytics?.completed_nodes || 0, color: 'bg-green-500' },
          { icon: TrendingUp, label: 'Overall Progress', value: `${analytics?.overall_completion || 0}%`, color: 'bg-purple-500' },
          { icon: Clock, label: "Today's Sessions", value: analytics?.today_sessions || 0, color: 'bg-amber-500' },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="bg-white border border-gray-200 rounded-xl p-5 flex items-center gap-4">
            <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${color}`}>
              <Icon size={20} className="text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
              <p className="text-xs text-gray-500">{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Bar chart */}
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Completion by Roadmap</h3>
          {barData.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-gray-400 text-sm">No roadmaps yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} margin={{ top: 0, right: 10, bottom: 40, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="completed" stackId="a" fill="#10b981" name="Completed" radius={[0, 0, 0, 0]} />
                <Bar dataKey="remaining" stackId="a" fill="#e5e7eb" name="Remaining" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Pie chart */}
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Topic Status Overview</h3>
          {analytics?.total_nodes === 0 ? (
            <div className="h-48 flex items-center justify-center text-gray-400 text-sm">No topics yet</div>
          ) : (
            <div className="flex items-center gap-6">
              <ResponsiveContainer width="60%" height={200}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={3} dataKey="value">
                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-3">
                {pieData.map((entry, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: COLORS[i] }} />
                    <span className="text-gray-600">{entry.name}</span>
                    <span className="font-semibold text-gray-900 ml-auto">{entry.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Roadmap breakdown */}
      {roadmaps.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Roadmap Breakdown</h3>
          <div className="space-y-4">
            {roadmaps.map((rm) => (
              <div key={rm.id}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium text-gray-900 truncate max-w-[70%]">{rm.title}</span>
                  <span className="text-gray-500 ml-2 flex-shrink-0">{rm.completed_nodes}/{rm.total_nodes} topics</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full transition-all" style={{ width: `${rm.completion_percentage}%` }} />
                </div>
                <p className="text-xs text-gray-400 mt-0.5">{rm.completion_percentage}% complete</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
