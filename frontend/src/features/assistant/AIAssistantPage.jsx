import { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Send, Bot, User, FileText, HelpCircle, Zap } from 'lucide-react'
import apiClient from '../../lib/axios'

function Message({ role, content }) {
  return (
    <div className={`flex gap-3 ${role === 'user' ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${role === 'user' ? 'bg-indigo-100 text-indigo-700' : 'bg-purple-100 text-purple-700'}`}>
        {role === 'user' ? <User size={16} /> : <Bot size={16} />}
      </div>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${role === 'user' ? 'bg-indigo-600 text-white rounded-tr-sm' : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm'}`}>
        {content}
      </div>
    </div>
  )
}

export default function AIAssistantPage() {
  const [searchParams] = useSearchParams()
  const nodeId = searchParams.get('node')
  const roadmapId = searchParams.get('roadmap')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your AI learning assistant. Ask me anything about your topics, or use the quick actions to generate quizzes and notes." }
  ])
  const [input, setInput] = useState('')
  const [mode, setMode] = useState('chat') // chat | quiz | notes
  const [quizData, setQuizData] = useState(null)
  const [notesData, setNotesData] = useState(null)
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const bottomRef = useRef()

  const { data: roadmaps } = useQuery({
    queryKey: ['roadmaps'],
    queryFn: () => apiClient.get('/api/v1/roadmaps').then((r) => r.data.data),
  })
  const [selectedRoadmap, setSelectedRoadmap] = useState(roadmapId || '')
  const [selectedNode, setSelectedNode] = useState(nodeId || '')

  const { data: roadmapDetail } = useQuery({
    queryKey: ['roadmap-nodes', selectedRoadmap],
    queryFn: () => apiClient.get(`/api/v1/roadmaps/${selectedRoadmap}`).then((r) => r.data.data),
    enabled: !!selectedRoadmap,
  })
  const nodes = roadmapDetail?.nodes || []

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const chatMutation = useMutation({
    mutationFn: (q) => apiClient.post('/api/v1/ai/chat', {
      question: q,
      node_id: selectedNode || undefined,
      roadmap_id: selectedRoadmap || undefined,
    }).then((r) => r.data.data),
    onSuccess: (data) => setMessages((m) => [...m, { role: 'assistant', content: data.answer }]),
    onError: () => setMessages((m) => [...m, { role: 'assistant', content: 'Sorry, the AI service is temporarily unavailable. Please try again.' }]),
  })

  const quizMutation = useMutation({
    mutationFn: () => apiClient.post('/api/v1/ai/quiz', {
      node_id: selectedNode, roadmap_id: selectedRoadmap,
    }).then((r) => r.data.data),
    onSuccess: (data) => { setQuizData(data); setMode('quiz'); setSelectedAnswers({}) },
  })

  const notesMutation = useMutation({
    mutationFn: () => apiClient.post('/api/v1/ai/notes', {
      node_id: selectedNode, roadmap_id: selectedRoadmap,
    }).then((r) => r.data.data),
    onSuccess: (data) => { setNotesData(data); setMode('notes') },
  })

  const handleSend = () => {
    if (!input.trim()) return
    setMessages((m) => [...m, { role: 'user', content: input }])
    chatMutation.mutate(input)
    setInput('')
  }

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-120px)]">
      {/* Context selector */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4 flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[180px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Roadmap</label>
          <select value={selectedRoadmap} onChange={(e) => { setSelectedRoadmap(e.target.value); setSelectedNode('') }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">No roadmap selected</option>
            {(roadmaps || []).map((r) => <option key={r._id} value={r._id}>{r.title}</option>)}
          </select>
        </div>
        {selectedRoadmap && (
          <div className="flex-1 min-w-[180px]">
            <label className="block text-xs font-medium text-gray-500 mb-1">Topic (optional)</label>
            <select value={selectedNode} onChange={(e) => setSelectedNode(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">General</option>
              {nodes.map((n) => <option key={n._id} value={n._id}>{n.title}</option>)}
            </select>
          </div>
        )}
        <div className="flex gap-2">
          <button onClick={() => { setMode('chat'); setQuizData(null); setNotesData(null) }}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg border transition-colors ${mode === 'chat' ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
            <Bot size={13} /> Chat
          </button>
          <button onClick={() => selectedNode && quizMutation.mutate()} disabled={!selectedNode || quizMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            {quizMutation.isPending ? <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" /> : <HelpCircle size={13} />}
            Quiz
          </button>
          <button onClick={() => selectedNode && notesMutation.mutate()} disabled={!selectedNode || notesMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            {notesMutation.isPending ? <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" /> : <FileText size={13} />}
            Notes
          </button>
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {mode === 'chat' && (
          <>
            {messages.map((m, i) => <Message key={i} role={m.role} content={m.content} />)}
            {chatMutation.isPending && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center"><Bot size={16} className="text-purple-700" /></div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex gap-1"><span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} /><span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} /><span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} /></div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </>
        )}

        {mode === 'quiz' && quizData && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-6">
            <h3 className="font-semibold text-gray-900 text-lg">Quiz: {quizData.topic}</h3>
            {(quizData.questions || []).map((q, qi) => (
              <div key={qi} className="space-y-2">
                <p className="font-medium text-gray-900 text-sm">{qi + 1}. {q.question}</p>
                <div className="space-y-1.5">
                  {(q.options || []).map((opt, oi) => {
                    const selected = selectedAnswers[qi] === oi
                    const revealed = selectedAnswers[qi] !== undefined
                    const isCorrect = oi === q.correct_answer
                    return (
                      <button key={oi} onClick={() => !revealed && setSelectedAnswers((a) => ({ ...a, [qi]: oi }))}
                        className={`w-full text-left px-4 py-2.5 rounded-lg border text-sm transition-colors ${revealed ? isCorrect ? 'bg-green-50 border-green-400 text-green-800' : selected ? 'bg-red-50 border-red-400 text-red-800' : 'border-gray-200 text-gray-500' : 'border-gray-200 hover:border-indigo-400 hover:bg-indigo-50'}`}>
                        {opt}
                      </button>
                    )
                  })}
                </div>
                {selectedAnswers[qi] !== undefined && (
                  <p className="text-xs text-gray-600 bg-gray-50 rounded-lg px-3 py-2 border border-gray-100">
                    <strong>Explanation:</strong> {q.explanation}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {mode === 'notes' && notesData && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-5">
            <h3 className="font-semibold text-gray-900 text-lg">{notesData.notes?.title || notesData.topic}</h3>
            {notesData.notes?.summary && (
              <div><h4 className="text-sm font-semibold text-gray-700 mb-1">Summary</h4><p className="text-sm text-gray-600">{notesData.notes.summary}</p></div>
            )}
            {notesData.notes?.key_concepts?.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Concepts</h4>
                <div className="space-y-2">
                  {notesData.notes.key_concepts.map((kc, i) => (
                    <div key={i} className="flex gap-2 text-sm"><strong className="text-indigo-700 flex-shrink-0">{kc.term}:</strong><span className="text-gray-600">{kc.definition}</span></div>
                  ))}
                </div>
              </div>
            )}
            {notesData.notes?.main_points?.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Main Points</h4>
                <ul className="list-disc ml-5 space-y-1 text-sm text-gray-600">
                  {notesData.notes.main_points.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Chat input */}
      {mode === 'chat' && (
        <div className="flex gap-3 items-end bg-white border border-gray-200 rounded-xl p-3">
          <textarea
            value={input} onChange={(e) => setInput(e.target.value)} rows={1}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
            placeholder="Ask a question about your topic…"
            className="flex-1 resize-none text-sm text-gray-800 focus:outline-none bg-transparent py-1 max-h-32"
          />
          <button onClick={handleSend} disabled={!input.trim() || chatMutation.isPending}
            className="p-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-60 flex-shrink-0 transition-colors">
            <Send size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
