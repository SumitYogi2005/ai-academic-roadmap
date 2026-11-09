import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, ChevronRight, ChevronLeft, Check } from 'lucide-react'
import apiClient from '../../lib/axios'
import { useAuthStore } from '../../store/authStore'

const STEPS = ['Academic Background', 'Study Preferences', 'Your Goals']

const LEVELS = ['beginner', 'intermediate', 'advanced']
const TIMES = ['early_morning', 'morning', 'afternoon', 'evening', 'night']
const TIME_LABELS = { early_morning: 'Early Morning (5–8am)', morning: 'Morning (8–12pm)', afternoon: 'Afternoon (12–5pm)', evening: 'Evening (5–9pm)', night: 'Night (9pm+)' }

export default function OnboardingPage() {
  const navigate = useNavigate()
  const setUser = useAuthStore((s) => s.setUser)
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    study_hours_per_day: 2,
    preferred_study_times: ['morning'],
    learning_level: 'beginner',
    goal: '',
  })

  const toggle = (arr, val) => arr.includes(val) ? arr.filter((v) => v !== val) : [...arr, val]

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.put('/api/v1/users/preferences', {
        study_hours_per_day: Number(form.study_hours_per_day),
        preferred_study_times: form.preferred_study_times,
        learning_level: form.learning_level,
        goal: form.goal,
      })
      setUser(data.data)
      navigate('/dashboard')
    } catch {
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex items-center justify-center px-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-indigo-600 rounded-2xl mb-4">
            <GraduationCap size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Set up your profile</h1>
          <p className="text-gray-600 mt-1">Help us personalise your learning experience</p>
        </div>

        {/* Progress */}
        <div className="flex gap-2 mb-8">
          {STEPS.map((s, i) => (
            <div key={s} className={`flex-1 h-2 rounded-full transition-colors ${i <= step ? 'bg-indigo-600' : 'bg-gray-200'}`} />
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">{STEPS[step]}</h2>

          {step === 0 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">What is your current knowledge level?</label>
                <div className="grid grid-cols-3 gap-3">
                  {LEVELS.map((l) => (
                    <button key={l} onClick={() => setForm((f) => ({ ...f, learning_level: l }))}
                      className={`py-3 px-4 rounded-lg border-2 text-sm font-medium capitalize transition-colors ${form.learning_level === l ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'}`}>
                      {l}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Daily study hours: <span className="text-indigo-600 font-semibold">{form.study_hours_per_day}h</span>
                </label>
                <input type="range" min="0.5" max="12" step="0.5"
                  value={form.study_hours_per_day}
                  onChange={(e) => setForm((f) => ({ ...f, study_hours_per_day: e.target.value }))}
                  className="w-full accent-indigo-600"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1"><span>30 min</span><span>12 hours</span></div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Preferred study times (select all that apply)</label>
                <div className="space-y-2">
                  {TIMES.map((t) => (
                    <button key={t} onClick={() => setForm((f) => ({ ...f, preferred_study_times: toggle(f.preferred_study_times, t) }))}
                      className={`flex items-center w-full px-4 py-3 rounded-lg border-2 text-sm transition-colors ${form.preferred_study_times.includes(t) ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'}`}>
                      <span className="flex-1 text-left">{TIME_LABELS[t]}</span>
                      {form.preferred_study_times.includes(t) && <Check size={16} />}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">What is your primary learning goal?</label>
              <textarea
                value={form.goal}
                onChange={(e) => setForm((f) => ({ ...f, goal: e.target.value }))}
                rows={5}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                placeholder="e.g. Pass my DBMS exam with distinction, learn Python for data science, prepare for GATE..."
              />
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <button onClick={() => setStep((s) => s - 1)} disabled={step === 0}
              className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
              <ChevronLeft size={16} /> Back
            </button>
            {step < STEPS.length - 1 ? (
              <button onClick={() => setStep((s) => s + 1)}
                className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
                Next <ChevronRight size={16} />
              </button>
            ) : (
              <button onClick={handleSubmit} disabled={loading}
                className="flex items-center gap-2 px-6 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-60 transition-colors">
                {loading ? 'Saving…' : 'Get Started'} <ChevronRight size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
