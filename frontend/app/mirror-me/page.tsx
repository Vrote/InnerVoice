'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Sparkles, ArrowLeft, Loader2, RefreshCw, TrendingUp,
  Brain, Heart, Lightbulb, Star, Cloud, BarChart2, Calendar,
  Activity, FileText, AlertTriangle
} from 'lucide-react';
import api from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';

interface CognitiveDistortion {
  distortion_type: string;
  evidence: string;
}

interface ClinicalInsights {
  practitioner_summary: string;
  cognitive_distortions_detected: CognitiveDistortion[];
  key_stressors: string[];
  coping_mechanisms_observed: string[];
  mood_volatility: string;
}

interface MirrorInsight { title: string; description: string; }
interface MirrorReport {
  month_summary?: string;
  mood_trend_description?: string;
  insights?: MirrorInsight[];
  lessons_learned?: string[];
  self_care_recommendations?: string[];
  clinical_insights?: ClinicalInsights;
  supportive_closing?: string;
  avg_mood?: number;
  total_messages?: number;
  word_cloud?: { text: string; value: number }[];
  has_data?: boolean;
  message?: string;
  last_generated_at?: string;
}
interface StatusData {
  month: number;
  year: number;
  message_count: number;
  threshold: number;
  qualifies: boolean;
  has_report: boolean;
  messages_remaining: number;
  last_generated_at?: string | null;
}

const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

// ── Mood ring ─────────────────────────────────────────────────────────────────
function MoodRing({ score }: { score: number }) {
  const pct   = (score / 10) * 100;
  const color = score >= 7 ? '#34d399' : score >= 5 ? '#a78bfa' : score >= 3 ? '#fb923c' : '#f87171';
  const r = 40, c = 2 * Math.PI * r;

  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      <svg className="absolute inset-0 -rotate-90" width="96" height="96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
        <circle
          cx="48" cy="48" r={r} fill="none"
          stroke={color} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={`${(pct / 100) * c} ${c}`}
          style={{ transition: 'stroke-dasharray 1s ease-out' }}
        />
      </svg>
      <div className="text-center">
        <span className="text-xl font-bold text-white">{score.toFixed(1)}</span>
        <p className="text-[9px] text-slate-500 leading-tight">avg mood</p>
      </div>
    </div>
  );
}

// ── Word cloud ────────────────────────────────────────────────────────────────
function WordCloud({ words }: { words: { text: string; value: number }[] }) {
  const max = Math.max(...words.map(w => w.value), 1);
  return (
    <div className="flex flex-wrap gap-2 justify-center py-2">
      {words.slice(0, 18).map(w => {
        const size = 0.7 + (w.value / max) * 0.8;
        const opacity = 0.5 + (w.value / max) * 0.5;
        return (
          <span key={w.text}
            className="text-violet-300 font-medium cursor-default select-none transition-opacity hover:opacity-100"
            style={{ fontSize: `${size}rem`, opacity }}
          >
            {w.text}
          </span>
        );
      })}
    </div>
  );
}

