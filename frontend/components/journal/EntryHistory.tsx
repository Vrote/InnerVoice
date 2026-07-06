'use client';
import { useEffect, useState } from 'react';
import { Clock, ChevronDown, ChevronUp } from 'lucide-react';
import api from '@/lib/api';

const EMOTION_EMOJIS: Record<string, string> = {
  happy: '😊', excited: '🚀', grateful: '🙏', motivated: '💪',
  hopeful: '🌱', neutral: '😶', confused: '🤔', nostalgic: '🕊️',
  sad: '💙', lonely: '🌙', anxious: '😰', overwhelmed: '😵',
  angry: '🔥', fearful: '😨', disappointed: '😔', burnout: '🪫',
};

interface Entry {
  id: string;
  content: string;
  word_count: number;
  created_at: string;
  ai_response: string | null;
  emotion: string;
  mood_score: number;
}

export default function EntryHistory() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const fetchEntries = async (p = 1) => {
    try {
      setLoading(true);
      const res = await api.get(`/api/journal/history?page=${p}&limit=10`);
      setEntries(res.data);
    } catch (e) {
      console.error('Failed to load entries:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchEntries(page); }, [page]);

  if (loading) return (
    <div className="space-y-3">
      {[1, 2, 3].map(i => (
        <div key={i} className="glass-panel rounded-xl p-4 animate-pulse">
          <div className="h-3 bg-white/10 rounded w-1/4 mb-3" />
          <div className="h-4 bg-white/10 rounded w-3/4 mb-2" />
          <div className="h-4 bg-white/10 rounded w-1/2" />
        </div>
      ))}
    </div>
  );

  if (!entries.length) return (
    <div className="text-center py-12 text-slate-500">
      <p className="text-4xl mb-3">📖</p>
      <p className="text-sm">No entries yet. Write your first one above!</p>
    </div>
  );

  return (
    <div className="space-y-3">
      {entries.map((entry) => {
        const isOpen = expanded === entry.id;
        const emoji = EMOTION_EMOJIS[entry.emotion] || '✨';
        return (
          <div key={entry.id} className="glass-panel rounded-xl border border-white/5 overflow-hidden transition-all">
            <button
              onClick={() => setExpanded(isOpen ? null : entry.id)}
              className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-white/3 transition-all"
            >
              <span className="text-xl">{emoji}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">{entry.content.slice(0, 80)}...</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <Clock className="w-3 h-3 text-slate-500" />
                  <span className="text-xs text-slate-500">{entry.created_at.split(' ')[0]}</span>
                  <span className="text-xs text-slate-600">·</span>
                  <span className="text-xs text-slate-500">{entry.word_count} words</span>
                  <span className="text-xs text-slate-600">·</span>
                  <span className="text-xs text-slate-400 capitalize">{entry.emotion}</span>
                </div>
              </div>
              {isOpen ? (
                <ChevronUp className="w-4 h-4 text-slate-500 shrink-0" />
              ) : (
                <ChevronDown className="w-4 h-4 text-slate-500 shrink-0" />
              )}
            </button>

            {isOpen && (
              <div className="px-4 pb-4 space-y-3">
                <div className="pt-2 border-t border-white/5">
                  <p className="text-xs text-slate-500 mb-1.5">Your entry</p>
                  <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{entry.content}</p>
                </div>
                {entry.ai_response && (
                  <div className="bg-violet-500/5 border border-violet-500/15 rounded-xl p-4">
                    <p className="text-xs text-violet-400 mb-1.5">✨ InnerVoice replied</p>
                    <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{entry.ai_response}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}

      <div className="flex gap-2 pt-2">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="flex-1 py-2 rounded-xl text-xs text-slate-400 bg-white/5 hover:bg-white/8 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          ← Newer
        </button>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={entries.length < 10}
          className="flex-1 py-2 rounded-xl text-xs text-slate-400 bg-white/5 hover:bg-white/8 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          Older →
        </button>
      </div>
    </div>
  );
}
