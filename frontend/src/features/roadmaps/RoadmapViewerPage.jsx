import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useCallback, useEffect } from 'react'
import {
  ReactFlow, Background, Controls, MiniMap,
  useNodesState, useEdgesState,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { List, GitBranch, ChevronRight, Clock, AlertCircle, CheckCircle, Circle, Bot, X } from 'lucide-react'
import apiClient from '../../lib/axios'

const NODE_COLORS = {
  concept: { bg: '#eff6ff', border: '#3b82f6', text: '#1d4ed8' },
  practice: { bg: '#f0fdf4', border: '#22c55e', text: '#15803d' },
  project: { bg: '#faf5ff', border: '#a855f7', text: '#7e22ce' },
  assessment: { bg: '#fff7ed', border: '#f97316', text: '#c2410c' },
}

function CustomNode({ data }) {
  const colors = NODE_COLORS[data.type] || NODE_COLORS.concept
  return (
    <div onClick={() => data.onSelect(data)}
      style={{ background: colors.bg, border: `2px solid ${colors.border}`, borderRadius: 12, padding: '10px 14px', minWidth: 160, maxWidth: 220, cursor: 'pointer' }}>
      <div style={{ fontSize: 10, color: colors.text, fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>
        {data.type}
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#111827', lineHeight: 1.3 }}>{data.label}</div>
      <div style={{ fontSize: 11, color: '#6b7280', marginTop: 4 }}>⏱ {data.duration}h</div>
    </div>
  )
}

const nodeTypes = { custom: CustomNode }

export default function RoadmapViewerPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [view, setView] = useState('graph')
  const [selected, setSelected] = useState(null)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const { data, isLoading, error } = useQuery({
    queryKey: ['roadmap', id],
    queryFn: () => apiClient.get(`/api/v1/roadmaps/${id}`).then((r) => r.data.data),
    onSuccess: (d) => {
      const flowNodes = d.nodes.map((n) => ({
        id: n._id,
        type: 'custom',
        position: { x: n.position_x || 0, y: n.position_y || 0 },
        data: {
          label: n.title,
          type: n.type,
          duration: n.duration_hours,
          description: n.description,
          difficulty: n.difficulty,
          nodeId: n._id,
          onSelect: setSelected,
        },
      }))
      const flowEdges = d.edges.map((e) => ({
        id: e._id,
        source: e.source_node_id,
        target: e.target_node_id,
        animated: e.relationship_type === 'prerequisite',
        style: { stroke: '#6366f1' },
      }))
      setNodes(flowNodes)
      setEdges(flowEdges)
    },
  })

  const { data: progressData } = useQuery({
    queryKey: ['progress', id],
    queryFn: () => apiClient.get(`/api/v1/progress/roadmap/${id}`).then((r) => r.data.data),
  })

  const progressMutation = useMutation({
    mutationFn: ({ nodeId, status }) =>
      apiClient.put(`/api/v1/progress/${nodeId}`, { status, roadmap_id: id }),
    onSuccess: () => qc.invalidateQueries(['progress', id]),
  })

  const onNodeDragStop = useCallback(async (_, node) => {
    try {
      await apiClient.put(`/api/v1/roadmaps/${id}/nodes/${node.id}`, {
        position_x: node.position.x,
        position_y: node.position.y,
      })
    } catch { /* ignore */ }
  }, [id])

  const getNodeProgress = (nodeId) => {
    return progressData?.progress?.find((p) => p.node_id === nodeId)?.status || 'not_started'
  }

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )

  if (error) return (
    <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
      <AlertCircle size={18} /> Failed to load roadmap.
    </div>
  )

  const roadmap = data?.roadmap
  const allNodes = data?.nodes || []

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-semibold mr-2 ${roadmap?.type === 'academic' ? 'bg-indigo-100 text-indigo-700' : 'bg-purple-100 text-purple-700'}`}>
            {roadmap?.type}
          </span>
          <h2 className="inline text-lg font-semibold text-gray-900">{roadmap?.title}</h2>
          {progressData && (
            <span className="ml-3 text-sm text-gray-500">
              {progressData.completed}/{progressData.total_nodes} complete
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="flex border border-gray-200 rounded-lg overflow-hidden">
            {[{ id: 'graph', icon: GitBranch }, { id: 'outline', icon: List }].map(({ id: v, icon: Icon }) => (
              <button key={v} onClick={() => setView(v)}
                className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition-colors ${view === v ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}>
                <Icon size={15} /> {v.charAt(0).toUpperCase() + v.slice(1)}
              </button>
            ))}
          </div>
          <button onClick={() => navigate('/study-planner')}
            className="px-3 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700">
            Plan Study
          </button>
        </div>
      </div>

      {/* Main view */}
      <div className="flex gap-4 flex-1 min-h-0">
        <div className="flex-1 min-h-[500px]">
          {view === 'graph' ? (
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden" style={{ height: 580 }}>
              <ReactFlow
                nodes={nodes} edges={edges}
                onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                onNodeDragStop={onNodeDragStop}
                fitView
              >
                <Background gap={20} color="#f1f5f9" />
                <Controls />
                <MiniMap nodeColor={(n) => NODE_COLORS[n.data?.type]?.border || '#6366f1'} />
              </ReactFlow>
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-xl overflow-y-auto" style={{ maxHeight: 580 }}>
              {allNodes.length === 0 ? (
                <p className="p-8 text-center text-gray-500">No nodes in this roadmap.</p>
              ) : (
                <ul className="divide-y divide-gray-100">
                  {allNodes.map((n) => {
                    const progress = getNodeProgress(n._id)
                    const colors = NODE_COLORS[n.type] || NODE_COLORS.concept
                    return (
                      <li key={n._id}
                        onClick={() => setSelected(n)}
                        className="flex items-center gap-4 px-5 py-3.5 hover:bg-gray-50 cursor-pointer transition-colors">
                        {progress === 'completed' ? <CheckCircle size={18} className="text-green-500 flex-shrink-0" /> :
                          progress === 'in_progress' ? <Clock size={18} className="text-amber-500 flex-shrink-0" /> :
                          <Circle size={18} className="text-gray-300 flex-shrink-0" />}
                        <span style={{ color: colors.text }} className="text-xs font-semibold uppercase w-16 flex-shrink-0">{n.type}</span>
                        <span className="flex-1 text-sm font-medium text-gray-900">{n.title}</span>
                        <span className="text-xs text-gray-400">{n.duration_hours}h</span>
                        <ChevronRight size={15} className="text-gray-400" />
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selected && (
          <div className="w-80 flex-shrink-0 bg-white border border-gray-200 rounded-xl p-5 overflow-y-auto" style={{ maxHeight: 580 }}>
            <div className="flex items-start justify-between mb-4">
              <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded-full`}
                style={{ background: NODE_COLORS[selected.type]?.bg, color: NODE_COLORS[selected.type]?.text }}>
                {selected.type}
              </span>
              <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600 p-1"><X size={16} /></button>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">{selected.title || selected.label}</h3>
            <p className="text-sm text-gray-600 mb-4">{selected.description}</p>
            <div className="flex gap-4 text-sm text-gray-500 mb-4">
              <span>⏱ {selected.duration_hours || selected.duration}h</span>
              <span className="capitalize">📊 {selected.difficulty}</span>
            </div>

            <div className="mb-4">
              <label className="block text-xs font-medium text-gray-700 mb-2">Progress</label>
              <div className="grid grid-cols-3 gap-1.5">
                {['not_started', 'in_progress', 'completed'].map((s) => (
                  <button key={s} onClick={() => progressMutation.mutate({ nodeId: selected._id || selected.nodeId, status: s })}
                    className={`py-1.5 px-2 rounded-md text-xs font-medium capitalize transition-colors ${getNodeProgress(selected._id || selected.nodeId) === s ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
                    {s.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => navigate(`/assistant?node=${selected._id || selected.nodeId}&roadmap=${id}`)}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-purple-50 text-purple-700 text-sm font-medium rounded-lg hover:bg-purple-100 transition-colors">
              <Bot size={16} /> Ask AI about this
            </button>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex gap-4 flex-wrap">
        {Object.entries(NODE_COLORS).map(([type, colors]) => (
          <div key={type} className="flex items-center gap-1.5 text-xs text-gray-600">
            <div className="w-3 h-3 rounded-sm" style={{ background: colors.border }} />
            <span className="capitalize">{type}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
