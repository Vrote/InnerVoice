import { Calendar, TrendingUp, Star, AlertCircle } from 'lucide-react';

interface WeeklySummaryProps {
  summary: {
    summary_text: string;
    most_common_emotion: string;
    most_positive_day: string;
    most_stressful_day: string;
    biggest_achievement: string;
    average_mood_score: number;
    entries_count: number;
    week_start: string;
    week_end: string;
  } | null;
}

export default function WeeklySummary({ summary }: WeeklySummaryProps) {
  if (!summary) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-white/5">
        <div className="flex items-center gap-3 mb-3">
          <Calendar className="w-5 h-5 text-violet-400" />
          <h3 className="text-base font-semibold text-white">This Week</h3>
        </div>
        <p className="text-sm text-slate-500">
          Keep journaling — your weekly summary will appear after a few entries this week.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-6 border border-white/5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Calendar className="w-5 h-5 text-violet-400" />
          <h3 className="text-base font-semibold text-white">This Week</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">{summary.entries_count} entries</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-violet-500/15 text-violet-300">
            avg {summary.average_mood_score?.toFixed(1)}/10
          </span>
        </div>
      </div>

      <p className="text-sm text-slate-300 leading-relaxed mb-4">{summary.summary_text}</p>

      <div className="grid grid-cols-2 gap-3">
        {summary.most_positive_day && (
          <div className="flex items-center gap-2 bg-emerald-500/10 rounded-xl px-3 py-2">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            <div>
              <p className="text-xs text-emerald-400">Best day</p>
              <p className="text-xs text-slate-300">{summary.most_positive_day}</p>
            </div>
          </div>
        )}
        {summary.biggest_achievement && (
          <div className="flex items-center gap-2 bg-violet-500/10 rounded-xl px-3 py-2">
            <Star className="w-3.5 h-3.5 text-violet-400" />
            <div>
              <p className="text-xs text-violet-400">Achievement</p>
              <p className="text-xs text-slate-300 truncate">{summary.biggest_achievement}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
