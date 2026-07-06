import { Lightbulb } from 'lucide-react';

interface InsightCardProps {
  title: string;
  content: string;
  type?: 'insight' | 'pattern' | 'growth' | 'highlight';
  emoji?: string;
}

const TYPE_STYLES: Record<string, { border: string; bg: string; icon: string }> = {
  insight:   { border: 'border-violet-500/20', bg: 'bg-violet-500/5',  icon: 'text-violet-400' },
  pattern:   { border: 'border-cyan-500/20',   bg: 'bg-cyan-500/5',    icon: 'text-cyan-400' },
  growth:    { border: 'border-emerald-500/20', bg: 'bg-emerald-500/5', icon: 'text-emerald-400' },
  highlight: { border: 'border-amber-500/20',  bg: 'bg-amber-500/5',   icon: 'text-amber-400' },
};

export default function InsightCard({ title, content, type = 'insight', emoji }: InsightCardProps) {
  const styles = TYPE_STYLES[type];
  return (
    <div className={`rounded-xl p-4 border ${styles.border} ${styles.bg}`}>
      <div className="flex items-center gap-2 mb-2">
        {emoji ? (
          <span className="text-lg">{emoji}</span>
        ) : (
          <Lightbulb className={`w-4 h-4 ${styles.icon}`} />
        )}
        <h4 className="text-sm font-semibold text-white">{title}</h4>
      </div>
      <p className="text-sm text-slate-400 leading-relaxed">{content}</p>
    </div>
  );
}
