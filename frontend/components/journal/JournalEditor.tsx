'use client';
import { useEffect, useState, useRef } from 'react';
import { Send, Mic, Loader2 } from 'lucide-react';

interface JournalEditorProps {
  onSubmit: (content: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

const PLACEHOLDERS = [
  "What's on your mind today?",
  "How are you feeling right now?",
  "What happened today that you want to remember?",
  "Something you're grateful for, worried about, or thinking through...",
];

export default function JournalEditor({ onSubmit, isLoading = false, disabled = false }: JournalEditorProps) {
  const [content, setContent] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const [placeholder] = useState(() => PLACEHOLDERS[Math.floor(Math.random() * PLACEHOLDERS.length)]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const words = content.trim().split(/\s+/).filter(Boolean).length;
    setWordCount(words);
  }, [content]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 400)}px`;
    }
  }, [content]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || isLoading || disabled) return;
    onSubmit(content.trim());
    setContent('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel rounded-2xl border border-white/10 overflow-hidden">
      {/* Textarea */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading || disabled}
          rows={5}
          className="w-full bg-transparent resize-none text-white placeholder-slate-600 text-[15px] leading-relaxed p-6 outline-none transition-all disabled:opacity-50 min-h-[140px]"
          style={{ height: 'auto' }}
        />
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between px-6 py-3 border-t border-white/5">
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-600">{wordCount} words</span>
          {wordCount > 0 && (
            <span className="text-xs text-slate-600">· Ctrl+Enter to submit</span>
          )}
        </div>
        <button
          type="submit"
          disabled={!content.trim() || isLoading || disabled}
          className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg shadow-violet-500/20 hover:shadow-violet-500/30 active:scale-95"
        >
          {isLoading ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</>
          ) : (
            <><Send className="w-4 h-4" /> Send to InnerVoice</>
          )}
        </button>
      </div>
    </form>
  );
}
