import InsightCard from './InsightCard';
import { Brain } from 'lucide-react';

interface MirrorMeReportProps {
  report: any;
  month: number;
  year: number;
}

const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

export default function MirrorMeReport({ report, month, year }: MirrorMeReportProps) {
  if (!report) return null;

  const rd = typeof report === 'string' ? JSON.parse(report) : report;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 border border-violet-500/20 text-center">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center mx-auto mb-4">
          <Brain className="w-7 h-7 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-1">{MONTH_NAMES[month - 1]} {year}</h2>
        <p className="text-slate-400 text-sm">Your monthly self-portrait</p>
      </div>

      {/* Narrative */}
      {rd.narrative && (
        <div className="glass-panel rounded-2xl p-6 border border-white/5">
          <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{rd.narrative}</p>
        </div>
      )}

      {/* Key insights */}
      {rd.key_insights && rd.key_insights.length > 0 && (
        <div>
          <h3 className="text-base font-semibold text-white mb-3">Key Insights</h3>
          <div className="grid gap-3">
            {rd.key_insights.map((insight: any, i: number) => (
              <InsightCard
                key={i}
                title={insight.title || `Insight ${i + 1}`}
                content={insight.description || insight}
                type={insight.type || 'insight'}
                emoji={insight.emoji}
              />
            ))}
          </div>
        </div>
      )}

      {/* Emotion summary */}
      {rd.emotion_summary && (
        <div>
          <h3 className="text-base font-semibold text-white mb-3">Emotional Landscape</h3>
          <div className="glass-panel rounded-xl p-5 border border-white/5">
            <p className="text-sm text-slate-300">{rd.emotion_summary}</p>
          </div>
        </div>
      )}

      {/* Top words / signature phrases */}
      {rd.signature_phrases && rd.signature_phrases.length > 0 && (
        <div>
          <h3 className="text-base font-semibold text-white mb-3">Your Signature Words</h3>
          <div className="flex flex-wrap gap-2">
            {rd.signature_phrases.map((w: string, i: number) => (
              <span
                key={i}
                className="px-3 py-1.5 rounded-full text-sm text-violet-300 bg-violet-500/10 border border-violet-500/20"
                style={{ fontSize: `${Math.max(12, 14 - i)}px` }}
              >
                {w}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Growth areas */}
      {rd.growth_areas && rd.growth_areas.length > 0 && (
        <div>
          <h3 className="text-base font-semibold text-white mb-3">Growth Areas</h3>
          <div className="grid gap-3">
            {rd.growth_areas.map((area: any, i: number) => (
              <InsightCard
                key={i}
                title={area.title || area}
                content={area.description || ''}
                type="growth"
                emoji="🌱"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
