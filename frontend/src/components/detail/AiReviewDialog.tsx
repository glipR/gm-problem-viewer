import { Modal, Stack, Group, Text, Loader, ThemeIcon, Divider } from '@mantine/core'
import { IconBrain, IconCircleCheck, IconCircleX, IconClock } from '@tabler/icons-react'
import { useJobPoller } from '../../hooks/useJobPoller'
import type { AiReviewCheck, AiReviewResult } from '../../types/problem'

/** The 5 checks in execution order — used to show pending placeholders. */
const DEFAULT_CHECK_NAMES = [
  'Output Validator Alignment',
  'Input Validator Coverage',
  'Boundary Test Coverage',
  'Statement Spelling',
  'Solution Optimality',
]

interface Props {
  jobId: string
  slug: string
  onClose: () => void
  /** Override the list of expected check names (defaults to the full AI review set). */
  checkNames?: string[]
}

export function AiReviewDialog({ jobId, slug, onClose, checkNames }: Props) {
  const allCheckNames = checkNames ?? DEFAULT_CHECK_NAMES
  const { data: job } = useJobPoller(jobId)

  const result = job?.result as AiReviewResult | undefined
  const completedChecks: AiReviewCheck[] = result?.checks ?? []
  const completedNames = new Set(completedChecks.map((c) => c.name))

  const isDone = job?.status === 'done'
  const isFailed = job?.status === 'failed'

  return (
    <Modal
      opened
      onClose={onClose}
      title={
        <Group gap="xs">
          <IconBrain size={18} />
          <Text fw={600}>AI Review</Text>
          {!isDone && !isFailed && <Loader size={14} />}
        </Group>
      }
      size="lg"
      centered
    >
      <Stack gap="sm">
        {allCheckNames.map((name) => {
          const check = completedChecks.find((c) => c.name === name)
          const isRunning =
            !completedNames.has(name) &&
            !isDone &&
            !isFailed &&
            completedChecks.length === allCheckNames.indexOf(name)

          return (
            <div key={name}>
              <Group gap="xs" wrap="nowrap" align="flex-start">
                <div style={{ width: 20, flexShrink: 0, paddingTop: 2 }}>
                  {check ? (
                    check.summary.startsWith('Error:') ? (
                      <IconCircleX size={16} color="var(--mantine-color-red-6)" />
                    ) : (
                      <IconCircleCheck size={16} color="var(--mantine-color-green-6)" />
                    )
                  ) : isRunning ? (
                    <Loader size={14} />
                  ) : (
                    <IconClock size={16} color="var(--mantine-color-gray-4)" />
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <Text size="sm" fw={500}>
                    {name}
                  </Text>
                  {check && (
                    <Text
                      size="xs"
                      c={check.summary.startsWith('Error:') ? 'red' : 'dimmed'}
                      mt={2}
                    >
                      {check.summary}
                    </Text>
                  )}
                </div>
              </Group>
              {name !== allCheckNames[allCheckNames.length - 1] && (
                <Divider mt="sm" />
              )}
            </div>
          )
        })}

        {isFailed && job?.error && (
          <Text size="sm" c="red" mt="xs">
            Job failed: {job.error}
          </Text>
        )}
      </Stack>
    </Modal>
  )
}
