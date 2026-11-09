import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, User, Settings, Lock, AlertCircle, Check } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import apiClient from '../../lib/axios'

const TABS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'preferences', label: 'Preferences', icon: Settings },
  { id: 'account', label: 'Account', icon: Lock },
]
const LEVELS = ['beginner', 'intermediate', 'advanced']
const TIMES = ['early_morning', 'morning', 'afternoon', 'evening', 'night']
const TIME_LABELS = { early_morning: 'Early Morning', morning: 'Morning', afternoon: 'Afternoon', evening: 'Evening', night: 'Night' }

export default function SettingsPage() {
  const qc = useQueryClient()
  const { user, setUser } = useAuthStore()
  const [tab, setTab] = useState('profile')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  const [profile, setProfile] = useState({ full_name: user?.full_name || '' })
  const [prefs, setPrefs] = useState({
    study_hours_per_day: user?.preferences?.study_hours_per_day || 2,
    preferred_study_times: user?.preferences?.preferred_study_times || ['morning'],
    learning_level: user?.preferences?.learning_level || 'beginner',
    goal: user?.preferences?.goal || '',
  })
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' })

  const profileMutation = useMutation({
    mutationFn: (body) => apiClient.put('/api/v1/users/me', body).then((r) => r.data.data),
    onSuccess: (data) => { setUser(data); showSaved() },
    onError: (e) => setError(e.response?.data?.detail || 'Failed to update profile.'),
  })

  const prefsMutation = useMutation({
    mutationFn: (body) => apiClient.put('/api/v1/users/preferences', body).then((r) => r.data.data),
    onSuccess: (data) => { setUser(data); showSaved() },
    onError: (e) => setError(e.response?.data?.detail || 'Failed to update preferences.'),
  })

  const showSaved = () => { setSaved(true); setTimeout(() => setSaved(false), 2500) }
  const toggleTime = (t) => setPrefs((p) => ({
    ...p,
    preferred_study_times: p.preferred_study_times.includes(t)
      ? p.preferred_study_times.filter((v) => v !== t)
      : [...p.preferred_study_times, t],
  }))

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
        <p className="text-sm text-gray-500 mt-0.5">Manage your profile and preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex border border-gray-200 rounded-xl overflow-hidden bg-white">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => { setTab(id); setError('') }}
            className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${tab === id ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}>
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-5">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            <AlertCircle size={16} /> {error}
          </div>
        )}
        {saved && (
          <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            <Check size={16} /> Saved successfully!
          </div>
        )}

        {tab === 'profile' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
              <input value={profile.full_name} onChange={(e) => setProfile({ full_name: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input value={user?.email || ''} disabled
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed" />
              <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
            </div>
            <button onClick={() => profileMutation.mutate(profile)} disabled={profileMutation.isPending}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-60">
              <Save size={15} /> Save Profile
            </button>
          </>
        )}

        {tab === 'preferences' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Daily study hours: <span className="text-indigo-600 font-semibold">{prefs.study_hours_per_day}h</span>
              </label>
              <input type="range" min="0.5" max="12" step="0.5"
                value={prefs.study_hours_per_day}
                onChange={(e) => setPrefs((p) => ({ ...p, study_hours_per_day: parseFloat(e.target.value) }))}
                className="w-full accent-indigo-600" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Preferred Study Times</label>
              <div className="flex flex-wrap gap-2">
                {TIMES.map((t) => (
                  <button key={t} onClick={() => toggleTime(t)}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${prefs.preferred_study_times.includes(t) ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-600 hover:border-indigo-400'}`}>
                    {TIME_LABELS[t]}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Learning Level</label>
              <div className="flex gap-3">
                {LEVELS.map((l) => (
                  <button key={l} onClick={() => setPrefs((p) => ({ ...p, learning_level: l }))}
                    className={`flex-1 py-2.5 rounded-lg border-2 text-sm font-medium capitalize transition-colors ${prefs.learning_level === l ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600'}`}>
                    {l}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Learning Goal</label>
              <textarea value={prefs.goal} onChange={(e) => setPrefs((p) => ({ ...p, goal: e.target.value }))}
                rows={3} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                placeholder="What do you want to achieve?" />
            </div>
            <button onClick={() => prefsMutation.mutate(prefs)} disabled={prefsMutation.isPending}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-60">
              <Save size={15} /> Save Preferences
            </button>
          </>
        )}

        {tab === 'account' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">To change your password, contact support or use the forgot-password flow on the login page.</p>
            <div className="border border-red-200 rounded-xl p-5 bg-red-50">
              <h4 className="font-semibold text-red-700 mb-1">Danger Zone</h4>
              <p className="text-sm text-red-600 mb-3">Deleting your account is permanent and cannot be undone.</p>
              <button disabled className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg opacity-50 cursor-not-allowed">
                Delete Account (not yet available)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
