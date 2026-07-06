'use client';
import { useEffect, useRef, useState } from 'react';
import { Sparkles } from 'lucide-react';

const EMOTION_COLORS: Record<string, string> = {
  happy: 'text-yellow-400',
  excited: 'text-orange-400',
  grateful: 'text-emerald-400',
  motivated: 'text-cyan-400',
  hopeful: 'text-sky-400',
  neutral: 'text-slate-400',
  confused: 'text-purple-400',
  nostalgic: 'text-violet-400',
  sad: 'text-blue-400',
  lonely: 'text-indigo-400',
  anxious: 'text-amber-400',
  overwhelmed: 'text-rose-400',
  angry: 'text-red-400',
  fearful: 'text-red-500',
  disappointed: 'text-orange-500',
  burnout: 'text-pink-500',
};

const EMOTION_EMOJIS: Record<string, string> = {
  happy: '😊', excited: '🚀', grateful: '🙏', motivated: '💪',
  hopeful: '🌱', neutral: '😶', confused: '🤔', nostalgic: '🕊️',
  sad: '💙', lonely: '🌙', anxious: '😰', overwhelmed: '😵',
  angry: '🔥', fearful: '😨', disappointed: '😔', burnout: '🪫',
};

interface AIResponseProps {
  response: string;
  emotion?: string | null;
  toolsUsed?: string[];
  plan?: string[];
}

export default function AIResponse({ response, emotion, toolsUsed = [], plan = [] }: AIResponseProps) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);
  const indexRef = useRef(0);

  useEffect(() => {
    setDisplayed('');
    setDone(false);
    indexRef.current = 0;

    const interval = setInterval(() => {
      if (indexRef.current < response.length) {
        setDisplayed(response.slice(0, indexRef.current + 1));
        indexRef.current += 1;
      } else {
        setDone(true);
        clearInterval(interval);
      }
    }, 18);

    return () => clearInterval(interval);
  }, [response]);

  const emotionColor = emotion ? (EMOTION_COLORS[emotion] || 'text-slate-400') : 'text-slate-400';
  const emotionEmoji = emotion ? (EMOTION_EMOJIS[emotion] || '✨') : '✨';

  return (
    <div className="glass-panel rounded-2xl p-6 border border-violet-500/20 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold text-violet-300">InnerVoice</p>
          {emotion && (
            <p className={`text-xs ${emotionColor}`}>
              {emotionEmoji} Detected: {emotion}
            </p>
          )}
        </div>
      </div>

      {/* Response text with typewriter */}
      <div className="text-slate-200 text-[15px] leading-relaxed whitespace-pre-wrap">
        {displayed}
        {!done && (
          <span className="inline-block w-0.5 h-4 bg-violet-400 ml-0.5 animate-pulse align-middle" />
        )}
      </div>

      {/* Tools used (visible once done) */}
      {done && toolsUsed.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <p className="text-xs text-slate-500 mb-2">Reasoning used:</p>
          <div className="flex flex-wrap gap-1.5">
            {toolsUsed.map((t) => (
              <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20">
                {t.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
