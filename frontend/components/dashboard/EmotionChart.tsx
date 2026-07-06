'use client';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts';

interface EmotionPoint {
  date: string;
  mood_score: number;
  primary_emotion: string;
}

const EMOTION_EMOJIS: Record<string, string> = {
  happy: '😊', excited: '🚀', grateful: '🙏', motivated: '💪',
  hopeful: '🌱', neutral: '😶', confused: '🤔', nostalgic: '🕊️',
  sad: '💙', lonely: '🌙', anxious: '😰', overwhelmed: '😵',
  angry: '🔥', fearful: '😨', disappointed: '😔', burnout: '🪫',
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    const emoji = EMOTION_EMOJIS[d.primary_emotion] || '✨';
    return (
      <div className="glass-panel rounded-xl px-4 py-3 border border-white/10 text-sm">
        <p className="text-slate-400 text-xs mb-1">{label}</p>
        <p className="text-white font-semibold">{emoji} {d.primary_emotion}</p>
        <p className="text-violet-300">Mood: {d.mood_score?.toFixed(1)}/10</p>
      </div>
    );
  }
  return null;
};

export default function EmotionChart({ data }: { data: EmotionPoint[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
        No emotion data yet. Start journaling!
      </div>
    );
  }

  const chartData = data.map((d) => ({
    ...d,
    date: d.date?.slice(5),  // MM-DD
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="moodGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="date"
          tick={{ fill: '#64748b', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[0, 10]}
          tick={{ fill: '#64748b', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area
          type="monotone"
          dataKey="mood_score"
          stroke="#7c3aed"
          strokeWidth={2}
          fill="url(#moodGradient)"
          dot={{ fill: '#7c3aed', strokeWidth: 0, r: 4 }}
          activeDot={{ fill: '#a78bfa', r: 6, strokeWidth: 0 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
