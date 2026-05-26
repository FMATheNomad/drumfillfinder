import { useEffect, useRef, useCallback, useState } from "react"
import WaveSurfer from "wavesurfer.js"

interface Hit {
  time: number
  label: string
}

interface Props {
  audioUrl: string
  hits: Hit[]
}

const LABEL_COLORS: Record<string, string> = {
  kick: "#ef4444",
  snare: "#22c55e",
  "hi-hat": "#3b82f6",
}

export default function WaveformViewer({ audioUrl, hits }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const wavesurferRef = useRef<WaveSurfer | null>(null)
  const [playing, setPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  useEffect(() => {
    if (!containerRef.current) return

    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "#4a4a6a",
      progressColor: "#e94560",
      cursorColor: "#e94560",
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      height: 120,
      normalize: true,
      backend: "WebAudio",
    })

    ws.load(audioUrl)

    ws.on("ready", () => {
      setDuration(ws.getDuration())
    })

    ws.on("timeupdate", (time) => {
      setCurrentTime(time)
    })

    ws.on("play", () => setPlaying(true))
    ws.on("pause", () => setPlaying(false))

    wavesurferRef.current = ws

    return () => {
      ws.destroy()
      wavesurferRef.current = null
    }
  }, [audioUrl])

  const togglePlay = useCallback(() => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause()
    }
  }, [])

  const formatTime = (t: number) => {
    const m = Math.floor(t / 60)
    const s = Math.floor(t % 60)
    return `${m}:${s.toString().padStart(2, "0")}`
  }

  return (
    <div className="space-y-3">
      <div ref={containerRef} className="w-full" />

      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={togglePlay}
            className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
          >
            {playing ? "⏸" : "▶"}
          </button>
          <span className="text-sm text-[var(--text-secondary)] tabular-nums">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs">
          {Object.entries(LABEL_COLORS).map(([label, color]) => (
            <span key={label} className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
              {label}
            </span>
          ))}
        </div>
      </div>

      {hits.length > 0 && duration > 0 && (
        <div className="relative w-full h-2 bg-white/5 rounded-full overflow-hidden">
          {hits.map((h, i) => (
            <div
              key={i}
              className="absolute top-0 h-full w-0.5 rounded-full"
              style={{
                left: `${(h.time / duration) * 100}%`,
                backgroundColor: LABEL_COLORS[h.label] || "#888",
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
