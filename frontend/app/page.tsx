"use client"

import { useState, useCallback } from "react"
import Uploader from "./components/Uploader"
import WaveformViewer from "./components/WaveformViewer"
import DrumHitsOverlay from "./components/DrumHitsOverlay"

interface Hit {
  time: number
  label: string
}

export default function Home() {
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<string>("")
  const [progress, setProgress] = useState(0)
  const [hits, setHits] = useState<Hit[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState("")

  const reset = useCallback(() => {
    setError(null)
    setHits([])
    setTaskId(null)
    setStatus("")
    setProgress(0)
  }, [])

  const handleFileSelect = useCallback((file: File) => {
    reset()
    setAudioFile(file)
    setAudioUrl(URL.createObjectURL(file))
  }, [reset])

  const handleUpload = useCallback(async () => {
    if (!audioFile) return
    setLoading(true)
    setError(null)
    setStatus("Mengupload...")

    try {
      const form = new FormData()
      form.append("file", audioFile)
      const res = await fetch("/api/upload", { method: "POST", body: form })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setTaskId(data.task_id)
      setStatus("Memproses")
      setProgress(5)
      pollStatus(data.task_id)
    } catch (e: any) {
      setError(e.message || "Upload gagal")
      setStatus("")
      setProgress(0)
      setLoading(false)
    }
  }, [audioFile])

  const handleYoutube = useCallback(async () => {
    if (!youtubeUrl.trim()) return
    reset()
    setStatus("Mendownload dari YouTube")
    setProgress(3)
    setLoading(true)

    try {
      const res = await fetch("/api/youtube", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: youtubeUrl.trim() }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setTaskId(data.task_id)
      setStatus("Memproses")
      setProgress(5)
      pollStatus(data.task_id)
    } catch (e: any) {
      setError(e.message || "Gagal")
      setStatus("")
      setProgress(0)
      setLoading(false)
    }
  }, [youtubeUrl, reset])

  const pollStatus = useCallback(async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${id}`)
        if (!res.ok) { clearInterval(interval); return }
        const data = await res.json()
        setProgress(data.progress)
        if (data.status === "SUCCESS") {
          clearInterval(interval)
          setProgress(100)
          setStatus("Selesai!")
          fetchResult(id)
        } else if (data.status === "FAILURE") {
          clearInterval(interval)
          setStatus("Gagal")
          setProgress(0)
          setError(data.error_message || "Proses gagal")
          setLoading(false)
        }
      } catch { clearInterval(interval) }
    }, 2000)
  }, [])

  const fetchResult = useCallback(async (id: string) => {
    try {
      const res = await fetch(`/api/result/${id}`)
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setHits(data.hits || [])
    } catch (e: any) {
      setError(e.message || "Gagal mengambil hasil")
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-8">
      <header className="w-full max-w-4xl flex items-center gap-3 mb-10">
        <img src="/logo.png" alt="Drumfillfinder" className="h-10 w-10" />
        <h1 className="text-2xl font-bold tracking-tight">Drumfillfinder</h1>
      </header>

      <div className="w-full max-w-4xl space-y-8">
        <Uploader
          onFileSelect={handleFileSelect}
          onUpload={handleUpload}
          loading={loading}
          error={error}
          hasFile={!!audioFile}
        />

        <div className="relative flex items-center gap-4">
          <div className="flex-1 border-t border-white/10" />
          <span className="text-xs text-[var(--text-secondary)]">atau</span>
          <div className="flex-1 border-t border-white/10" />
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=..."
            className="flex-1 px-4 py-2.5 rounded-xl bg-[var(--bg-card)] border border-white/10 text-sm
              focus:outline-none focus:border-[var(--accent)] transition-colors"
            onKeyDown={(e) => e.key === "Enter" && handleYoutube()}
          />
          <button
            onClick={handleYoutube}
            disabled={loading || !youtubeUrl.trim()}
            className="px-5 py-2.5 rounded-xl bg-[var(--accent)] text-white font-medium text-sm
              hover:opacity-90 disabled:opacity-50 transition-opacity shrink-0"
          >
            Proses
          </button>
        </div>

        {audioUrl && (
          <div className="relative bg-[var(--bg-card)] rounded-2xl p-4 border border-white/5">
            <WaveformViewer audioUrl={audioUrl} hits={hits} />
            {hits.length > 0 && <DrumHitsOverlay hits={hits} />}
          </div>
        )}

        {loading && (
          <div className="w-full max-w-4xl space-y-4">
            <div className="relative h-5 bg-zinc-900/80 rounded-full overflow-hidden border border-green-900/30 shadow-inner">
              <div
                className="h-full rounded-full relative transition-all duration-700 ease-out"
                style={{
                  width: `${Math.max(progress, 2)}%`,
                  background: "linear-gradient(90deg, #15803d 0%, #22c55e 50%, #4ade80 100%)",
                  boxShadow: "0 0 16px rgba(34,197,94,0.4), inset 0 1px 0 rgba(255,255,255,0.15)",
                }}
              >
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-green-300 animate-pulse shadow-lg shadow-green-400/60" />
              </div>
              <div className="absolute inset-0 flex items-center px-2">
                {Array.from({ length: 40 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex-1 h-full border-r border-green-950/40"
                    style={{ opacity: progress > (i / 40) * 100 ? 0.4 : 0.1 }}
                  />
                ))}
              </div>
            </div>
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-mono text-green-400/70">{status}</span>
              <span className="text-xs font-mono text-green-400/70">{progress}%</span>
            </div>
          </div>
        )}

        {error && !loading && (
          <div className="text-center text-sm text-red-400 bg-red-400/10 rounded-xl p-4 border border-red-400/20">
            {error}
          </div>
        )}

        {hits.length > 0 && (
          <div className="w-full max-w-4xl bg-[var(--bg-card)] rounded-2xl p-6 border border-white/5">
            <h2 className="text-lg font-semibold mb-4">Hasil Deteksi</h2>
            <div className="grid grid-cols-3 gap-4 text-center mb-4">
              {[
                { label: "Kick", count: hits.filter(h => h.label === "kick").length, color: "var(--drum-kick, #ef4444)" },
                { label: "Snare", count: hits.filter(h => h.label === "snare").length, color: "var(--drum-snare, #22c55e)" },
                { label: "Hi-Hat", count: hits.filter(h => h.label === "hi-hat").length, color: "var(--drum-hi-hat, #3b82f6)" },
              ].map(d => (
                <div key={d.label} className="bg-[var(--bg-primary)] rounded-xl p-3">
                  <div className="text-2xl font-bold" style={{ color: d.color }}>{d.count}</div>
                  <div className="text-xs text-[var(--text-secondary)] mt-1">{d.label}</div>
                </div>
              ))}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {hits.map((h, i) => {
                const colorMap: Record<string, string> = { kick: "#ef4444", snare: "#22c55e", "hi-hat": "#3b82f6" }
                return (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                    style={{ backgroundColor: colorMap[h.label] + "20", color: colorMap[h.label], border: `1px solid ${colorMap[h.label]}40` }}
                  >
                    <span style={{ color: colorMap[h.label] }}>●</span>
                    {h.time.toFixed(2)}s
                  </span>
                )
              })}
            </div>
          </div>
        )}
      </div>

      <footer className="mt-auto pt-16 pb-6 text-xs text-[var(--text-secondary)] text-center">
        Drumfillfinder &mdash; MVP
      </footer>
    </main>
  )
}
