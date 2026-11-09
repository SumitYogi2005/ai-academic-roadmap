import { Link } from 'react-router-dom'
import { GraduationCap, Map, Calendar, Bot, ArrowRight, CheckCircle, Upload, Zap } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="border-b border-gray-100 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <GraduationCap size={18} className="text-white" />
            </div>
            <span className="font-bold text-gray-900 text-xl">AI Academic Roadmap</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
              Sign in
            </Link>
            <Link to="/register" className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="px-6 py-20 text-center bg-gradient-to-b from-indigo-50 to-white">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium mb-6">
            <Zap size={14} />
            AI-Powered Learning
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-6 leading-tight">
            Transform Your Syllabus into a{' '}
            <span className="text-indigo-600">Smart Learning Journey</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Upload your academic syllabus, and our AI creates an interactive roadmap with a personalized
            study schedule tailored to your deadlines and availability.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200"
            >
              Start for Free <ArrowRight size={18} />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 px-8 py-4 border border-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 py-20 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">How It Works</h2>
        <p className="text-center text-gray-600 mb-14">Three simple steps to your personalised learning plan</p>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step: '01', icon: Upload, title: 'Upload Your Syllabus', desc: 'Upload a PDF, DOCX, or image of your academic syllabus. Our AI extracts units, topics, and learning objectives automatically.' },
            { step: '02', icon: Map, title: 'Review & Generate Roadmap', desc: 'Review the extracted content, make corrections, and generate an interactive prerequisite-based learning roadmap.' },
            { step: '03', icon: Calendar, title: 'Get Your Study Plan', desc: 'Enter your exam date and daily availability. Our scheduler creates a feasible day-by-day study plan that respects your capacity.' },
          ].map(({ step, icon: Icon, title, desc }) => (
            <div key={step} className="relative p-8 bg-white border border-gray-200 rounded-2xl hover:shadow-md transition-shadow">
              <div className="text-5xl font-bold text-indigo-100 mb-4">{step}</div>
              <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4">
                <Icon size={24} className="text-indigo-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
              <p className="text-gray-600">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-14">Everything You Need to Excel</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Bot, title: 'AI Tutor', desc: 'Ask questions about any topic. Get explanations, notes, and quizzes generated on demand.' },
              { icon: Map, title: 'Interactive Roadmap', desc: 'Visualise dependencies between topics. Navigate by graph or outline view.' },
              { icon: Calendar, title: 'Smart Planner', desc: 'Algorithmic scheduling that guarantees no daily capacity violations.' },
              { icon: GraduationCap, title: 'Progress Tracking', desc: 'Mark topics complete and watch your progress analytics update in real time.' },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="p-6 bg-white rounded-xl border border-gray-200">
                <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center mb-4">
                  <Icon size={20} className="text-indigo-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-sm text-gray-600">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-20 bg-indigo-600 text-white text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Ready to Learn Smarter?</h2>
          <p className="text-indigo-200 mb-8 text-lg">Join students who transformed their study habits with AI-powered roadmaps.</p>
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 transition-colors"
          >
            Create Free Account <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 border-t border-gray-100 text-center text-sm text-gray-500">
        <p>© {new Date().getFullYear()} AI Academic Roadmap. Built as a portfolio project.</p>
      </footer>
    </div>
  )
}
