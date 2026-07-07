"use client"
import { useState, useEffect } from "react"

const STEPS = [
  { text: "Close your eyes if you can. Take one slow breath.", duration: 8 },
  { text: "Notice your feet and legs. Are they tense or relaxed?", duration: 8 },
  { text: "Move to your stomach. Is it tight? Let it soften.", duration: 8 },
  { text: "Your chest and shoulders. Where are you holding tension?", duration: 8 },
  { text: "Your jaw, your face. Let everything loosen slightly.", duration: 8 },
  { text: "Your whole body, right now. You're here. That's enough.", duration: 8 },
  { text: "Take one more slow breath. You did it.", duration: 8 }
]

export default function BodyScan() {
  const [step, setStep] = useState(-1) // -1 = not started
  const [timer, setTimer] = useState(0)
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (step < 0 || done) return
    setTimer(STEPS[step].duration)
    const interval = setInterval(() => {
      setTimer(t => {
        if (t <= 1) {
          clearInterval(interval)
          if (step + 1 >= STEPS.length) setDone(true)
          else setStep(s => s + 1)
          return 0
        }
        return t - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [step, done])

  if (done) return (
    <div className="text-center py-3">
      <p className="text-white/70 text-sm">You just checked in with yourself 💜</p>
      <p className="text-white/40 text-xs mt-1">That's harder than it sounds.</p>
    </div>
  )

  if (step < 0) return (
    <div className="text-center py-2">
      <p className="text-white/50 text-xs mb-2">
        60 seconds. Follow the text at your own pace.
      </p>
      <p className="text-purple-300/70 text-[11px] mb-4 leading-relaxed max-w-sm mx-auto">
        💡 <strong>Benefit:</strong> Relinks body and mind, helps release stored physical tension, and grounds your thoughts when feeling angry or burnt out.
      </p>
      <button
        onClick={() => setStep(0)}
        className="px-4 py-2 rounded-lg bg-purple-600/70 hover:bg-purple-600 text-white font-medium text-xs transition-colors"
      >
        Begin
      </button>
    </div>
  )

  const current = STEPS[step]
  const progress = ((step) / STEPS.length) * 100

  return (
    <div className="flex flex-col gap-3 py-2">
      {/* Progress bar */}
      <div className="w-full h-0.5 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-purple-500/60 transition-all duration-1000"
          style={{ width: `${progress}%` }}
        />
      </div>
      {/* Instruction */}
      <p className="text-white/75 text-sm leading-relaxed min-h-[3rem]">
        {current.text}
      </p>
      {/* Timer */}
      <p className="text-white/25 text-xs text-right">{timer}s</p>
    </div>
  )
}
