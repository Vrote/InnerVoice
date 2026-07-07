"use client"
import { useState } from "react"
import Breathing from "./exercises/Breathing"
import Gratitude from "./exercises/Gratitude"
import BodyScan from "./exercises/BodyScan"

interface CopingSuggestion {
  show: boolean
  emotion?: string
  exercise_type?: "breathing" | "gratitude" | "bodyscan"
  title?: string
  subtitle?: string
}

export default function CopingToolkit({ suggestion }: { suggestion: CopingSuggestion }) {
  const [open, setOpen] = useState(false)
  const [dismissed, setDismissed] = useState(false)

  if (!suggestion?.show || dismissed) return null

  return (
    <div className="mt-3 rounded-xl border border-white/10 bg-white/5 p-4 max-w-md w-full">
      {!open ? (
        // The suggestion card
        <div>
          <p className="text-xs text-white/40 mb-1">Want to try something?</p>
          <p className="text-sm text-white/80 font-medium">{suggestion.title}</p>
          <p className="text-xs text-white/50 mt-0.5 mb-3">{suggestion.subtitle}</p>
          <div className="flex gap-2">
            <button
              onClick={() => setOpen(true)}
              className="text-xs px-3 py-1.5 rounded-lg bg-purple-600/70 hover:bg-purple-600 text-white font-medium transition-colors"
            >
              Try it
            </button>
            <button
              onClick={() => setDismissed(true)}
              className="text-xs px-3 py-1.5 rounded-lg text-white/30 hover:text-white/60 font-medium transition-colors"
            >
              Not now
            </button>
          </div>
        </div>
      ) : (
        // The exercise
        <div>
          <div className="flex justify-between items-center mb-3">
            <p className="text-sm text-white/70 font-medium">{suggestion.title}</p>
            <button
              onClick={() => { setOpen(false); setDismissed(true) }}
              className="text-white/30 hover:text-white/60 text-xs"
            >
              ✕ close
            </button>
          </div>
          {suggestion.exercise_type === "breathing" && <Breathing />}
          {suggestion.exercise_type === "gratitude" && <Gratitude />}
          {suggestion.exercise_type === "bodyscan" && <BodyScan />}
        </div>
      )}
    </div>
  )
}
