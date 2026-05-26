import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Drumfillfinder",
  description: "Analisis ketukan drum dari potongan lagu",
  icons: { icon: "/favicon.png" },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  )
}
