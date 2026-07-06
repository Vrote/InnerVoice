import { Flame, Trophy, BookOpen } from 'lucide-react';

interface StreakCardProps {
  streak: number;
  longestStreak: number;
  totalEntries: number;
}

export default function StreakCard({ streak, longestStreak, totalEntries }: StreakCardProps) {
  return (
    <div className="grid grid-cols-3 gap-3">
      <div className="glass-panel rounded-xl p-4 text-center border border-orange-500/20">
        <div className="w-9 h-9 rounded-xl bg-orange-500/15 flex items-center justify-center mx-auto mb-2">
          <Flame className="w-5 h-5 text-orange-400" />
        </div>
        <p className="text-2xl font-bold text-white">{streak}</p>
        <p className="text-xs text-slate-500 mt-0.5">Day streak</p>
      </div>
      <div className="glass-panel rounded-xl p-4 text-center border border-violet-500/20">
        <div className="w-9 h-9 rounded-xl bg-violet-500/15 flex items-center justify-center mx-auto mb-2">
          <Trophy className="w-5 h-5 text-violet-400" />
        </div>
        <p className="text-2xl font-bold text-white">{longestStreak}</p>
        <p className="text-xs text-slate-500 mt-0.5">Best streak</p>
      </div>
      <div className="glass-panel rounded-xl p-4 text-center border border-emerald-500/20">
        <div className="w-9 h-9 rounded-xl bg-emerald-500/15 flex items-center justify-center mx-auto mb-2">
          <BookOpen className="w-5 h-5 text-emerald-400" />
        </div>
        <p className="text-2xl font-bold text-white">{totalEntries}</p>
        <p className="text-xs text-slate-500 mt-0.5">Total entries</p>
      </div>
    </div>
  );
}
