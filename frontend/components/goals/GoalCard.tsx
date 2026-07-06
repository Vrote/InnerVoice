import { Target, Calendar, Tag, Sparkles, CheckCircle2, Pause, XCircle } from 'lucide-react';

const STATUS_STYLES: Record<string, string> = {
  active:    'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  completed: 'text-violet-400 bg-violet-500/10 border-violet-500/20',
  paused:    'text-amber-400 bg-amber-500/10 border-amber-500/20',
  abandoned: 'text-slate-400 bg-slate-500/10 border-slate-500/20',
};

const STATUS_ICONS: Record<string, any> = {
  active: Target, completed: CheckCircle2, paused: Pause, abandoned: XCircle,
};

const TYPE_COLORS: Record<string, string> = {
  career: 'text-cyan-400', health: 'text-emerald-400', habit: 'text-amber-400',
  relationship: 'text-pink-400', learning: 'text-violet-400', personal: 'text-orange-400',
};

interface GoalCardProps {
  goal: {
    id: string;
    title: string;
    description: string | null;
    goal_type: string;
    status: string;
    progress_notes: any[];
    created_at: string;
    target_date: string | null;
    ai_suggested: boolean;
  };
  onStatusChange?: (id: string, status: string) => void;
}

export default function GoalCard({ goal, onStatusChange }: GoalCardProps) {
  const StatusIcon = STATUS_ICONS[goal.status] || Target;
  const statusStyle = STATUS_STYLES[goal.status] || STATUS_STYLES.active;
  const typeColor = TYPE_COLORS[goal.goal_type] || 'text-slate-400';
  const progressNotes = Array.isArray(goal.progress_notes) ? goal.progress_notes : [];

  return (
    <div className="glass-panel rounded-xl p-5 border border-white/5 hover:border-white/10 transition-all">
      <div className="flex items-start gap-3 mb-3">
        <div className={`w-8 h-8 rounded-lg border flex items-center justify-center shrink-0 ${statusStyle}`}>
          <StatusIcon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2 flex-wrap">
            <h3 className="text-sm font-semibold text-white leading-snug">{goal.title}</h3>
            {goal.ai_suggested && (
              <span className="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20">
                <Sparkles className="w-2.5 h-2.5" />AI
              </span>
            )}
          </div>
          {goal.description && (
            <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{goal.description}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 mb-3 flex-wrap">
        {goal.goal_type && (
          <span className={`flex items-center gap-1 text-xs ${typeColor}`}>
            <Tag className="w-3 h-3" />
            {goal.goal_type}
          </span>
        )}
        {goal.target_date && (
          <span className="flex items-center gap-1 text-xs text-slate-500">
            <Calendar className="w-3 h-3" />
            {goal.target_date}
          </span>
        )}
        <span className={`ml-auto text-xs px-2 py-0.5 rounded-full border ${statusStyle}`}>
          {goal.status}
        </span>
      </div>

      {progressNotes.length > 0 && (
        <div className="space-y-1 mb-3">
          {progressNotes.slice(-2).map((note: any, i: number) => (
            <p key={i} className="text-xs text-slate-500 pl-3 border-l border-violet-500/30">
              {typeof note === 'string' ? note : note.note || ''}
            </p>
          ))}
        </div>
      )}

      {onStatusChange && goal.status === 'active' && (
        <div className="flex gap-2 pt-2 border-t border-white/5">
          <button
            onClick={() => onStatusChange(goal.id, 'completed')}
            className="flex-1 py-1.5 rounded-lg text-xs text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 transition-all"
          >
            ✓ Mark Done
          </button>
          <button
            onClick={() => onStatusChange(goal.id, 'paused')}
            className="flex-1 py-1.5 rounded-lg text-xs text-amber-400 bg-amber-500/10 hover:bg-amber-500/20 transition-all"
          >
            ⏸ Pause
          </button>
        </div>
      )}
    </div>
  );
}
