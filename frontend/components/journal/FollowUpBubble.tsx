'use client';
import { useState } from 'react';
import { MessageCircle, Send } from 'lucide-react';

interface FollowUpBubbleProps {
  question: string;
  onSubmit: (answer: string) => void;
  isLoading?: boolean;
}

export default function FollowUpBubble({ question, onSubmit, isLoading = false }: FollowUpBubbleProps) {
  const [answer, setAnswer] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || isLoading) return;
    onSubmit(answer.trim());
    setAnswer('');
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-amber-500/20 animate-fadeIn">
      {/* Question bubble */}
      <div className="flex items-start gap-3 mb-5">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shrink-0 mt-0.5">
          <MessageCircle className="w-4 h-4 text-white" />
        </div>
        <div className="flex-1">
          <p className="text-xs text-amber-400 font-semibold mb-1.5">InnerVoice has a question</p>
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
            <p className="text-slate-200 text-sm leading-relaxed">{question}</p>
          </div>
        </div>
      </div>

      {/* Reply form */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your reply..."
          disabled={isLoading}
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20 transition-all disabled:opacity-50"
          autoFocus
        />
        <button
          type="submit"
          disabled={!answer.trim() || isLoading}
          className="w-10 h-10 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-all shrink-0"
        >
          <Send className="w-4 h-4 text-white" />
        </button>
      </form>
    </div>
  );
}
