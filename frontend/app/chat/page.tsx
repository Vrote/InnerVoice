'use client';
import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Sparkles, Send, Loader2, ChevronDown, ChevronUp,
  Flame, Brain, LogOut, BarChart2, ArrowRight, AlertTriangle
} from 'lucide-react';
import api from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import CopingToolkit from '@/components/chat/CopingToolkit';

// ── Types ─────────────────────────────────────────────────────────────────────
interface Emotion {
  primary_emotion?: string;
  mood_score?: number;
  intensity?: number;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: Date;
  emotion?: Emotion;
  tools_used?: string[];
  reasoning_log?: { step: string; tool?: string; reasoning?: string }[];
  followup_question?: string | null;
  status?: string;
  crisis_level?: string;
  isTyping?: boolean;
  coping_suggestion?: {
    show: boolean;
    emotion?: string;
    exercise_type?: 'breathing' | 'gratitude' | 'bodyscan';
    title?: string;
    subtitle?: string;
  };
}

// ── Typewriter hook ───────────────────────────────────────────────────────────
function useTypewriter(text: string, speed = 18, active = true) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!active) { setDisplayed(text); setDone(true); return; }
    setDisplayed('');
    setDone(false);
    let i = 0;
    const timer = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) { clearInterval(timer); setDone(true); }
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed, active]);

  return { displayed, done };
}

// ── Emotion colours ───────────────────────────────────────────────────────────
const emotionColor: Record<string, string> = {
  happy: 'text-yellow-400', excited: 'text-orange-400', grateful: 'text-emerald-400',
  hopeful: 'text-sky-400', motivated: 'text-blue-400', nostalgic: 'text-purple-400',
  sad: 'text-blue-300', lonely: 'text-slate-400', anxious: 'text-amber-400',
  angry: 'text-red-400', burnout: 'text-orange-500', overwhelmed: 'text-rose-400',
  fearful: 'text-rose-300', disappointed: 'text-slate-500', confused: 'text-indigo-400',
  neutral: 'text-slate-400',
};

// ── Time & Date formatting helpers ───────────────────────────────────────────
const formatTime = (dateInput: Date | string) => {
  const d = new Date(dateInput);
  if (isNaN(d.getTime())) return "";
  let hours = d.getHours();
  const minutes = d.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  const minStr = minutes < 10 ? '0' + minutes : minutes;
  return `${hours}:${minStr} ${ampm}`;
};

const formatDateDivider = (dateInput: Date | string) => {
  const d = new Date(dateInput);
  if (isNaN(d.getTime())) return "";
  
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
  const msgDate = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  
  if (msgDate.getTime() === today.getTime()) {
    return "Today";
  }
  if (msgDate.getTime() === yesterday.getTime()) {
    return "Yesterday";
  }
  
  const diffTime = today.getTime() - msgDate.getTime();
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
  if (diffDays < 7) {
    return d.toLocaleDateString('en-US', { weekday: 'long' });
  }
  
  const day = d.getDate();
  const month = d.toLocaleDateString('en-US', { month: 'short' });
  const year = d.getFullYear();
  if (year === now.getFullYear()) {
    return `${day} ${month}`;
  }
  return `${day} ${month} ${year}`;
};

