import { useState } from 'react'
import {
  BrainCircuit,
  FileText,
  ShieldCheck,
  Clock,
  BarChart3,
  Bell,
  ArrowRight,
  CheckCircle2,
  Users,
  Landmark,
  Sparkles,
} from 'lucide-react'
import AuthScreen from './AuthScreen'
import type { Role } from './types'

type Screen = 'home' | 'auth'

export default function App() {
  const [screen, setScreen] = useState<Screen>('home')
  const [authRole, setAuthRole] = useState<Role>('citizen')

  function goToAuth(role: Role) {
    setAuthRole(role)
    setScreen('auth')
  }

  if (screen === 'auth') {
    return <AuthScreen initialRole={authRole} onBack={() => setScreen('home')} />
  }

  return (
    <div className="min-h-screen bg-[#F8F9FB] font-['Inter',sans-serif]">
      {/* ── Navbar ── */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <BrainCircuit size={18} className="text-white" />
            </div>
            <span className="font-bold text-gray-900 text-lg tracking-tight">
              CivicSahayak
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => goToAuth('citizen')}
              className="text-sm font-medium text-gray-600 hover:text-indigo-600 transition-colors px-3 py-1.5"
            >
              Submit Grievance
            </button>
            <button
              onClick={() => goToAuth('officer')}
              className="text-sm font-medium bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Officer Login
            </button>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative overflow-hidden">
        <div className="absolute -top-32 -right-32 w-[500px] h-[500px] bg-indigo-100 rounded-full blur-3xl opacity-50 pointer-events-none" />
        <div className="absolute -bottom-20 -left-20 w-[400px] h-[400px] bg-violet-100 rounded-full blur-3xl opacity-40 pointer-events-none" />

        <div className="relative max-w-6xl mx-auto px-6 pt-20 pb-24 text-center">
          <div className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-6">
            <Sparkles size={13} />
            AI-Powered Grievance Redressal System
          </div>

          <h1 className="text-5xl font-extrabold text-gray-900 leading-tight max-w-3xl mx-auto mb-6">
            Your grievances,{' '}
            <span className="text-indigo-600">resolved faster</span> with AI
          </h1>

          <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
            CivicSahayak automatically classifies, prioritizes, and routes your
            complaint to the right department — cutting resolution time by up to
            60%.
          </p>

          {/* ── CTA Cards ── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 max-w-2xl mx-auto">
            {/* Citizen card */}
            <button
              onClick={() => goToAuth('citizen')}
              className="group relative bg-white border-2 border-indigo-100 hover:border-indigo-500 rounded-2xl p-7 text-left transition-all duration-200 hover:shadow-xl hover:-translate-y-0.5"
            >
              <div className="w-12 h-12 rounded-xl bg-indigo-50 group-hover:bg-indigo-600 flex items-center justify-center mb-4 transition-colors">
                <Users size={24} className="text-indigo-600 group-hover:text-white transition-colors" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-1.5">
                I'm a Citizen
              </h2>
              <p className="text-sm text-gray-500 mb-5 leading-relaxed">
                Submit a new grievance or track an existing one. Get real-time
                status updates via SMS or email.
              </p>
              <div className="flex items-center gap-1.5 text-indigo-600 font-semibold text-sm">
                Go to Citizen Portal
                <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </div>
            </button>

            {/* Officer card */}
            <button
              onClick={() => goToAuth('officer')}
              className="group relative bg-white border-2 border-gray-100 hover:border-indigo-500 rounded-2xl p-7 text-left transition-all duration-200 hover:shadow-xl hover:-translate-y-0.5"
            >
              <div className="w-12 h-12 rounded-xl bg-gray-50 group-hover:bg-indigo-600 flex items-center justify-center mb-4 transition-colors">
                <Landmark size={24} className="text-gray-600 group-hover:text-white transition-colors" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-1.5">
                I'm an Officer
              </h2>
              <p className="text-sm text-gray-500 mb-5 leading-relaxed">
                Manage your queue, view AI insights, respond to grievances, and
                track SLA compliance in one dashboard.
              </p>
              <div className="flex items-center gap-1.5 text-indigo-600 font-semibold text-sm">
                Go to Officer Dashboard
                <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          </div>
        </div>
      </section>

      {/* ── Stats strip ── */}
      <section className="bg-indigo-600">
        <div className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
          {[
            { value: '60%', label: 'Faster Resolution' },
            { value: '24/7', label: 'AI Availability' },
            { value: '99%', label: 'Routing Accuracy' },
            { value: '<2 min', label: 'Avg. Intake Time' },
          ].map(({ value, label }) => (
            <div key={label}>
              <div className="text-3xl font-extrabold text-white">{value}</div>
              <div className="text-indigo-200 text-sm mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">
            How CivicSahayak works
          </h2>
          <p className="text-gray-500 max-w-xl mx-auto">
            From submission to resolution — every step is automated,
            transparent, and trackable.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {[
            {
              icon: <FileText size={22} className="text-indigo-600" />,
              step: '01',
              title: 'Submit',
              desc: 'Citizen submits a grievance in natural language — text, voice, or file attachment.',
            },
            {
              icon: <BrainCircuit size={22} className="text-indigo-600" />,
              step: '02',
              title: 'AI Triage',
              desc: 'Our LLM classifies the category, detects urgency, and routes it to the correct department instantly.',
            },
            {
              icon: <CheckCircle2 size={22} className="text-indigo-600" />,
              step: '03',
              title: 'Resolve & Close',
              desc: 'Officer reviews, acts, and closes. Citizen gets notified. SLA is enforced throughout.',
            },
          ].map(({ icon, step, title, desc }) => (
            <div
              key={step}
              className="bg-white rounded-2xl p-7 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-11 h-11 rounded-xl bg-indigo-50 flex items-center justify-center">
                  {icon}
                </div>
                <span className="text-4xl font-black text-gray-100">{step}</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features grid ── */}
      <section className="bg-white border-y border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">
              Built for both sides of the counter
            </h2>
            <p className="text-gray-500">
              Features designed for citizens and officers alike.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              {
                icon: <BrainCircuit size={20} className="text-indigo-600" />,
                title: 'AI Classification',
                desc: 'Automatically categorizes complaints into departments with 99% accuracy.',
              },
              {
                icon: <Clock size={20} className="text-indigo-600" />,
                title: 'SLA Enforcement',
                desc: 'Every grievance has a deadline. Officers are alerted before breaches.',
              },
              {
                icon: <Bell size={20} className="text-indigo-600" />,
                title: 'Real-time Notifications',
                desc: 'Citizens get SMS/email updates at every status change.',
              },
              {
                icon: <BarChart3 size={20} className="text-indigo-600" />,
                title: 'Analytics Dashboard',
                desc: 'Officers see trends, bottlenecks, and resolution rates at a glance.',
              },
              {
                icon: <ShieldCheck size={20} className="text-indigo-600" />,
                title: 'Secure & Auditable',
                desc: 'All actions are logged. Full audit trail for compliance.',
              },
              {
                icon: <FileText size={20} className="text-indigo-600" />,
                title: 'Multi-format Input',
                desc: 'Accept grievances via text, PDF uploads, or structured forms.',
              },
            ].map(({ icon, title, desc }) => (
              <div
                key={title}
                className="flex gap-4 p-5 rounded-xl border border-gray-100 hover:border-indigo-100 hover:bg-indigo-50/30 transition-all"
              >
                <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0 mt-0.5">
                  {icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="max-w-6xl mx-auto px-6 py-20 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to get started?
        </h2>
        <p className="text-gray-500 mb-8 max-w-lg mx-auto">
          Lodge your grievance in under 2 minutes, or log in as an officer to
          manage your queue.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => goToAuth('citizen')}
            className="inline-flex items-center justify-center gap-2 bg-indigo-600 text-white font-semibold px-7 py-3.5 rounded-xl hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200"
          >
            <Users size={18} />
            Submit a Grievance
          </button>
          <button
            onClick={() => goToAuth('officer')}
            className="inline-flex items-center justify-center gap-2 bg-white text-gray-900 font-semibold px-7 py-3.5 rounded-xl border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
          >
            <Landmark size={18} />
            Officer Login
          </button>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center">
              <BrainCircuit size={13} className="text-white" />
            </div>
            <span className="font-semibold text-gray-700">CivicSahayak</span>
            <span>·</span>
            <span>Smart India Hackathon 2026</span>
          </div>
          <span>Built with ❤️ for faster public service delivery</span>
        </div>
      </footer>
    </div>
  )
}
