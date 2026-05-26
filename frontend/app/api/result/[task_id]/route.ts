import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.BACKEND_URL || "http://backend:8000"

export async function GET(request: NextRequest, { params }: { params: { task_id: string } }) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/result/${params.task_id}`)
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 })
  }
}
