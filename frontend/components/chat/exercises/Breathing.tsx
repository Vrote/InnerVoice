"use client"
import { useState, useEffect } from "react"

const PACINGS = {
  standard: [
    { label: "Breathe in", duration: 4, scale: 1.4, color: "#7c6af7" },
    { label: "Hold", duration: 7, scale: 1.4, color: "#a78bfa" },
    { label: "Breathe out", duration: 8, scale: 0.85, color: "#6d6af0" },
  ],
  gentle: [
    { label: "Breathe in", duration: 2, scale: 1.4, color: "#7c6af7" },
    { label: "Hold", duration: 3, scale: 1.4, color: "#a78bfa" },
    { label: "Breathe out", duration: 4, scale: 0.85, color: "#6d6af0" },
  ]
}
const TOTAL_ROUNDS = 3

export default function Breathing() {
  const [pacing, setPacing] = useState<'standard' | 'gentle'>('standard')
  const [phase, setPhase] = useState(0)
  const [count, setCount] = useState(4)
  const [round, setRound] = useState(1)
  const [done, setDone] = useState(false)
  const [started, setStarted] = useState(false)

  const phases = PACINGS[pacing]

  // Update initial count when pacing changes (before starting)
  useEffect(() => {
    if (!started) {
      setCount(PACINGS[pacing][0].duration)
    }
  }, [pacing, started])

  // Countdown timer effect
  useEffect(() => {
    if (!started || done) return

    const timer = setInterval(() => {
      setCount(prev => prev - 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [started, done])

  // Phase transition effect
  useEffect(() => {
    if (!started || done) return

    if (count <= 0) {
      const nextPhase = (phase + 1) % phases.length
      if (nextPhase === 0) {
        if (round >= TOTAL_ROUNDS) {
          setDone(true)
          return
        }
        setRound(r => r + 1)
      }
      setPhase(nextPhase)
      setCount(phases[nextPhase].duration)
    }
  }, [count, phase, round, started, done, phases])

  const current = phases[phase]

  if (done) return (
    <div className="text-center py-4">
      <p className="text-white/70 text-sm">Well done 💜</p>
      <p className="text-white/40 text-xs mt-1">3 rounds complete. How do you feel?</p>
    </div>
  )

  if (!started) return (
    <div className="text-center py-2">
      <p className="text-white/50 text-xs mb-3">Select breathing speed:</p>
      
      {/* Pacing Toggle Buttons */}
      <div className="flex justify-center gap-2 mb-4">
        <button
          onClick={() => setPacing('standard')}
          className={`px-3 py-1.5 rounded-lg text-[10px] font-semibold transition-colors ${
            pacing === 'standard'
              ? 'bg-purple-600 text-white'
              : 'bg-white/5 text-white/50 hover:bg-white/10'
          }`}
        >
          Deep (4-7-8s)
        </button>
        <button
          onClick={() => setPacing('gentle')}
          className={`px-3 py-1.5 rounded-lg text-[10px] font-semibold transition-colors ${
            pacing === 'gentle'
              ? 'bg-purple-600 text-white'
              : 'bg-white/5 text-white/50 hover:bg-white/10'
          }`}
        >
          Gentle/Faster (2-3-4s)
        </button>
      </div>

      <p className="text-purple-300/70 text-[11px] mb-4 leading-relaxed max-w-sm mx-auto">
        {pacing === 'standard' 
          ? "💡 Benefit: Activates the parasympathetic nervous system, lowers heart rate, and triggers deep physical calm."
          : "💡 Benefit: Shorter, lighter counts that calm your breathing path without strain if you are short of breath."
        }
      </p>
      
      <button
        onClick={() => setStarted(true)}
        className="px-6 py-2 rounded-lg bg-purple-600/75 hover:bg-purple-600 text-white font-medium text-xs transition-colors"
      >
        Start
      </button>
    </div>
  )

  return (
    <div className="flex flex-col items-center py-3 gap-4">
      {/* Animated circle */}
      <div className="relative flex items-center justify-center">
        <div
          className="rounded-full transition-all"
          style={{
            width: 80, height: 80,
            backgroundColor: current.color + "33",
            border: `2px solid ${current.color}66`,
            transform: `scale(${current.scale})`,
            transition: `transform ${current.duration * 0.9}s ease-in-out`,
            boxShadow: `0 0 20px ${current.color}44`,
          }}
        />
        <span className="absolute text-2xl font-light text-white/80">{count}</span>
      </div>
      {/* Phase label */}
      <div className="text-center">
        <p className="text-white/80 text-sm font-medium">{current.label}</p>
        <p className="text-white/30 text-xs mt-0.5">Round {round} of {TOTAL_ROUNDS} ({pacing === 'standard' ? 'Deep' : 'Gentle'})</p>
      </div>
    </div>
  )
}