// ── Main Mirror Me page ───────────────────────────────────────────────────────
export default function MirrorMePage() {
  const router = useRouter();
  const { token, isLoading, loadFromStorage, user } = useAuthStore();
  const [status, setStatus]   = useState<StatusData | null>(null);
  const [report, setReport]   = useState<MirrorReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError]     = useState('');

  // Selected date states
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear]   = useState<number>(new Date().getFullYear());
  const [activeTab, setActiveTab]         = useState<'reflection' | 'clinical'>('reflection');

  const getPastMonths = () => {
    const months = [];
    const now = new Date();
    for (let i = 0; i < 6; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      months.push({
        label: d.toLocaleString('default', { month: 'long', year: 'numeric' }),
        month: d.getMonth() + 1,
        year: d.getFullYear()
      });
    }
    return months;
  };

  useEffect(() => { loadFromStorage(); }, [loadFromStorage]);
  useEffect(() => {
    if (!isLoading && !token) router.replace('/auth/login');
  }, [isLoading, token, router]);

  // Set initial month/year from query params on load
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const searchParams = new URLSearchParams(window.location.search);
      const m = searchParams.get('month') ? Number(searchParams.get('month')) : new Date().getMonth() + 1;
      const y = searchParams.get('year') ? Number(searchParams.get('year')) : new Date().getFullYear();
      setSelectedMonth(m);
      setSelectedYear(y);
    }
  }, []);

  // Fetch report whenever selected date changes
  useEffect(() => {
    if (!token) return;
    loadData();
  }, [token, selectedMonth, selectedYear]);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [statusRes, reportRes] = await Promise.all([
        api.get(`/api/mirror-me/status?month=${selectedMonth}&year=${selectedYear}`),
        api.get(`/api/mirror-me/${selectedYear}/${selectedMonth}`),
      ]);
      setStatus(statusRes.data);
      const rep = reportRes.data;
      if (rep && rep.has_data !== false) {
        setReport(rep);
      } else {
        setReport(null);
      }
    } catch (e: any) {
      setError('Failed to load Mirror Me data.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError('');
    try {
      const res = await api.post('/api/mirror-me/generate', { month: selectedMonth, year: selectedYear });
      const rep = res.data ?? res.data;
      if (rep?.has_data) {
        setReport(rep);
        await loadData();
      } else {
        setError(rep?.message ?? 'Not enough messages yet.');
      }
    } catch (e: any) {
      setError('Failed to generate report. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30 animate-pulse-slow">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <p className="text-slate-500 text-sm">Loading your mirror...</p>
        </div>
      </div>
    );
  }

  const monthName  = status ? MONTHS[status.month - 1] : '';
  const progressPct = status ? Math.min(100, (status.message_count / status.threshold) * 100) : 0;

  return (
    <div className="min-h-screen bg-[#0f0f0f]">
      {/* Ambient glow */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-violet-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[300px] bg-indigo-600/4 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-white/[0.05] bg-[#0f0f0f]/80 backdrop-blur-xl">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              id="back-to-chat"
              onClick={() => router.push('/chat')}
              className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/5 transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-md shadow-violet-500/30">
                <BarChart2 className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="font-semibold text-white text-sm">Mirror Me</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={`${selectedYear}-${selectedMonth}`}
              onChange={(e) => {
                const [y, m] = e.target.value.split('-').map(Number);
                setSelectedYear(y);
                setSelectedMonth(m);
                if (typeof window !== 'undefined') {
                  const newUrl = `${window.location.pathname}?month=${m}&year=${y}`;
                  window.history.pushState({ path: newUrl }, '', newUrl);
                }
              }}
              className="bg-transparent border-none text-slate-300 text-xs font-semibold focus:ring-0 focus:outline-none cursor-pointer hover:text-white"
            >
              {getPastMonths().map((m) => (
                <option key={`${m.year}-${m.month}`} value={`${m.year}-${m.month}`} className="bg-slate-950 text-slate-300">
                  {m.label}
                </option>
              ))}
            </select>
            <button
              id="refresh-mirror"
              onClick={loadData}
              className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/5 transition-all"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">

        {error && (
          <div className="card p-4 border-rose-500/20 bg-rose-500/5">
            <p className="text-sm text-rose-400">{error}</p>
          </div>
        )}

        {/* ── Progress card (when no report yet) ──────────────────────────── */}
        {!report && status && (
          <div className="card p-6 animate-fadeIn">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                <Brain className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <h2 className="text-white font-semibold">Your {monthName} Portrait</h2>
                <p className="text-xs text-slate-500">
                  {status.qualifies
                    ? 'Ready to generate your monthly self-portrait'
                    : `${status.messages_remaining} more message${status.messages_remaining !== 1 ? 's' : ''} needed to unlock`}
                </p>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mb-6">
              <div className="flex justify-between text-xs text-slate-500 mb-2">
                <span>{status.message_count} messages this month</span>
                <span>{status.threshold} required</span>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-violet-600 to-indigo-600 rounded-full transition-all duration-700"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>

            {status.qualifies && (
              <button
                id="generate-report-btn"
                onClick={handleGenerate}
                disabled={generating}
                className="btn-primary w-full"
              >
                {generating
                  ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating your portrait...</>
                  : <><Sparkles className="w-4 h-4" /> Generate Mirror Me Report</>}
              </button>
            )}
          </div>
        )}

        {/* ── Report ───────────────────────────────────────────────────────── */}
        {report && report.has_data && (
          <div className="space-y-5 animate-fadeIn">

            {/* Last updated banner */}
            <div className="flex items-center justify-between px-1">
              <p className="text-xs text-slate-500">
                Last updated:{' '}
                <span className="text-slate-400 font-medium">
                  {report.last_generated_at
                    ? new Date(report.last_generated_at).toLocaleString()
                    : status?.last_generated_at
                      ? new Date(status.last_generated_at).toLocaleString()
                      : 'Unknown'}
                </span>
              </p>
              {status?.qualifies && (
                <button
                  id="refresh-latest-btn"
                  onClick={handleGenerate}
                  disabled={generating}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold
                    bg-violet-500/10 border border-violet-500/20 text-violet-300
                    hover:bg-violet-500/20 hover:text-white transition-all disabled:opacity-50"
                >
                  {generating
                    ? <><Loader2 className="w-3 h-3 animate-spin" /> Refreshing...</>
                    : <><RefreshCw className="w-3 h-3" /> Refresh with latest chats</>}
                </button>
              )}
            </div>

            {/* Hero stats */}
            <div className="card p-6">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-3">
                    {monthName} {status?.year} · Monthly Portrait
                  </p>
                  <p className="text-sm text-slate-300 leading-relaxed">{report.month_summary}</p>
                </div>
                {report.avg_mood !== undefined && (
                  <MoodRing score={report.avg_mood} />
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-white/[0.05] flex items-center gap-6">
                <div className="text-center">
                  <p className="text-xl font-bold text-white">{report.total_messages ?? 0}</p>
                  <p className="text-xs text-slate-500">conversations</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-white">{report.insights?.length ?? 0}</p>
                  <p className="text-xs text-slate-500">key insights</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-white">{report.lessons_learned?.length ?? 0}</p>
                  <p className="text-xs text-slate-500">lessons</p>
                </div>
              </div>
            </div>

            {/* Tabs Navigation */}
            <div className="flex border-b border-white/[0.06] gap-2 p-1">
              <button
                onClick={() => setActiveTab('reflection')}
                className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
                  activeTab === 'reflection'
                    ? 'bg-violet-500/15 border border-violet-500/30 text-violet-300'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                <Brain className="w-3.5 h-3.5" />
                Reflection Report
              </button>
              <button
                onClick={() => setActiveTab('clinical')}
                className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
                  activeTab === 'clinical'
                    ? 'bg-violet-500/15 border border-violet-500/30 text-violet-300'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                Practitioner Insights
              </button>
            </div>

            {activeTab === 'reflection' && (
              <>
                {/* Mood trend */}
                {report.mood_trend_description && (
                  <div className="card p-5 animate-fadeIn">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-4 h-4 text-violet-400" />
                      <h3 className="text-sm font-semibold text-white">Mood Journey</h3>
                    </div>
                    <p className="text-sm text-slate-400 leading-relaxed">{report.mood_trend_description}</p>
                  </div>
                )}

                {/* Insights */}
                {(report.insights?.length ?? 0) > 0 && (
                  <div className="card p-5 animate-fadeIn">
                    <div className="flex items-center gap-2 mb-4">
                      <Lightbulb className="w-4 h-4 text-yellow-400" />
                      <h3 className="text-sm font-semibold text-white">Key Themes</h3>
                    </div>
                    <div className="space-y-4">
                      {report.insights!.map((ins, i) => (
                        <div key={i} className="flex gap-3">
                          <div className="w-6 h-6 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center flex-shrink-0 mt-0.5 text-xs text-violet-400 font-bold">
                            {i + 1}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-white mb-1">{ins.title}</p>
                            <p className="text-xs text-slate-400 leading-relaxed">{ins.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Lessons + Self-care */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fadeIn">
                  {(report.lessons_learned?.length ?? 0) > 0 && (
                    <div className="card p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <Star className="w-4 h-4 text-amber-400" />
                        <h3 className="text-sm font-semibold text-white">Lessons Learned</h3>
                      </div>
                      <ul className="space-y-2">
                        {report.lessons_learned!.map((l, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-amber-500/60 mt-1.5 flex-shrink-0" />
                            <p className="text-xs text-slate-400 leading-relaxed">{l}</p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {(report.self_care_recommendations?.length ?? 0) > 0 && (
                    <div className="card p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <Heart className="w-4 h-4 text-rose-400" />
                        <h3 className="text-sm font-semibold text-white">Self-Care Tips</h3>
                      </div>
                      <ul className="space-y-2">
                        {report.self_care_recommendations!.map((r, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-rose-500/60 mt-1.5 flex-shrink-0" />
                            <p className="text-xs text-slate-400 leading-relaxed">{r}</p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Word cloud */}
                {(report.word_cloud?.length ?? 0) > 0 && (
                  <div className="card p-5 animate-fadeIn">
                    <div className="flex items-center gap-2 mb-4">
                      <Cloud className="w-4 h-4 text-sky-400" />
                      <h3 className="text-sm font-semibold text-white">Your Language This Month</h3>
                    </div>
                    <WordCloud words={report.word_cloud!} />
                  </div>
                )}

                {/* Closing message */}
                {report.supportive_closing && (
                  <div className="card p-6 border-violet-500/20 bg-gradient-to-br from-violet-500/5 to-indigo-500/5 animate-fadeIn">
                    <div className="flex items-center gap-2 mb-3">
                      <Sparkles className="w-4 h-4 text-violet-400" />
                      <h3 className="text-sm font-semibold text-violet-300">A note from your InnerVoice</h3>
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed italic">"{report.supportive_closing}"</p>
                  </div>
                )}
              </>
            )}

            {activeTab === 'clinical' && (
              <div className="space-y-5 animate-fadeIn">
                {report.clinical_insights ? (
                  <>
                    {/* Practitioner Summary Card */}
                    <div className="card p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <FileText className="w-4 h-4 text-violet-400" />
                        <h3 className="text-sm font-semibold text-white">Practitioner Clinical Summary</h3>
                      </div>
                      <p className="text-sm text-slate-300 leading-relaxed">
                        {report.clinical_insights.practitioner_summary}
                      </p>
                      
                      <div className="mt-4 pt-4 border-t border-white/[0.05] flex items-center justify-between">
                        <span className="text-xs text-slate-500 font-medium">Calculated Mood Volatility:</span>
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          report.clinical_insights.mood_volatility === 'High' 
                            ? 'bg-rose-500/10 border border-rose-500/20 text-rose-400'
                            : report.clinical_insights.mood_volatility === 'Moderate'
                            ? 'bg-amber-500/10 border border-amber-500/20 text-amber-400'
                            : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                        }`}>
                          {report.clinical_insights.mood_volatility} Volatility
                        </span>
                      </div>
                    </div>

                    {/* Stressors & Coping Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Key Stressors */}
                      <div className="card p-5">
                        <div className="flex items-center gap-2 mb-3">
                          <AlertTriangle className="w-4 h-4 text-amber-400" />
                          <h3 className="text-sm font-semibold text-white">Identified Stressors</h3>
                        </div>
                        <ul className="space-y-2">
                          {report.clinical_insights.key_stressors?.map((st, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-amber-500/60 mt-1.5 flex-shrink-0" />
                              <p className="text-xs text-slate-400 leading-relaxed">{st}</p>
                            </li>
                          ))}
                          {(!report.clinical_insights.key_stressors || report.clinical_insights.key_stressors.length === 0) && (
                            <p className="text-xs text-slate-500 italic">No significant stressors identified.</p>
                          )}
                        </ul>
                      </div>

                      {/* Coping Mechanisms */}
                      <div className="card p-5">
                        <div className="flex items-center gap-2 mb-3">
                          <Heart className="w-4 h-4 text-emerald-400" />
                          <h3 className="text-sm font-semibold text-white">Observed Coping Behaviors</h3>
                        </div>
                        <ul className="space-y-2">
                          {report.clinical_insights.coping_mechanisms_observed?.map((cm, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/60 mt-1.5 flex-shrink-0" />
                              <p className="text-xs text-slate-400 leading-relaxed">{cm}</p>
                            </li>
                          ))}
                          {(!report.clinical_insights.coping_mechanisms_observed || report.clinical_insights.coping_mechanisms_observed.length === 0) && (
                            <p className="text-xs text-slate-500 italic">No coping behaviors logged.</p>
                          )}
                        </ul>
                      </div>
                    </div>

                    {/* Cognitive Distortions / Thinking Patterns */}
                    <div className="card p-5">
                      <div className="flex items-center gap-2 mb-4">
                        <Brain className="w-4 h-4 text-sky-400" />
                        <h3 className="text-sm font-semibold text-white">Cognitive Patterns & Distortions</h3>
                      </div>
                      
                      <div className="space-y-4">
                        {report.clinical_insights.cognitive_distortions_detected?.map((dist, i) => (
                          <div key={i} className="flex gap-3">
                            <div className="w-6 h-6 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center flex-shrink-0 mt-0.5 text-xs text-sky-400 font-bold">
                              {i + 1}
                            </div>
                            <div>
                              <p className="text-sm font-medium text-white mb-1">{dist.distortion_type}</p>
                              <p className="text-xs text-slate-400 leading-relaxed">{dist.evidence}</p>
                            </div>
                          </div>
                        ))}
                        {(!report.clinical_insights.cognitive_distortions_detected || report.clinical_insights.cognitive_distortions_detected.length === 0) && (
                          <p className="text-xs text-slate-500 italic">No distinct cognitive distortions detected this month.</p>
                        )}
                      </div>
                    </div>

                    {/* Disclaimer card */}
                    <div className="card p-4 border-slate-500/10 bg-slate-500/5">
                      <p className="text-[11px] text-slate-500 leading-relaxed">
                        <strong>Clinical Disclaimer:</strong> This section uses clinical language and psychological analysis models (such as detecting Cognitive Distortions) to synthesize your reflections. It is intended to help you and your healthcare professional/therapist better analyze patterns in your mood and mental health. This is not a diagnosis. Please review these insights together with your certified provider.
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="card p-8 text-center space-y-3">
                    <p className="text-sm text-slate-400">Clinical insights are not available for this report.</p>
                    <p className="text-xs text-slate-600">This report was generated with an older version of the prompt. Click "Refresh with latest chats" or "Regenerate Report" below to generate clinical insights.</p>
                  </div>
                )}
              </div>
            )}

            {/* Regenerate */}
            <div className="flex justify-center pb-4">
              <button
                id="regenerate-report-btn"
                onClick={handleGenerate}
                disabled={generating}
                className="btn-secondary flex items-center gap-2 text-xs"
              >
                {generating
                  ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Regenerating...</>
                  : <><RefreshCw className="w-3.5 h-3.5" /> Regenerate Report</>}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
