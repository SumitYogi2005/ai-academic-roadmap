import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import AppLayout from './components/layout/AppLayout'

// Public pages
import LandingPage from './features/landing/LandingPage'
import LoginPage from './features/auth/LoginPage'
import RegisterPage from './features/auth/RegisterPage'

// Protected pages
import OnboardingPage from './features/onboarding/OnboardingPage'
import DashboardPage from './features/dashboard/DashboardPage'
import RoadmapsListPage from './features/roadmaps/RoadmapsListPage'
import CreateRoadmapPage from './features/roadmaps/CreateRoadmapPage'
import RoadmapViewerPage from './features/roadmaps/RoadmapViewerPage'
import SyllabusReviewPage from './features/syllabus/SyllabusReviewPage'
import StudyPlannerPage from './features/planner/StudyPlannerPage'
import AIAssistantPage from './features/assistant/AIAssistantPage'
import AnalyticsPage from './features/analytics/AnalyticsPage'
import SettingsPage from './features/settings/SettingsPage'

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function PublicRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />

      {/* Protected routes */}
      <Route path="/onboarding" element={<ProtectedRoute><OnboardingPage /></ProtectedRoute>} />
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/roadmaps" element={<RoadmapsListPage />} />
        <Route path="/roadmaps/create" element={<CreateRoadmapPage />} />
        <Route path="/roadmaps/:id" element={<RoadmapViewerPage />} />
        <Route path="/syllabus/:id/review" element={<SyllabusReviewPage />} />
        <Route path="/study-planner" element={<StudyPlannerPage />} />
        <Route path="/assistant" element={<AIAssistantPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
