interface Hit {
  time: number
  label: string
}

interface Props {
  hits: Hit[]
}

const LABEL_COLORS: Record<string, string> = {
  kick: "#ef4444",
  snare: "#22c55e",
  "hi-hat": "#3b82f6",
}

const LABEL_ICONS: Record<string, string> = {
  kick: "🥁",
  snare: "🛢️",
  "hi-hat": "🔔",
}

export default function DrumHitsOverlay({ hits }: Props) {
  if (hits.length === 0) return null

  return (
    <div className="mt-4">
      <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Timeline Ketukan</h3>
      <div className="flex flex-wrap gap-2">
        {hits.map((hit, i) => (
          <div
            key={i}
            className="group relative flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium transition-transform hover:scale-105"
            style={{
              backgroundColor: LABEL_COLORS[hit.label] + "15",
              color: LABEL_COLORS[hit.label],
              border: `1px solid ${LABEL_COLORS[hit.label]}30`,
            }}
          >
            <span>{LABEL_ICONS[hit.label] || "●"}</span>
            <span className="tabular-nums">{hit.time.toFixed(2)}s</span>
          </div>
        ))}
      </div>
    </div>
  )
}
