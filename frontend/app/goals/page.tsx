'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Target, Plus, Loader2 } from 'lucide-react';
import Navbar from '@/components/shared/Navbar';
import GoalCard from '@/components/goals/GoalCard';
import GoalProgress from '@/components/goals/GoalProgress';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { useAuthStore } from '@/stores/authStore';
import api from '@/lib/api';

export default function GoalsPage() {
  const router = useRouter();
  const { token, loadFromStorage, isLoading } = useAuthStore();
  const [goals, setGoals]           = useState<any[]>([]);
  const [pageLoading, setPageLoading] = useState(true);
  const [filter, setFilter]           = useState<string>('all');

  useEffect(() => { loadFromStorage(); }, [loadFromStorage]);
  useEffect(() => {
    if (!isLoading && !token) router.push('/auth/login');
  }, [isLoading, token, router]);

  const fetchGoals = async () => {
    try {
      const res = await api.get('/api/goals');
      setGoals(res.data || []);
    } catch (e) {
      console.error('Goals load error:', e);
    } finally {
      setPageLoading(false);
    }
  };

  useEffect(() => { if (token) fetchGoals(); }, [token]);

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await api.put(`/api/goals/${id}`, { status });
      fetchGoals();
    } catch (e) { console.error(e); }
  };

  const filtered = filter === 'all' ? goals : goals.filter(g => g.status === filter);
  const active    = goals.filter(g => g.status === 'active').length;
  const completed = goals.filter(g => g.status === 'completed').length;
  const paused    = goals.filter(g => g.status === 'paused').length;

  if (isLoading || pageLoading) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <LoadingSpinner size="lg" label="Loading goals..." /></div>;
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />
      <main className="pl-64 min-h-screen">
        <div className="max-w-4xl mx-auto px-8 py-10">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-600 flex items-center justify-center">
                <Target className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Goals</h1>
                <p className="text-sm text-slate-400">AI-detected and manually created goals</p>
              </div>
            </div>
          </div>

          {/* Progress summary */}
          <div className="mb-6">
            <GoalProgress active={active} completed={completed} paused={paused} />
          </div>

          {/* Filter tabs */}
          <div className="flex gap-2 mb-6">
            {['all', 'active', 'completed', 'paused'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                  filter === f
                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                    : 'text-slate-500 hover:text-white bg-white/5 hover:bg-white/8'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
                <span className="ml-1.5 opacity-60">
                  {f === 'all' ? goals.length : goals.filter(g => g.status === f).length}
                </span>
              </button>
            ))}
          </div>

          {/* Goals grid */}
          {filtered.length === 0 ? (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/5">
              <p className="text-4xl mb-3">🎯</p>
              <p className="text-white font-semibold mb-2">No goals yet</p>
              <p className="text-sm text-slate-500">
                Write journal entries and InnerVoice will detect your goals automatically.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {filtered.map(goal => (
                <GoalCard key={goal.id} goal={goal} onStatusChange={handleStatusChange} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
