import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, Map, Search } from 'lucide-react'
import { useState } from 'react'
import apiClient from '../../lib/axios'

export default function RoadmapsListPage() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')

  const { data, isLoading } = useQuery({
    queryKey: ['roadmaps'],
    queryFn: () => apiClient.get('/api/v1/roadmaps').then((r) => r.data.data),
  })

  const roadmaps = (data || []).filter((r) => {
    const matchSearch = r.title.toLowerCase().includes(search.toLowerCase())
    const matchFilter = filter === 'all' || r.type === filter
    return matchSearch && matchFilter
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">My Roadmaps</h2>
          <p className="text-sm text-gray-500 mt-0.5">{data?.length || 0} total roadmaps</p>
        </div>
        <Link to="/roadmaps/create"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition-colors">
          <Plus size={16} /> New Roadmap
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search roadmaps…"
            className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="flex gap-2">
          {['all', 'academic', 'skill'].map((f) => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-4 py-2.5 rounded-lg text-sm font-medium capitalize transition-colors ${filter === f ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-20 mb-3" />
              <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4" />
              <div className="h-2 bg-gray-200 rounded" />
            </div>
          ))}
        </div>
      ) : roadmaps.length === 0 ? (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-16 text-center">
          <Map size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 mb-4">
            {search || filter !== 'all' ? 'No roadmaps match your search.' : 'Create your first learning roadmap!'}
          </p>
          {!search && filter === 'all' && (
            <Link to="/roadmaps/create"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700">
              <Plus size={16} /> Create Roadmap
            </Link>
          )}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {roadmaps.map((rm) => (
            <Link key={rm._id} to={`/roadmaps/${rm._id}`}
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow block group">
              <div className="flex items-start justify-between mb-3">
                <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${rm.type === 'academic' ? 'bg-indigo-100 text-indigo-700' : 'bg-purple-100 text-purple-700'}`}>
                  {rm.type}
                </span>
                <span className="text-xs text-gray-400">{rm.node_count || 0} nodes</span>
              </div>
              <h3 className="font-semibold text-gray-900 group-hover:text-indigo-700 transition-colors mb-1 line-clamp-2">{rm.title}</h3>
              {rm.goal && <p className="text-xs text-gray-500 mb-3 line-clamp-2">{rm.goal}</p>}
              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Progress</span><span>0%</span>
                </div>
                <div className="h-1.5 bg-gray-100 rounded-full"><div className="h-full bg-indigo-500 rounded-full w-0" /></div>
              </div>
              <p className="text-xs text-gray-400 mt-3">
                {rm.created_at ? new Date(rm.created_at).toLocaleDateString() : ''}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
