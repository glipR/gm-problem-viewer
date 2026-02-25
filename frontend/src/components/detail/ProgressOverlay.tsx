import { useEffect, useRef } from 'react'
import { Box, Paper, Text, Group, Progress, Loader, Portal, Stack } from '@mantine/core'
import { IconCircleCheck, IconCircleX, IconClock } from '@tabler/icons-react'
import { notifications } from '@mantine/notifications'
import { useQueries, useQueryClient } from '@tanstack/react-query'
import { getJob } from '../../api/problems'
import type { JobStatus } from '../../types/problem'

// ---------------------------------------------------------------------------
// Job step type enum + per-type config
// ---------------------------------------------------------------------------

export enum JobStepType {
  GENERATE_TESTS = 'generate_tests',
  RUN_VALIDATORS = 'run_validators',
  RUN_SOLUTION = 'run_solution',
  REVIEW_DETERMINISTIC = 'review-deterministic',
}

interface StepConfig {
  label: string
  /** Query keys to invalidate whenever this step's job data refreshes. */
  invalidates: (slug: string) => unknown[][]
}

const STEP_CONFIG: Record<JobStepType, StepConfig> = {
  [JobStepType.GENERATE_TESTS]: {
    label: 'Generating tests',
    invalidates: (slug) => [['test-sets', slug]],
  },
  [JobStepType.RUN_VALIDATORS]: {
    label: 'Running validators',
    invalidates: () => [],
  },
  [JobStepType.RUN_SOLUTION]: {
    label: 'Running solutions',
    invalidates: (slug) => [['solution-merged-results', slug]],
  },
  [JobStepType.REVIEW_DETERMINISTIC]: {
    label: 'Running checks',
    invalidates: (slug) => [['latest-review-job', slug]],
  },
}

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface JobStep {
  jobId: string
  type: JobStepType
}

interface Props {
  steps: JobStep[]
  slug: string
  onDone: () => void
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const TERMINAL = new Set(['done', 'failed'])

function PhaseRow({ label, status }: { label: string; status?: string }) {
  let icon: React.ReactNode
  let color: string

  switch (status) {
    case 'running':
      icon = <Loader size={12} />
      color = 'blue'
      break
    case 'done':
      icon = <IconCircleCheck size={14} color="var(--mantine-color-green-6)" />
      color = 'green'
      break
    case 'failed':
      icon = <IconCircleX size={14} color="var(--mantine-color-red-6)" />
      color = 'red'
      break
    default:
      icon = <IconClock size={14} color="var(--mantine-color-gray-5)" />
      color = 'dimmed'
  }

  return (
    <Group gap="xs" wrap="nowrap">
      <Box style={{ width: 14, flexShrink: 0, display: 'flex', alignItems: 'center' }}>
        {icon}
      </Box>
      <Text size="xs" c={color}>
        {label}
      </Text>
    </Group>
  )
}

// ---------------------------------------------------------------------------
// ProgressOverlay
// ---------------------------------------------------------------------------

export function ProgressOverlay({ steps, slug, onDone }: Props) {
  const qc = useQueryClient()
  const doneRef = useRef(false)
  const prevTimestamps = useRef<number[]>(steps.map(() => 0))

  const results = useQueries({
    queries: steps.map((step) => ({
      queryKey: ['job', step.jobId],
      queryFn: () => getJob(step.jobId),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      refetchInterval: (q: any) => {
        const status = (q.state.data as JobStatus | undefined)?.status
        return status && TERMINAL.has(status) ? false : 1500
      },
    })),
  })

  // On each new poll result, invalidate the query keys for that step type.
  const updatedAt = results.map((r) => r.dataUpdatedAt).join(',')
  useEffect(() => {
    results.forEach((result, i) => {
      const ts = result.dataUpdatedAt
      if (!ts || ts === prevTimestamps.current[i]) return
      prevTimestamps.current[i] = ts
      STEP_CONFIG[steps[i].type].invalidates(slug).forEach((key) =>
        qc.invalidateQueries({ queryKey: key as readonly unknown[] }),
      )
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [updatedAt])

  const statuses = results.map((r) => r.data?.status)
  const completedCount = statuses.filter((s) => s && TERMINAL.has(s)).length
  const progress = (completedCount / steps.length) * 100
  const allDone = completedCount === steps.length
  const anyFailed = statuses.some((s) => s === 'failed')

  // On full completion: final invalidations + notification + dismiss.
  useEffect(() => {
    if (!allDone || doneRef.current) return
    doneRef.current = true
    steps.forEach((step) =>
      STEP_CONFIG[step.type].invalidates(slug).forEach((key) =>
        qc.invalidateQueries({ queryKey: key as readonly unknown[] }),
      ),
    )
    qc.invalidateQueries({ queryKey: ['problem', slug] })
    notifications.show({
      message: anyFailed ? 'Pipeline run failed' : 'Pipeline complete',
      color: anyFailed ? 'red' : 'green',
    })
    setTimeout(onDone, 2000)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [allDone])

  return (
    <Portal>
      <Box style={{ position: 'fixed', bottom: 24, right: 24, width: 260, zIndex: 300 }}>
        <Paper shadow="md" p="md" withBorder radius="md">
          <Group justify="space-between" mb={10}>
            <Text size="sm" fw={600}>
              {allDone ? (anyFailed ? 'Run failed' : 'Run complete') : 'Running pipeline'}
            </Text>
            <Text size="xs" c="dimmed">
              {completedCount}/{steps.length}
            </Text>
          </Group>

          <Stack gap={6} mb={10}>
            {steps.map((step, i) => (
              <PhaseRow
                key={step.jobId}
                label={STEP_CONFIG[step.type].label}
                status={results[i]?.data?.status}
              />
            ))}
          </Stack>

          <Progress
            value={progress}
            size="sm"
            animated={!allDone}
            color={anyFailed ? 'red' : 'blue'}
          />
        </Paper>
      </Box>
    </Portal>
  )
}
