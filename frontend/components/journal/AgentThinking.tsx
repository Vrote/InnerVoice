'use client';
import { useEffect, useState } from 'react';
import { Brain, Zap, CheckCircle2 } from 'lucide-react';

const THINKING_STAGES = [
  { icon: '🔍', text: 'Reading your entry...' },
  { icon: '💭', text: 'Understanding your context...' },
  { icon: '🧠', text: 'Reasoning about what you need...' },
  { icon: '🛠️', text: 'Gathering relevant memories...' },
  { icon: '✨', text: 'Crafting your response...' },
];

interface AgentThinkingProps {
  plan?: string[];
}

export default function AgentThinking({ plan = [] }: AgentThinkingProps) {
  const [stageIndex, setStageIndex] = useState(0);
  const [dots, setDots] = useState('');

  useEffect(() => {
    const stageTimer = setInterval(() => {
      setStageIndex((i) => (i + 1) % THINKING_STAGES.length);
    }, 2200);
    return () => clearInterval(stageTimer);
  }, []);

  useEffect(() => {
    const dotsTimer = setInterval(() => {
      setDots((d) => (d.length >= 3 ? '' : d + '.'));
    }, 400);
    return () => clearInterval(dotsTimer);
  }, []);

  const stage = THINKING_STAGES[stageIndex];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-indigo-500/20 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center animate-pulse">
          <Brain className="w-4 h-4 text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold text-indigo-300">InnerVoice is thinking{dots}</p>
          <p className="text-xs text-slate-500">Agentic reasoning loop active</p>
        </div>
      </div>

      {/* Current stage */}
      <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 mb-4">
        <span className="text-xl">{stage.icon}</span>
        <p className="text-sm text-indigo-200">{stage.text}</p>
        <Zap className="w-3 h-3 text-indigo-400 ml-auto animate-pulse" />
      </div>

      {/* Plan steps (if available) */}
      {plan.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs text-slate-500 mb-2">Execution plan:</p>
          {plan.map((step, i) => (
            <div key={i} className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-violet-500/50" />
              <span className="text-xs text-slate-500">{step.replace(/_/g, ' ')}</span>
            </div>
          ))}
        </div>
      )}

      {/* Pulsing bars */}
      <div className="flex gap-1 mt-4">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="flex-1 h-1 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 animate-pulse"
            style={{ animationDelay: `${i * 150}ms`, opacity: 0.3 + i * 0.15 }}
          />
        ))}
      </div>
    </div>
  );
}
