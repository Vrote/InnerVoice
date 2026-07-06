'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { LayoutDashboard } from 'lucide-react';
import Navbar from '@/components/shared/Navbar';
import EmotionChart from '@/components/dashboard/EmotionChart';
import StreakCard from '@/components/dashboard/StreakCard';
import WeeklySummary from '@/components/dashboard/WeeklySummary';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { useAuthStore } from '@/stores/authStore';
import api from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const { token, user, loadFromStorage, isLoading } = useAuthStore();
  const [timeline, setTimeline]   = useState([]);
  const [stats, setStats]         = useState<any>(null);
  const [weekly, setWeekly]       = useState<any>(null);
  const [pageLoading, setPageLoading] = useState(true);

  useEffect(() => { loadFromStorage(); }, [loadFromStorage]);
  useEffect(() => {
    if (!isLoading && !token) router.push('/auth/login');
  }, [isLoading, token, router]);

  useEffect(() => {
    if (!token) return;
    const load = async () => {
      try {
        const [tlRes, stRes, wkRes] = await Promise.all([
          api.get('/api/emotions/timeline?days=30'),
          api.get('/api/emotions/stats?days=30'),
          api.get('/api/weekly'),
        ]);
        const rawTimeline = tlRes.data || [];
        // Map created_at -> date for the chart
        const mappedTimeline = rawTimeline.map((r: any) => ({
          ...r,
          date: r.created_at?.slice(0, 10) || '',
        }));
        setTimeline(mappedTimeline);
        setStats(stRes.data);
        setWeekly(wkRes.data);
      } catch (e) {
        console.error('Dashboard load error:', e);
      } finally {
        setPageLoading(false);
      }
    };
    load();
  }, [token]);

  if (isLoading || pageLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <LoadingSpinner size="lg" label="Loading your dashboard..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />
      <main className="pl-64 min-h-screen">
        <div className="max-w-4xl mx-auto px-8 py-10">
          {/* Header */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Dashboard</h1>
              <p className="text-sm text-slate-400">Your emotional landscape at a glance</p>
            </div>
          </div>

          {/* Streak */}
          <div className="mb-6">
            <StreakCard
              streak={user?.streak_count || 0}
              longestStreak={user?.longest_streak || 0}
              totalEntries={user?.total_messages || 0}
            />
          </div>

          {/* Mood Chart */}
          <div className="glass-panel rounded-2xl p-6 border border-white/5 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-white">Mood Timeline — Last 30 Days</h2>
              {stats && (
                <div className="flex items-center gap-4">
                  <span className="text-xs text-slate-500">Avg: <span className="text-violet-400 font-semibold">{stats.avg_mood_30d?.toFixed(1) || '—'}/10</span></span>
                  <span className="text-xs text-slate-500 capitalize">Most common: <span className="text-white font-semibold">{stats.most_common_emotion || '—'}</span></span>
                </div>
              )}
            </div>
            <EmotionChart data={timeline} />
          </div>

          {/* Stats cards */}
          {stats && (
            <div className="grid grid-cols-3 gap-4 mb-6">
              {[
                { label: 'Best day this week', value: stats.best_day_this_week || '—', color: 'text-emerald-400' },
                { label: 'Hardest day', value: stats.hardest_day_this_week || '—', color: 'text-rose-400' },
                { label: 'Mood trend', value: stats.mood_trend || '—', color: 'text-cyan-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="glass-panel rounded-xl p-4 border border-white/5 text-center">
                  <p className="text-xs text-slate-500 mb-1">{label}</p>
                  <p className={`text-base font-semibold ${color} capitalize`}>{value}</p>
                </div>
              ))}
            </div>
          )}

          {/* Weekly summary */}
          <WeeklySummary summary={weekly} />
        </div>
      </main>
    </div>
  );
}