// ── AI Bubble component ───────────────────────────────────────────────────────
function AIBubble({ msg, onReply }: { msg: ChatMessage; onReply?: (q: string) => void }) {
  const { displayed, done } = useTypewriter(msg.content, 16, msg.isTyping ?? false);
  const [showReasoning, setShowReasoning] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [replying, setReplying] = useState(false);

  const text = msg.isTyping ? displayed : msg.content;
  const ec   = emotionColor[msg.emotion?.primary_emotion ?? 'neutral'];

  const handleReply = async () => {
    if (!replyText.trim() || replying) return;
    setReplying(true);
    onReply?.(replyText.trim());
  };

  return (
    <div className="flex flex-col gap-2 animate-fadeIn">
      {/* Avatar row */}
      <div className="flex items-start gap-3">
        <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md shadow-violet-500/30">
          <Sparkles className="w-3.5 h-3.5 text-white" />
        </div>
        <div className="flex flex-col gap-1.5 max-w-[78%]">
          {/* Bubble */}
          <div className={`bubble-ai ${msg.isTyping && !done ? 'typewriter-cursor' : ''}`}>
            {text.split('\n').map((line, i) => (
              <span key={i}>
                {line}
                {i < text.split('\n').length - 1 && <br />}
              </span>
            ))}
          </div>

          {/* Timestamp */}
          {(!msg.isTyping || done) && (
            <span className="text-xs text-white/25 select-none pr-1 mt-0.5 self-end">
              {formatTime(msg.timestamp)}
            </span>
          )}

          {done && msg.coping_suggestion?.show && (
            <CopingToolkit suggestion={msg.coping_suggestion} />
          )}

          {/* Crisis badge */}
          {msg.crisis_level && msg.crisis_level !== 'none' && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/20 w-fit">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span className="text-xs text-rose-300 font-medium">Crisis support resources included</span>
            </div>
          )}

          {/* Meta row */}
          {done && (
            <div className="flex items-center gap-3 px-1">
              {msg.emotion?.primary_emotion && (
                <span className={`text-xs font-medium ${ec}`}>
                  {msg.emotion.primary_emotion}
                  {msg.emotion.mood_score ? ` · ${msg.emotion.mood_score.toFixed(1)}/10` : ''}
                </span>
              )}
              {(msg.tools_used?.length ?? 0) > 0 && (
                <button
                  onClick={() => setShowReasoning(v => !v)}
                  className="flex items-center gap-1 text-xs text-slate-600 hover:text-slate-400 transition-colors"
                >
                  <Brain className="w-3 h-3" />
                  {msg.tools_used!.length} tools
                  {showReasoning ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>
              )}
            </div>
          )}

          {/* Reasoning panel */}
          {showReasoning && (
            <div className="glass-panel border border-white/[0.06] rounded-xl p-3 space-y-1.5 animate-fadeIn">
              <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">Reasoning steps</p>
              {msg.reasoning_log?.map((log, i) => (
                <div key={i} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-violet-500/60 mt-1.5 flex-shrink-0" />
                  <div>
                    {log.tool && <span className="text-xs text-violet-400 font-mono">{log.tool}</span>}
                    {log.reasoning && <p className="text-xs text-slate-500">{log.reasoning}</p>}
                  </div>
                </div>
              ))}
              {msg.tools_used?.map((t, i) => (
                <div key={`t-${i}`} className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500/60 flex-shrink-0" />
                  <span className="text-xs text-slate-500 font-mono">{t}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Inline followup */}
      {done && msg.followup_question && msg.status === 'waiting_for_user' && (
        <div className="ml-10 animate-slideUp">
          <div className="glass-panel border border-violet-500/20 rounded-2xl p-4 max-w-[78%]">
            <p className="text-sm text-violet-300 mb-3 leading-relaxed">{msg.followup_question}</p>
            <div className="flex gap-2">
              <input
                type="text"
                value={replyText}
                onChange={e => setReplyText(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleReply()}
                placeholder="Your answer..."
                className="flex-1 input-field text-xs py-2"
                disabled={replying}
              />
              <button
                onClick={handleReply}
                disabled={!replyText.trim() || replying}
                className="btn-primary px-3 py-2"
              >
                {replying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ArrowRight className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Thinking indicator ────────────────────────────────────────────────────────
function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-3 animate-fadeIn">
      <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-violet-500/30">
        <Sparkles className="w-3.5 h-3.5 text-white" />
      </div>
      <div className="bubble-ai flex items-center gap-2">
        <span className="text-xs text-slate-500">thinking</span>
        <div className="flex gap-1">
          {[0, 1, 2].map(i => (
            <div key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400/60"
              style={{ animation: `pulse 1.2s ${i * 0.2}s ease-in-out infinite` }} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Main Chat Page ─────────────────────────────────────────────────────────────
export default function ChatPage() {
  const router                   = useRouter();
  const { user, token, isLoading, loadFromStorage, logout } = useAuthStore();
  const [messages, setMessages]  = useState<ChatMessage[]>([]);
  const [input, setInput]        = useState('');
  const [sending, setSending]    = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const bottomRef                = useRef<HTMLDivElement>(null);
  const textareaRef              = useRef<HTMLTextAreaElement>(null);
  const pendingMsgId             = useRef<string | null>(null);

  // Time partition state
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear]   = useState(new Date().getFullYear());

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

  // Auth guard
  useEffect(() => { loadFromStorage(); }, [loadFromStorage]);
  useEffect(() => {
    if (!isLoading && !token) router.replace('/auth/login');
  }, [isLoading, token, router]);

  // Load history on mount or month change
  useEffect(() => {
    if (!token || historyLoaded) return;
    api.get(`/api/history?limit=30&year=${selectedYear}&month=${selectedMonth}`).then(res => {
      const items: any[] = (res.data?.items ?? res.data ?? []);
      const hydrated: ChatMessage[] = [];
      for (const item of [...items].reverse()) {
        hydrated.push({
          id:        item.id + '-u',
          role:      'user',
          content:   item.user_message,
          timestamp: new Date(item.created_at),
          isTyping:  false,
        });
        if (item.ai_response) {
          hydrated.push({
            id:               item.id + '-a',
            role:             'ai',
            content:          item.ai_response,
            timestamp:        new Date(item.created_at),
            emotion:          item.emotion,
            tools_used:       item.tools_used ?? [],
            followup_question: item.followup_question,
            status:           item.followup_pending ? 'waiting_for_user' : 'done',
            isTyping:         false,
          });
        }
      }
      setMessages(hydrated);
      setHistoryLoaded(true);
    }).catch(() => setHistoryLoaded(true));
  }, [token, historyLoaded, selectedMonth, selectedYear]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const ta = textareaRef.current;
    if (ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 180) + 'px'; }
  };

  const sendMessage = useCallback(async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || sending) return;

    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setSending(true);

    // Optimistic user bubble
    const tmpUserId = `tmp-u-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: tmpUserId, role: 'user', content, timestamp: new Date(), isTyping: false
    }]);

    // Thinking bubble
    const tmpAiId = `tmp-ai-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: tmpAiId, role: 'ai', content: '', timestamp: new Date(), isTyping: true
    }]);

    try {
      const res = await api.post('/api/chat', { message: content });
      const data = res.data ?? res;

      const msgId    = data.message_id;
      const response = data.response ?? '';
      pendingMsgId.current = data.status === 'waiting_for_user' ? msgId : null;

      setMessages(prev => prev.map(m =>
        m.id === tmpAiId
          ? {
              ...m,
              id:               msgId + '-a',
              content:          response,
              emotion:          data.emotions ?? {},
              tools_used:       data.tools_used ?? [],
              reasoning_log:    data.reasoning_log ?? [],
              followup_question: data.followup_question ?? null,
              status:           data.status ?? 'done',
              crisis_level:     data.crisis_level ?? 'none',
              coping_suggestion: data.coping_suggestion,
              isTyping:         true,
            }
          : m.id === tmpUserId
            ? { ...m, id: msgId + '-u' }
            : m
      ));
    } catch (err: any) {
      setMessages(prev => prev.filter(m => m.id !== tmpAiId).map(m =>
        m.id === tmpUserId
          ? { ...m, content: content + ' ⚠️' }
          : m
      ));
    } finally {
      setSending(false);
    }
  }, [input, sending]);

  const handleFollowupReply = useCallback(async (replyText: string) => {
    if (!pendingMsgId.current) return;
    const msgId = pendingMsgId.current;
    setSending(true);

    const tmpAiId = `tmp-ai-reply-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: tmpAiId, role: 'ai', content: '', timestamp: new Date(), isTyping: true
    }]);

    try {
      const res  = await api.post('/api/chat/reply', { message_id: msgId, reply: replyText });
      const data = res.data ?? res;

      pendingMsgId.current = null;
      setMessages(prev => prev.map(m =>
        m.id === tmpAiId
          ? {
              ...m,
              id:           msgId + '-reply-a',
              content:      data.response ?? '',
              emotion:      data.emotions ?? {},
              tools_used:   data.tools_used ?? [],
              status:       'done',
              crisis_level: data.crisis_level ?? 'none',
              coping_suggestion: data.coping_suggestion,
              isTyping:     true,
            }
          : m
      ));
    } catch {
      setMessages(prev => prev.filter(m => m.id !== tmpAiId));
    } finally {
      setSending(false);
    }
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30 animate-pulse">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <p className="text-slate-500 text-sm">Loading InnerVoice...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] flex flex-col" style={{ maxHeight: '100dvh' }}>

      {/* Ambient glow */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-violet-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[200px] bg-indigo-600/5 rounded-full blur-3xl" />
      </div>

      {/* ── Header ────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 border-b border-white/[0.05] bg-[#0f0f0f]/80 backdrop-blur-xl">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
          {/* Logo & Month Selector */}
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-md shadow-violet-500/30">
              <Sparkles className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-semibold text-white text-sm tracking-tight hidden sm:inline">InnerVoice</span>
            
            <select
              value={`${selectedYear}-${selectedMonth}`}
              onChange={(e) => {
                const [y, m] = e.target.value.split('-').map(Number);
                setSelectedYear(y);
                setSelectedMonth(m);
                setHistoryLoaded(false); // force reload
              }}
              className="bg-transparent border-none text-slate-300 text-xs font-semibold focus:ring-0 focus:outline-none cursor-pointer hover:text-white"
            >
              {getPastMonths().map((m) => (
                <option key={`${m.year}-${m.month}`} value={`${m.year}-${m.month}`} className="bg-slate-950 text-slate-300">
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-2">
            {/* Streak */}
            {(user?.streak_count ?? 0) > 0 && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-orange-500/10 border border-orange-500/20">
                <Flame className="w-3.5 h-3.5 text-orange-400" />
                <span className="text-xs font-semibold text-orange-300">{user?.streak_count} day{user?.streak_count !== 1 ? 's' : ''}</span>
              </div>
            )}

            {/* Mirror Me */}
            <button
              id="mirror-me-btn"
              onClick={() => router.push(`/mirror-me?month=${selectedMonth}&year=${selectedYear}`)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/5 transition-all"
            >
              <BarChart2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Mirror Me</span>
            </button>

            {/* Username */}
            <span className="text-xs text-slate-600 hidden sm:inline">{user?.username}</span>

            {/* Logout */}
            <button
              id="logout-btn"
              onClick={() => { logout(); router.push('/auth/login'); }}
              className="p-1.5 rounded-lg text-slate-600 hover:text-slate-400 hover:bg-white/5 transition-all"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* ── Messages ──────────────────────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">

          {/* Empty state */}
          {messages.length === 0 && historyLoaded && (
            <div className="flex flex-col items-center justify-center py-24 gap-6 animate-fadeIn">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20 border border-violet-500/20 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-violet-400" />
              </div>
              <div className="text-center max-w-sm">
                <h2 className="text-xl font-semibold text-white mb-2">
                  Hey{user?.username ? `, ${user.username}` : ''} 👋
                </h2>
                <p className="text-sm text-slate-500 leading-relaxed">
                  This is your private space. Tell me what's on your mind — how your day went, what you're feeling, or anything you want to explore.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {[
                  "I had a really rough day today...",
                  "Something is bothering me at work",
                  "I'm feeling excited about a new goal",
                  "I just need to talk",
                ].map(prompt => (
                  <button
                    key={prompt}
                    onClick={() => sendMessage(prompt)}
                    className="px-3 py-2 rounded-xl text-xs text-slate-400 border border-white/[0.07] hover:bg-white/5 hover:text-white transition-all"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message bubbles */}
          {(() => {
            let lastDateStr = "";
            return messages.map((msg) => {
              const msgDate = new Date(msg.timestamp);
              const dateStr = msgDate.toDateString();
              
              let showDivider = false;
              let dividerLabel = "";
              
              if (dateStr !== lastDateStr) {
                showDivider = true;
                dividerLabel = formatDateDivider(msg.timestamp);
                lastDateStr = dateStr;
              }
              
              return (
                <div key={msg.id} className="w-full flex flex-col">
                  {showDivider && dividerLabel && (
                    <div className="flex items-center justify-center my-6 text-white/20 text-xs select-none">
                      <span className="flex-1 border-t border-white/[0.05] max-w-[80px]"></span>
                      <span className="mx-4">{dividerLabel}</span>
                      <span className="flex-1 border-t border-white/[0.05] max-w-[80px]"></span>
                    </div>
                  )}
                  
                  <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
                    {msg.role === 'user' ? (
                      <div className="flex flex-col items-end max-w-[70%]">
                        <div className="bubble-user animate-fadeIn">{msg.content}</div>
                        <span className="text-xs text-white/25 mt-1 select-none pr-1">
                          {formatTime(msg.timestamp)}
                        </span>
                      </div>
                    ) : msg.content === '' && msg.isTyping ? (
                      <ThinkingIndicator />
                    ) : (
                      <AIBubble
                        msg={msg}
                        onReply={handleFollowupReply}
                      />
                    )}
                  </div>
                </div>
              );
            });
          })()}

          <div ref={bottomRef} />
        </div>
      </main>

      {/* ── Input bar (Active for current month, read-only archive for past months) ── */}
      <footer className="sticky bottom-0 z-40 border-t border-white/[0.05] bg-[#0f0f0f]/90 backdrop-blur-xl">
        {selectedMonth === new Date().getMonth() + 1 && selectedYear === new Date().getFullYear() ? (
          <div className="max-w-3xl mx-auto px-4 py-3">
            <div className="flex items-end gap-2 glass-panel border border-white/[0.08] rounded-2xl px-3 py-2 focus-within:border-violet-500/30 transition-colors">
              <textarea
                ref={textareaRef}
                id="chat-input"
                value={input}
                onChange={handleInputChange}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="What's on your mind..."
                rows={1}
                disabled={sending}
                className="flex-1 bg-transparent resize-none text-sm text-white placeholder-slate-600 outline-none leading-relaxed py-1 max-h-[180px] disabled:opacity-50"
              />
              <button
                id="send-btn"
                onClick={() => sendMessage()}
                disabled={!input.trim() || sending}
                className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 flex items-center justify-center transition-all active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed shadow-md shadow-violet-500/30"
              >
                {sending ? (
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                ) : (
                  <Send className="w-4 h-4 text-white" />
                )}
              </button>
            </div>
            <p className="text-center text-[10px] text-slate-700 mt-2">
              Press Enter to send · Shift+Enter for new line
            </p>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto px-4 py-6 text-center">
            <p className="text-xs text-slate-500 font-medium">
              Viewing archived conversations from {new Date(selectedYear, selectedMonth - 1).toLocaleString('default', { month: 'long', year: 'numeric' })}.
            </p>
            <button
              onClick={() => {
                const now = new Date();
                setSelectedMonth(now.getMonth() + 1);
                setSelectedYear(now.getFullYear());
                setHistoryLoaded(false);
              }}
              className="text-xs text-violet-400 hover:text-violet-300 font-semibold mt-1.5 transition-colors"
            >
              Back to current month to chat
            </button>
          </div>
        )}
      </footer>
    </div>
  );
}
