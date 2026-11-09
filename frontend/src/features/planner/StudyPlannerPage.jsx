import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Calendar, ChevronLeft, ChevronRight, Plus, Check, X, Clock, AlertTriangle } from 'lucide-react'
import apiClient from '../../lib/axios'

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
const STATUS_COLORS = {
  pending: 'bg-blue-100 text-blue-700 border-blue-200',
  completed: 'bg-green-100 text-green-700 border-green-200',
  missed: 'bg-red-100 text-red-700 border-red-200',
  rescheduled: 'bg-amber-100 text-amber-700 border-amber-200',
}

function addDays(date, n) {
  const d = new Date(date); d.setDate(d.getDate() + n); return d
}
function isoDate(d) { return d.toISOString().slice(0, 10) }
function weekStart(d) {
  const copy = new Date(d); copy.setDate(copy.getDate() - copy.getDay() + 1); return copy
}

export default function StudyPlannerPage() {
  const qc = useQueryClient()
  const [weekOffset, setWeekOffset] = useState(0)
  const [showGenerate, setShowGenerate] = useState(false)
  const [genForm, setGenForm] = useState({
    roadmap_id: '', start_date: isoDate(new Date()),
    target_date: '', availability: { monday: 90, tuesday: 90, wednesday: 90, thursday: 90, friday: 90, saturday: 120, sunday: 0 },
  })

  const baseWeek = weekStart(addDays(new Date(), weekOffset * 7))
  const weekDays = [...Array(7)].map((_, i) => addDays(baseWeek, i))

  const { data: plans } = useQuery({
    queryKey: ['plans'],
    queryFn: () => apiClient.get('/api/v1/study-plans').then((r) => r.data.data),
  })
  const { data: roadmaps } = useQuery({
    queryKey: ['roadmaps'],
    queryFn: () => apiClient.get('/api/v1/roadmaps').then((r) => r.data.data),
  })

  const activePlan = plans?.[0]
  const { data: planDetail } = useQuery({
    queryKey: ['plan', activePlan?._id],
    queryFn: () => apiClient.get(`/api/v1/study-plans/${activePlan._id}`).then((r) => r.data.data),
    enabled: !!activePlan,
  })

  const sessions = planDetail?.sessions || []
  const sessionsByDate = sessions.reduce((acc, s) => {
    const d = s.session_date?.slice(0, 10)
    if (d) { if (!acc[d]) acc[d] = []; acc[d].push(s) }
    return acc
  }, {})

  const updateMutation = useMutation({
    mutationFn: ({ sessionId, status }) =>
      apiClient.put(`/api/v1/study-plans/${activePlan._id}/sessions/${sessionId}`, { status }),
    onSuccess: () => qc.invalidateQueries(['plan', activePlan?._id]),
  })

  const generateMutation = useMutation({
    mutationFn: (body) => apiClient.post('/api/v1/study-plans/generate', body),
    onSuccess: () => { qc.invalidateQueries(['plans']); setShowGenerate(false) },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Study Planner</h2>
          <p className="text-sm text-gray-500 mt-0.5">{sessions.length} sessions scheduled</p>
        </div>
        <button onClick={() => setShowGenerate(true)}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700">
          <Plus size={16} /> Generate Plan
        </button>
      </div>

      {/* Week navigation */}
      <div className="flex items-center gap-4">
        <button onClick={() => setWeekOffset((w) => w - 1)} className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50">
          <ChevronLeft size={18} />
        </button>
        <span className="font-medium text-gray-900 flex-1 text-center">
          Week of {baseWeek.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
        </span>
        <button onClick={() => setWeekOffset((w) => w + 1)} className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50">
          <ChevronRight size={18} />
        </button>
      </div>

      {/* Calendar grid */}
      {!activePlan ? (
        <div className="bg-white border border-dashed border-gray-300 rounded-xl p-16 text-center">
          <Calendar size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 mb-4">No study plan yet. Create a roadmap first, then generate a plan.</p>
          <button onClick={() => setShowGenerate(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700">
            <Plus size={16} /> Generate Plan
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-7 gap-2">
          {weekDays.map((day, i) => {
            const dateStr = isoDate(day)
            const daySessions = sessionsByDate[dateStr] || []
            const isToday = dateStr === isoDate(new Date())
            return (
              <div key={i} className={`bg-white border rounded-xl p-3 min-h-[160px] ${isToday ? 'border-indigo-400 ring-1 ring-indigo-300' : 'border-gray-200'}`}>
                <p className={`text-xs font-semibold uppercase mb-1 ${isToday ? 'text-indigo-600' : 'text-gray-400'}`}>
                  {day.toLocaleDateString('en-US', { weekday: 'short' })}
                </p>
                <p className={`text-lg font-bold mb-2 ${isToday ? 'text-indigo-600' : 'text-gray-900'}`}>
                  {day.getDate()}
                </p>
                <div className="space-y-1.5">
                  {daySessions.map((s) => (
                    <div key={s._id}
                      className={`text-xs rounded-lg px-2 py-1.5 border ${STATUS_COLORS[s.status] || STATUS_COLORS.pending}`}>
                      <p className="font-medium line-clamp-2">{s.title || `${s.duration_minutes}m`}</p>
                      <div className="flex justify-between items-center mt-1">
                        <span>{s.duration_minutes}m</span>
                        {s.status === 'pending' && (
                          <div className="flex gap-1">
                            <button onClick={() => updateMutation.mutate({ sessionId: s._id, status: 'completed' })}
                              className="text-green-600 hover:text-green-800"><Check size={12} /></button>
                            <button onClick={() => updateMutation.mutate({ sessionId: s._id, status: 'missed' })}
                              className="text-red-500 hover:text-red-700"><X size={12} /></button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Generate modal */}
      {showGenerate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 px-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-semibold text-gray-900 text-lg">Generate Study Plan</h3>
              <button onClick={() => setShowGenerate(false)} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Roadmap</label>
                <select value={genForm.roadmap_id} onChange={(e) => setGenForm((f) => ({ ...f, roadmap_id: e.target.value }))}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">Select a roadmap…</option>
                  {(roadmaps || []).map((r) => <option key={r._id} value={r._id}>{r.title}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Start Date</label>
                  <input type="date" value={genForm.start_date} onChange={(e) => setGenForm((f) => ({ ...f, start_date: e.target.value }))}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Target / Exam Date</label>
                  <input type="date" value={genForm.target_date} onChange={(e) => setGenForm((f) => ({ ...f, target_date: e.target.value }))}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Daily Availability (minutes)</label>
                <div className="grid grid-cols-7 gap-1">
                  {DAYS.map((day) => (
                    <div key={day} className="text-center">
                      <p className="text-xs text-gray-500 mb-1 capitalize">{day.slice(0, 2)}</p>
                      <input type="number" min="0" max="600" step="15"
                        value={genForm.availability[day]}
                        onChange={(e) => setGenForm((f) => ({ ...f, availability: { ...f.availability, [day]: Number(e.target.value) } }))}
                        className="w-full text-center text-xs border border-gray-300 rounded-md py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowGenerate(false)} className="px-4 py-2.5 text-sm font-medium text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50">
                Cancel
              </button>
              <button
                onClick={() => generateMutation.mutate({
                  roadmap_id: genForm.roadmap_id,
                  start_date: genForm.start_date,
                  target_date: genForm.target_date,
                  availability: genForm.availability,
                })}
                disabled={generateMutation.isPending || !genForm.roadmap_id || !genForm.target_date}
                className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-60 flex items-center gap-2">
                {generateMutation.isPending && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                Generate Plan
              </button>
            </div>
            {generateMutation.isError && (
              <p className="text-sm text-red-600 mt-3 flex items-center gap-1.5">
                <AlertTriangle size={14} /> {generateMutation.error?.response?.data?.detail || 'Generation failed.'}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
