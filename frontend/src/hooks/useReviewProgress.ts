import { useQuery } from '@tanstack/react-query'
import { getLatestReviewJob } from '../api/problems'
import type { ReviewJobResult, CategoryResult } from '../types/problem'

const TERMINAL = new Set(['done', 'failed'])

export type ReviewColor = 'green' | 'yellow' | 'red' | 'gray'

export function useReviewProgress(slug: string) {
  const query = useQuery({
    queryKey: ['latest-review-job', slug],
    queryFn: () => getLatestReviewJob(slug),
    refetchInterval: (q) => {
      const data = q.state.data
      if (!data) return false
      if (TERMINAL.has(data.status)) return false
      return 2000
    },
  })

  const job = query.data ?? null
  const result = job?.result as ReviewJobResult | null | undefined

  const total = (result?.phase1?.num_tests ?? 0) + (result?.phase2?.num_tests ?? 0)
  const passed = (result?.phase1?.passed ?? 0) + (result?.phase2?.passed ?? 0)
  const progress = total > 0 ? Math.round((passed / total) * 100) : 0

  const phase1Failed = (result?.phase1?.num_tests ?? 0) > 0 && (result?.phase1?.passed ?? 0) < (result?.phase1?.num_tests ?? 0)
  const phase2Failed = (result?.phase2?.num_tests ?? 0) > 0 && (result?.phase2?.passed ?? 0) < (result?.phase2?.num_tests ?? 0)

  let color: ReviewColor = 'gray'
  if (total > 0) {
    if (phase1Failed) color = 'red'
    else if (phase2Failed) color = 'yellow'
    else color = 'green'
  }

  const issues = [
    ...(result?.phase1?.issues ?? []),
    ...(result?.phase2?.issues ?? []),
  ]

  const byCategory: Record<string, CategoryResult> | null = result?.by_category ?? null

  return { progress, color, issues, job, byCategory }
}
