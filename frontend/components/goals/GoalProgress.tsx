interface GoalProgressProps {
  active: number;
  completed: number;
  paused: number;
}

export default function GoalProgress({ active, completed, paused }: GoalProgressProps) {
  const total = active + completed + paused;
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="glass-panel rounded-xl p-5 border border-white/5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">Goal Progress</h3>
        <span className="text-2xl font-bold text-violet-400">{pct}%</span>
      </div>
      <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-500">
        <span className="text-emerald-400">{active} active</span>
        <span className="text-violet-400">{completed} completed</span>
        <span className="text-amber-400">{paused} paused</span>
      </div>
    </div>
  );
}
