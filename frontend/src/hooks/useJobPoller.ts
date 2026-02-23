import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getJob } from '../api/problems'
import type { JobStatus } from '../types/problem'

const TERMINAL = new Set(['done', 'failed'])

/**
 * Poll GET /jobs/{jobId} at 1.5 s intervals until the job reaches a terminal
 * state (done | failed), then stop.  Calls onDone exactly once on transition.
 */
export function useJobPoller(
  jobId: string | null,
  { onDone }: { onDone?: (job: JobStatus) => void } = {},
) {
  // Keep onDone stable so the effect doesn't re-fire if the caller recreates it
  const onDoneRef = useRef(onDone)
  onDoneRef.current = onDone

  const query = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJob(jobId!),
    enabled: !!jobId,
    refetchInterval: (q) => {
      const status = q.state.data?.status
      return status && TERMINAL.has(status) ? false : 1500
    },
  })

  useEffect(() => {
    if (query.data && TERMINAL.has(query.data.status)) {
      onDoneRef.current?.(query.data)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query.data?.status])

  return query
}
