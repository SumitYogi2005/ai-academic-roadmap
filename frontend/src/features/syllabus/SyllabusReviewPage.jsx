import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { ChevronDown, ChevronRight, Edit2, Plus, Trash2, AlertTriangle, Check, ArrowRight } from 'lucide-react'
import apiClient from '../../lib/axios'

export default function SyllabusReviewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [expanded, setExpanded] = useState({})
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['extraction', id],
    queryFn: () => apiClient.get(`/api/v1/documents/${id}/extraction`).then((r) => r.data.data),
  })

  const saveMutation = useMutation({
    mutationFn: (units) => apiClient.put(`/api/v1/documents/${id}/extraction`, { units, verification_status: 'verified' }),
  })

  const [units, setUnits] = useState(null)

  // Initialise local units from server on first load
  if (data && !units) setUnits(JSON.parse(JSON.stringify(data.units || [])))

  const toggleUnit = (uid) => setExpanded((e) => ({ ...e, [uid]: !e[uid] }))

  const updateUnitName = (uid, val) => setUnits((u) => u.map((un) => un.id === uid ? { ...un, name: val } : un))
  const updateTopicName = (uid, tid, val) => setUnits((u) => u.map((un) => un.id === uid ? {
    ...un, topics: un.topics.map((t) => t.id === tid ? { ...t, name: val } : t)
  } : un))
  const removeTopic = (uid, tid) => setUnits((u) => u.map((un) => un.id === uid ? {
    ...un, topics: un.topics.filter((t) => t.id !== tid)
  } : un))
  const addTopic = (uid) => setUnits((u) => u.map((un) => un.id === uid ? {
    ...un, topics: [...un.topics, { id: `${uid}_t${Date.now()}`, name: 'New Topic', description: '', duration_hours: 1, objectives: [] }]
  } : un))

  const handleGenerateRoadmap = async () => {
    setGenerating(true); setError('')
    try {
      await saveMutation.mutateAsync(units)
      const { data: rmData } = await apiClient.post('/api/v1/roadmaps/academic', {
        document_id: id,
        title: data?.file_name ? `${data.file_name} Roadmap` : 'Academic Roadmap',
      })
      navigate(`/roadmaps/${rmData.data.roadmap._id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate roadmap.')
      setGenerating(false)
    }
  }

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Review Extracted Syllabus</h2>
        <p className="text-sm text-gray-500 mt-1">Review and correct the AI-extracted content before generating your roadmap</p>
      </div>

      {/* Warnings */}
      {data?.ai_warnings?.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-center gap-2 text-amber-700 font-medium mb-2">
            <AlertTriangle size={16} /> AI Extraction Warnings
          </div>
          <ul className="list-disc ml-5 text-sm text-amber-700 space-y-1">
            {data.ai_warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      {/* Units tree */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        {(units || []).length === 0 ? (
          <div className="p-10 text-center text-gray-500">No units extracted. Try re-uploading your document.</div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {(units || []).map((unit, ui) => (
              <li key={unit.id}>
                <div className="flex items-center gap-3 px-5 py-3.5 bg-gray-50">
                  <button onClick={() => toggleUnit(unit.id)} className="text-gray-500 flex-shrink-0">
                    {expanded[unit.id] ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                  </button>
                  <input
                    value={unit.name}
                    onChange={(e) => updateUnitName(unit.id, e.target.value)}
                    className="flex-1 bg-transparent font-semibold text-gray-900 text-sm border-b border-transparent focus:border-indigo-400 focus:outline-none py-0.5"
                  />
                  <span className="text-xs text-gray-400">{unit.topics?.length || 0} topics</span>
                </div>

                {expanded[unit.id] && (
                  <ul className="divide-y divide-gray-50">
                    {(unit.topics || []).map((topic) => (
                      <li key={topic.id} className="flex items-center gap-3 pl-12 pr-5 py-2.5 group">
                        <div className="w-2 h-2 rounded-full bg-indigo-300 flex-shrink-0" />
                        <input
                          value={topic.name}
                          onChange={(e) => updateTopicName(unit.id, topic.id, e.target.value)}
                          className="flex-1 text-sm text-gray-700 bg-transparent border-b border-transparent focus:border-indigo-400 focus:outline-none py-0.5"
                        />
                        <span className="text-xs text-gray-400">{topic.duration_hours}h</span>
                        <button onClick={() => removeTopic(unit.id, topic.id)}
                          className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all">
                          <Trash2 size={14} />
                        </button>
                      </li>
                    ))}
                    <li className="pl-12 pr-5 py-2">
                      <button onClick={() => addTopic(unit.id)}
                        className="flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
                        <Plus size={14} /> Add topic
                      </button>
                    </li>
                  </ul>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer actions */}
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">
          <strong className="text-gray-700">{(units || []).reduce((a, u) => a + (u.topics?.length || 0), 0)}</strong> topics across{' '}
          <strong className="text-gray-700">{(units || []).length}</strong> units
        </p>
        <div className="flex gap-3">
          <button onClick={() => saveMutation.mutate(units)} disabled={saveMutation.isPending}
            className="px-4 py-2.5 border border-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 disabled:opacity-60">
            Save Changes
          </button>
          <button onClick={handleGenerateRoadmap} disabled={generating}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-60 transition-colors">
            {generating ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <ArrowRight size={16} />}
            {generating ? 'Generating…' : 'Confirm & Generate Roadmap'}
          </button>
        </div>
      </div>
    </div>
  )
}
