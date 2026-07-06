import { Mic2, BarChart3, Globe, MessageSquareText } from 'lucide-react';

interface VoiceProfileData {
  avg_sentence_length: number;
  formality_score: number;
  hinglish_ratio: number;
  uses_english_only: boolean;
  detected_languages: string;
  dominant_tone: string;
  vocabulary_richness: number;
  signature_words: string;
  style_summary: string;
  entries_analyzed: number;
  uses_emoji: boolean;
  uses_ellipsis: boolean;
  exclamation_ratio: number;
}

export default function VoiceProfileCard({ profile }: { profile: VoiceProfileData }) {
  let sigWords: string[] = [];
  try { sigWords = JSON.parse(profile.signature_words || '[]'); } catch {}

  const formalityLabel = profile.formality_score < 0.3 ? 'Casual' :
    profile.formality_score < 0.6 ? 'Balanced' : 'Formal';

  return (
    <div className="space-y-4">
      {/* Style summary */}
      <div className="glass-panel rounded-2xl p-6 border border-violet-500/20">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <Mic2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">Your Voice Fingerprint</h3>
            <p className="text-xs text-slate-500">{profile.entries_analyzed} entries analyzed</p>
          </div>
        </div>
        {profile.style_summary ? (
          <p className="text-sm text-slate-300 leading-relaxed">{profile.style_summary}</p>
        ) : (
          <p className="text-sm text-slate-500">Write more entries to see your voice analysis.</p>
        )}
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="glass-panel rounded-xl p-4 border border-white/5">
          <p className="text-xs text-slate-500 mb-1">Dominant Tone</p>
          <p className="text-lg font-bold text-white capitalize">{profile.dominant_tone || '—'}</p>
        </div>
        <div className="glass-panel rounded-xl p-4 border border-white/5">
          <p className="text-xs text-slate-500 mb-1">Formality</p>
          <p className="text-lg font-bold text-white">{formalityLabel}</p>
        </div>
        <div className="glass-panel rounded-xl p-4 border border-white/5">
          <p className="text-xs text-slate-500 mb-1">Avg Sentence</p>
          <p className="text-lg font-bold text-white">{profile.avg_sentence_length?.toFixed(0) || 0} words</p>
        </div>
        <div className="glass-panel rounded-xl p-4 border border-white/5">
          <p className="text-xs text-slate-500 mb-1">Vocab Richness</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-white/10 rounded-full">
              <div
                className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full"
                style={{ width: `${(profile.vocabulary_richness || 0) * 100}%` }}
              />
            </div>
            <span className="text-xs text-violet-400">{Math.round((profile.vocabulary_richness || 0) * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Language */}
      <div className="glass-panel rounded-xl p-4 border border-white/5">
        <div className="flex items-center gap-2 mb-2">
          <Globe className="w-4 h-4 text-cyan-400" />
          <p className="text-sm font-semibold text-white">Languages</p>
        </div>
        <p className="text-sm text-slate-400">{profile.detected_languages || 'English'}</p>
        {profile.hinglish_ratio > 0.05 && (
          <div className="mt-2 flex items-center gap-2">
            <div className="flex-1 h-1 bg-white/5 rounded-full">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
                style={{ width: `${profile.hinglish_ratio * 100}%` }}
              />
            </div>
            <span className="text-xs text-amber-400">{Math.round(profile.hinglish_ratio * 100)}% Hinglish</span>
          </div>
        )}
      </div>

      {/* Habits */}
      <div className="glass-panel rounded-xl p-4 border border-white/5">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-4 h-4 text-violet-400" />
          <p className="text-sm font-semibold text-white">Writing Habits</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {profile.uses_emoji && <Tag label="Uses emoji 😊" />}
          {profile.uses_ellipsis && <Tag label="Uses ellipsis..." />}
          {profile.exclamation_ratio > 0.05 && <Tag label="Expressive!" />}
        </div>
      </div>

      {/* Signature words */}
      {sigWords.length > 0 && (
        <div className="glass-panel rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquareText className="w-4 h-4 text-pink-400" />
            <p className="text-sm font-semibold text-white">Signature Words</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {sigWords.map((w, i) => (
              <span key={i} className="px-3 py-1 rounded-full text-xs text-pink-300 bg-pink-500/10 border border-pink-500/20">
                {w}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Tag({ label }: { label: string }) {
  return (
    <span className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-slate-400 border border-white/10">
      {label}
    </span>
  );
}
