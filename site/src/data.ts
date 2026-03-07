import type { ProblemSummary, ProblemData } from './types'

const BASE = import.meta.env.BASE_URL

export async function fetchIndex(): Promise<ProblemSummary[]> {
  const res = await fetch(`${BASE}data/index.json`)
  if (!res.ok) throw new Error('Failed to load problem index')
  return res.json()
}

export async function fetchProblem(slug: string): Promise<ProblemData> {
  const res = await fetch(`${BASE}data/${slug}/data.json`)
  if (!res.ok) throw new Error(`Failed to load problem: ${slug}`)
  return res.json()
}
