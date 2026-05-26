import { useCallback, useRef, useState } from "react"

interface Props {
  onFileSelect: (file: File) => void
  onUpload: () => void
  loading: boolean
  error: string | null
  hasFile: boolean
}

export default function Uploader({ onFileSelect, onUpload, loading, error, hasFile }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && validateFile(file)) onFileSelect(file)
  }, [onFileSelect])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && validateFile(file)) onFileSelect(file)
  }, [onFileSelect])

  const validateFile = (file: File): boolean => {
    const valid = ["audio/mpeg", "audio/wav", "audio/flac", "audio/x-wav", "audio/x-flac"]
    if (!valid.includes(file.type) && !file.name.match(/\.(mp3|wav|flac)$/i)) {
      alert("Hanya file mp3, wav, atau flac yang didukung.")
      return false
    }
    if (file.size > 10 * 1024 * 1024) {
      alert("File maksimal 10MB.")
      return false
    }
    return true
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`
        relative w-full border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer
        transition-all duration-200
        ${dragging ? "border-[var(--accent)] bg-[var(--accent)]/5 scale-[1.01]" : "border-white/10 hover:border-white/20"}
        ${hasFile ? "bg-[var(--bg-card)]" : ""}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".mp3,.wav,.flac"
        className="hidden"
        onChange={handleChange}
      />

      {!hasFile ? (
        <div className="space-y-3">
          <div className="text-4xl opacity-30">🎵</div>
          <p className="text-lg font-medium">Drop audio file di sini</p>
          <p className="text-sm text-[var(--text-secondary)]">
            atau klik untuk memilih file &bull; mp3, wav, flac &bull; maks 30 detik
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-[var(--text-secondary)]">File siap</div>
          <button
            onClick={(e) => { e.stopPropagation(); onUpload() }}
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-[var(--accent)] text-white font-medium
              hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {loading ? "Memproses..." : "Upload & Analisis"}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 text-sm text-red-400 bg-red-400/10 rounded-lg p-3">{error}</div>
      )}
    </div>
  )
}
