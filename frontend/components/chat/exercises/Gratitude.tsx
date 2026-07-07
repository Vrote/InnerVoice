"use client"
import { useState } from "react"

const PROMPTS = [
  "Something small that went okay today...",
  "Someone who has shown up for you recently...",
  "Something about yourself you can acknowledge right now...",
]

export default function Gratitude() {
  const [values, setValues] = useState(["", "", ""])
  const [done, setDone] = useState(false)

  if (done) return (
    <div className="py-3 text-center">
      <p className="text-white/70 text-sm">That took courage 💜</p>
      <p className="text-white/40 text-xs mt-1">
        Even when things are hard, something small is always there.
      </p>
    </div>
  )

  return (
    <div className="flex flex-col gap-3">
      <p className="text-purple-300/70 text-[11px] mb-1 leading-relaxed">
        💡 <strong>Benefit:</strong> Shunts focus away from negative loops, builds emotional resilience, and rewires the brain to notice support and positive elements.
      </p>
      {PROMPTS.map((prompt, i) => (
        <div key={i}>
          <p className="text-white/40 text-xs mb-1">{i + 1}. {prompt}</p>
          <input
            type="text"
            value={values[i]}
            onChange={e => setValues(v => { const n = [...v]; n[i] = e.target.value; return n; })}
            placeholder="Write anything..."
            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-white/20 focus:border-purple-500/50 outline-none"
          />
        </div>
      ))}
      <button
        onClick={() => setDone(true)}
        disabled={values.every(v => v.trim() === "")}
        className="mt-1 px-3 py-2 rounded-lg bg-purple-600/70 hover:bg-purple-600 text-white font-medium text-xs disabled:opacity-40 disabled:hover:bg-purple-600/70 transition-colors"
      >
        Done
      </button>
    </div>
  )
}
