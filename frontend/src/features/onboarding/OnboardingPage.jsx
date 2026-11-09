import { useMutation } from '@tanstack/react-query';
import { ArrowLeft, ArrowRight, BookOpen, CheckCircle, Clock, GraduationCap, Target } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Select from '../../components/ui/Select';
import { useAuthStore } from '../../store/authStore';
import apiClient from '../../lib/axios';

const STEPS = [
  { id: 1, label: 'Academic Background', icon: GraduationCap },
  { id: 2, label: 'Learning Preferences', icon: Clock },
  { id: 3, label: 'Your Goals', icon: Target },
];

const LEVEL_OPTIONS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
];

const TIME_OPTIONS = [
  { value: 'morning', label: 'Morning (6am–12pm)' },
  { value: 'afternoon', label: 'Afternoon (12pm–6pm)' },
  { value: 'evening', label: 'Evening (6pm–10pm)' },
  { value: 'night', label: 'Night (10pm+)' },
];

const SEMESTER_OPTIONS = Array.from({ length: 8 }, (_, i) => ({
  value: String(i + 1),
  label: `Semester ${i + 1}`,
}));

const GOAL_OPTIONS = [
  { id: 'exam', label: 'Pass upcoming exams', icon: '📝' },
  { id: 'mastery', label: 'Master the subject deeply', icon: '🎓' },
  { id: 'career', label: 'Advance my career', icon: '💼' },
  { id: 'project', label: 'Complete a project', icon: '🚀' },
  { id: 'certification', label: 'Get a certification', icon: '🏆' },
];

export default function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    institution: '',
    semester: '',
    year: new Date().getFullYear(),
    daily_study_hours: 2,
    preferred_times: [],
    learning_level: 'intermediate',
    goals: [],
  });
  const { setUser, user } = useAuthStore();
  const navigate = useNavigate();

  const { mutate: savePreferences, isPending } = useMutation({
    mutationFn: async (data) => {
      const { data: res } = await apiClient.put('/api/v1/users/preferences', data);
      return res;
    },
    onSuccess: (data) => {
      setUser({ ...user, ...data });
      navigate('/dashboard');
    },
  });

  const update = (field, value) => setFormData((prev) => ({ ...prev, [field]: value }));

  const toggleItem = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter((v) => v !== value)
        : [...prev[field], value],
    }));
  };

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
    else savePreferences(formData);
  };

  const handleBack = () => setStep(step - 1);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-indigo-600 mb-3 shadow-lg shadow-indigo-200">
            <GraduationCap size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Set Up Your Profile</h1>
          <p className="text-gray-500 text-sm mt-1">Help us personalize your learning experience</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {STEPS.map(({ id, label, icon: Icon }) => (
            <div key={id} className="flex items-center">
              <div className="flex flex-col items-center gap-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                    id < step
                      ? 'bg-indigo-600 text-white'
                      : id === step
                      ? 'bg-indigo-600 text-white ring-4 ring-indigo-100'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {id < step ? <CheckCircle size={18} /> : <Icon size={18} />}
                </div>
                <span className={`text-xs font-medium hidden sm:block ${id === step ? 'text-indigo-600' : 'text-gray-400'}`}>
                  {label}
                </span>
              </div>
              {id < STEPS.length && (
                <div className={`w-16 h-px mx-2 mt-[-20px] sm:mt-[-30px] ${id < step ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          {/* Step 1 */}
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Academic Background</h2>
              <Input
                label="Institution / University"
                placeholder="e.g., MIT, Stanford University"
                value={formData.institution}
                onChange={(e) => update('institution', e.target.value)}
              />
              <div className="grid grid-cols-2 gap-4">
                <Select
                  label="Current Semester"
                  options={SEMESTER_OPTIONS}
                  placeholder="Select semester"
                  value={formData.semester}
                  onChange={(e) => update('semester', e.target.value)}
                />
                <Input
                  label="Academic Year"
                  type="number"
                  min={2020}
                  max={2030}
                  value={formData.year}
                  onChange={(e) => update('year', Number(e.target.value))}
                />
              </div>
            </div>
          )}

          {/* Step 2 */}
          {step === 2 && (
            <div className="space-y-5">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Learning Preferences</h2>

              <div>
                <label className="text-sm font-medium text-gray-700">
                  Daily Study Hours: <span className="text-indigo-600 font-bold">{formData.daily_study_hours}h</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={12}
                  value={formData.daily_study_hours}
                  onChange={(e) => update('daily_study_hours', Number(e.target.value))}
                  className="w-full mt-2 accent-indigo-600"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>1h</span><span>12h</span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">Preferred Study Times</label>
                <div className="grid grid-cols-2 gap-2">
                  {TIME_OPTIONS.map(({ value, label }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => toggleItem('preferred_times', value)}
                      className={`p-3 rounded-lg border text-sm font-medium transition-colors text-left ${
                        formData.preferred_times.includes(value)
                          ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                          : 'border-gray-200 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              <Select
                label="Learning Level"
                options={LEVEL_OPTIONS}
                value={formData.learning_level}
                onChange={(e) => update('learning_level', e.target.value)}
              />
            </div>
          )}

          {/* Step 3 */}
          {step === 3 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">What Do You Want to Achieve?</h2>
              <p className="text-sm text-gray-500">Select all that apply</p>
              <div className="space-y-2">
                {GOAL_OPTIONS.map(({ id, label, icon }) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => toggleItem('goals', id)}
                    className={`w-full flex items-center gap-3 p-4 rounded-xl border transition-colors text-left ${
                      formData.goals.includes(id)
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <span className="text-2xl">{icon}</span>
                    <span className={`font-medium text-sm ${formData.goals.includes(id) ? 'text-indigo-700' : 'text-gray-700'}`}>
                      {label}
                    </span>
                    {formData.goals.includes(id) && (
                      <CheckCircle size={18} className="ml-auto text-indigo-600" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-100">
            <Button
              variant="ghost"
              onClick={handleBack}
              disabled={step === 1}
              icon={<ArrowLeft size={16} />}
            >
              Back
            </Button>
            <Button
              onClick={handleNext}
              loading={isPending}
              icon={step < 3 ? <ArrowRight size={16} /> : <CheckCircle size={16} />}
            >
              {step < 3 ? 'Next' : 'Complete Setup'}
            </Button>
          </div>
        </div>

        {step === 3 && (
          <p className="text-center text-sm text-gray-500 mt-4">
            You can always update these preferences in Settings.
          </p>
        )}
      </div>
    </div>
  );
}
