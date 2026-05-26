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
  const [hits, setHits] = useState<Hit[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = useCallback((file: File) => {
    setError(null)
    setHits([])
    setTaskId(null)
    setStatus("")
    setAudioFile(file)
    setAudioUrl(URL.createObjectURL(file))
  }, [])

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
      setStatus("Memproses...")
      pollStatus(data.task_id)
    } catch (e: any) {
      setError(e.message || "Upload gagal")
      setStatus("")
      setLoading(false)
    }
  }, [audioFile])

  const pollStatus = useCallback(async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${id}`)
        if (!res.ok) { clearInterval(interval); return }
        const data = await res.json()
        setStatus(`Memproses... ${data.progress}%`)
        if (data.status === "SUCCESS") {
          clearInterval(interval)
          setStatus("Selesai!")
          fetchResult(id)
        } else if (data.status === "FAILURE") {
          clearInterval(interval)
          setStatus("Gagal")
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

        {audioUrl && (
          <div className="relative bg-[var(--bg-card)] rounded-2xl p-4 border border-white/5">
            <WaveformViewer audioUrl={audioUrl} hits={hits} />
            {hits.length > 0 && <DrumHitsOverlay hits={hits} />}
          </div>
        )}

        {status && (
          <div className="text-center text-sm text-[var(--text-secondary)]">
            {status}
            {loading && <span className="ml-2 inline-block animate-pulse">●</span>}
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
