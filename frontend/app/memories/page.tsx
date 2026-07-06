'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Database, Trash2, AlertCircle } from 'lucide-react';
import Navbar from '@/components/shared/Navbar';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { useAuthStore } from '@/stores/authStore';
import api from '@/lib/api';

const TYPE_COLORS: Record<string, string> = {
  goal:         'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  hobby:        'text-violet-400 bg-violet-500/10 border-violet-500/20',
  relationship: 'text-pink-400 bg-pink-500/10 border-pink-500/20',
  fear:         'text-rose-400 bg-rose-500/10 border-rose-500/20',
  achievement:  'text-amber-400 bg-amber-500/10 border-amber-500/20',
  habit:        'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  preference:   'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
  context:      'text-slate-400 bg-slate-500/10 border-slate-500/20',
};

export default function MemoriesPage() {
  const router = useRouter();
  const { token, loadFromStorage, isLoading } = useAuthStore();
  const [memories, setMemories]       = useState<any[]>([]);
  const [pageLoading, setPageLoading] = useState(true);
  const [deletingId, setDeletingId]   = useState<string | null>(null);

  useEffect(() => { loadFromStorage(); }, [loadFromStorage]);
  useEffect(() => {
    if (!isLoading && !token) router.push('/auth/login');
  }, [isLoading, token, router]);

  const fetchMemories = async () => {
    try {
      const res = await api.get('/api/memories');
      setMemories(res.data || []);
    } catch (e) {
      console.error('Memories load error:', e);
    } finally {
      setPageLoading(false);
    }
  };

  useEffect(() => { if (token) fetchMemories(); }, [token]);

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await api.delete(`/api/memories/${id}`);
      setMemories(m => m.filter(x => x.id !== id));
    } catch (e) {
      console.error('Delete error:', e);
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading || pageLoading) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <LoadingSpinner size="lg" label="Loading memories..." /></div>;
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />
      <main className="pl-64 min-h-screen">
        <div className="max-w-4xl mx-auto px-8 py-10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Long-term Memories</h1>
              <p className="text-sm text-slate-400">What InnerVoice has learned and remembers about you</p>
            </div>
          </div>

          {/* Info banner */}
          <div className="flex items-start gap-3 glass-panel rounded-xl p-4 border border-white/5 mb-6">
            <AlertCircle className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
            <p className="text-sm text-slate-400">
              These memories help InnerVoice personalize every response. The AI creates them automatically from your journal entries. You can delete any memory you&apos;re not comfortable with.
            </p>
          </div>

          {memories.length === 0 ? (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/5">
              <p className="text-4xl mb-3">🧠</p>
              <p className="text-white font-semibold mb-2">No memories yet</p>
              <p className="text-sm text-slate-500">Write journal entries and InnerVoice will start learning about you.</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {memories.map(mem => {
                const typeStyle = TYPE_COLORS[mem.memory_type] || TYPE_COLORS.context;
                return (
                  <div key={mem.id} className="glass-panel rounded-xl p-4 border border-white/5 hover:border-white/10 transition-all flex items-start gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${typeStyle}`}>
                          {mem.memory_type}
                        </span>
                        <span className="text-xs text-slate-600">
                          Importance: {Math.round((mem.importance_score || 0.5) * 100)}%
                        </span>
                      </div>
                      <p className="text-sm text-slate-200 leading-relaxed">{mem.memory_text}</p>
                      <p className="text-xs text-slate-600 mt-1.5">
                        {mem.created_at ? mem.created_at.slice(0, 10) : ''}
                        {mem.reference_count > 0 && ` · referenced ${mem.reference_count}×`}
                      </p>
                    </div>
                    <button
                      onClick={() => handleDelete(mem.id)}
                      disabled={deletingId === mem.id}
                      className="w-8 h-8 rounded-lg bg-red-500/0 hover:bg-red-500/10 text-slate-600 hover:text-red-400 flex items-center justify-center transition-all shrink-0 disabled:opacity-40"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
