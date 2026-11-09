import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, GraduationCap, Zap, FileText, Image, X, AlertCircle, ChevronRight } from 'lucide-react'
import apiClient from '../../lib/axios'

const MODES = [
  {
    id: 'academic',
    icon: GraduationCap,
    title: 'Academic Mode',
    desc: 'Upload your institutional syllabus (PDF, DOCX, or image). AI extracts units and topics for you to review.',
    color: 'indigo',
  },
  {
    id: 'skill',
    icon: Zap,
    title: 'Skill Mode',
    desc: 'Enter a skill name and your learning goal. AI generates a custom progression roadmap from beginner to advanced.',
    color: 'purple',
  },
]

export default function CreateRoadmapPage() {
  const navigate = useNavigate()
  const fileRef = useRef()
  const [mode, setMode] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Academic form
  const [file, setFile] = useState(null)
  const [subjectId, setSubjectId] = useState('')
  const [acTitle, setAcTitle] = useState('')

  // Skill form
  const [skill, setSkill] = useState({ name: '', level: 'beginner', goal: '', weeks: 8, title: '' })

  const handleFileDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer?.files?.[0] || e.target.files?.[0]
    if (f) setFile(f)
  }

  const submitAcademic = async () => {
    if (!file) { setError('Please select a file.'); return }
    setLoading(true); setError('')
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('subject_id', subjectId || 'subject')
      const { data: upData } = await apiClient.post('/api/v1/documents/upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const docId = upData.data.id
      // Poll for completion
      let status = 'pending'
      for (let i = 0; i < 30; i++) {
        await new Promise((r) => setTimeout(r, 2000))
        const { data: st } = await apiClient.get(`/api/v1/documents/${docId}/status`)
        status = st.data.status
        if (status === 'completed' || status === 'failed') break
      }
      if (status === 'failed') { setError('Document processing failed. Try a different file.'); setLoading(false); return }
      navigate(`/syllabus/${docId}/review`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.')
      setLoading(false)
    }
  }

  const submitSkill = async () => {
    if (!skill.name) { setError('Please enter a skill name.'); return }
    setLoading(true); setError('')
    try {
      const { data } = await apiClient.post('/api/v1/roadmaps/skill', {
        skill_name: skill.name,
        skill_level: skill.level,
        goal: skill.goal,
        timeframe_weeks: Number(skill.weeks),
        title: skill.title || `${skill.name} Roadmap`,
      })
      navigate(`/roadmaps/${data.data.roadmap._id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate roadmap.')
      setLoading(false)
    }
  }

  if (!mode) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Create a New Roadmap</h2>
          <p className="text-gray-500 text-sm mt-1">Choose how you want to create your learning roadmap</p>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {MODES.map(({ id, icon: Icon, title, desc, color }) => (
            <button key={id} onClick={() => setMode(id)}
              className={`p-6 bg-white border-2 rounded-2xl text-left hover:shadow-md transition-all group ${color === 'indigo' ? 'hover:border-indigo-500' : 'hover:border-purple-500'} border-gray-200`}>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${color === 'indigo' ? 'bg-indigo-50' : 'bg-purple-50'}`}>
                <Icon size={24} className={color === 'indigo' ? 'text-indigo-600' : 'text-purple-600'} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
              <p className="text-sm text-gray-600">{desc}</p>
              <div className={`flex items-center gap-1 mt-4 text-sm font-medium ${color === 'indigo' ? 'text-indigo-600' : 'text-purple-600'}`}>
                Get started <ChevronRight size={16} />
              </div>
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => { setMode(null); setError('') }}
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100">
          <X size={18} />
        </button>
        <h2 className="text-xl font-semibold text-gray-900">
          {mode === 'academic' ? 'Academic Mode' : 'Skill Mode'}
        </h2>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-5">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            <AlertCircle size={16} /> {error}
          </div>
        )}

        {mode === 'academic' ? (
          <>
            {/* File drop zone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Syllabus File</label>
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleFileDrop}
                onClick={() => fileRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${file ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'}`}>
                <input ref={fileRef} type="file" className="hidden"
                  accept=".pdf,.docx,.png,.jpg,.jpeg"
                  onChange={handleFileDrop} />
                {file ? (
                  <div className="flex items-center justify-center gap-3 text-green-700">
                    <FileText size={24} />
                    <div className="text-left">
                      <p className="font-medium">{file.name}</p>
                      <p className="text-xs text-green-600">{(file.size / 1024).toFixed(0)} KB</p>
                    </div>
                    <button onClick={(e) => { e.stopPropagation(); setFile(null) }}
                      className="ml-2 text-green-600 hover:text-red-500"><X size={16} /></button>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-center gap-3 mb-3 text-gray-400">
                      <FileText size={28} /><Image size={28} />
                    </div>
                    <p className="text-sm text-gray-600 font-medium">Drop your syllabus here or click to browse</p>
                    <p className="text-xs text-gray-400 mt-1">PDF, DOCX, PNG, JPG up to 10 MB</p>
                  </>
                )}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Subject / Course Name</label>
              <input value={subjectId} onChange={(e) => setSubjectId(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g. DBMS, Operating Systems, Data Structures…" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Roadmap Title (optional)</label>
              <input value={acTitle} onChange={(e) => setAcTitle(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g. DBMS Exam Prep Roadmap" />
            </div>
            <button onClick={submitAcademic} disabled={loading || !file}
              className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-60 transition-colors flex items-center justify-center gap-2">
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Processing…</>
              ) : (
                <><Upload size={18} /> Upload &amp; Analyse Syllabus</>
              )}
            </button>
            {loading && <p className="text-xs text-gray-500 text-center">AI is extracting your syllabus… this may take 15–30 seconds.</p>}
          </>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Skill Name *</label>
              <input value={skill.name} onChange={(e) => setSkill((s) => ({ ...s, name: e.target.value }))}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g. Python, Machine Learning, Web Development…" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Current Level</label>
              <select value={skill.level} onChange={(e) => setSkill((s) => ({ ...s, level: e.target.value }))}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Learning Goal</label>
              <input value={skill.goal} onChange={(e) => setSkill((s) => ({ ...s, goal: e.target.value }))}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g. Build a full-stack web app, ace a job interview…" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Timeframe: <span className="text-indigo-600 font-semibold">{skill.weeks} weeks</span>
              </label>
              <input type="range" min="2" max="52" value={skill.weeks}
                onChange={(e) => setSkill((s) => ({ ...s, weeks: e.target.value }))}
                className="w-full accent-indigo-600" />
              <div className="flex justify-between text-xs text-gray-400 mt-1"><span>2 weeks</span><span>1 year</span></div>
            </div>
            <button onClick={submitSkill} disabled={loading || !skill.name}
              className="w-full py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:opacity-60 transition-colors flex items-center justify-center gap-2">
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Generating…</>
              ) : (
                <><Zap size={18} /> Generate Skill Roadmap</>
              )}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
