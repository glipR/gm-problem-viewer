import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Group,
  Text,
  Badge,
  Accordion,
  Tooltip,
  Alert,
  Loader,
  Stack,
} from '@mantine/core'
import { IconPlayerPlay, IconAlertTriangle } from '@tabler/icons-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { notifications } from '@mantine/notifications'
import type { JobStatus, Problem, Validator, ValidatorResult } from '../../types/problem'
import { runValidators, getLatestValidatorJob } from '../../api/problems'
import { useJobPoller } from '../../hooks/useJobPoller'

interface Props {
  problem: Problem
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function groupBySet(results: ValidatorResult[]): Map<string, ValidatorResult[]> {
  const map = new Map<string, ValidatorResult[]>()
  for (const r of results) {
    const list = map.get(r.test_set) ?? []
    list.push(r)
    map.set(r.test_set, list)
  }
  return map
}

// ---------------------------------------------------------------------------
// ValidatorResults — panel body showing per-set grouped pass/fail badges
// ---------------------------------------------------------------------------

function ValidatorResults({
  results,
  isRunning,
}: {
  results: ValidatorResult[] | null
  isRunning: boolean
}) {
  if (!results || results.length === 0) {
    if (isRunning) {
      return (
        <Group gap="xs" py={4}>
          <Loader size="xs" />
          <Text size="xs" c="dimmed">Running…</Text>
        </Group>
      )
    }
    return (
      <Text size="xs" c="dimmed" fs="italic">
        No results yet — run validators to see per-test results.
      </Text>
    )
  }

  const bySet = groupBySet(results)

  return (
    <Stack gap={8}>
      {[...bySet.entries()].map(([setName, setResults]) => {
        const allPassed = setResults.every((r) => r.passed)
        return (
          <Box key={setName}>
            <Group gap={6} mb={4} align="center">
              <Text size="xs" fw={600} style={{ fontFamily: 'monospace' }}>
                {setName}
              </Text>
              <Badge size="xs" color={allPassed ? 'green' : 'red'} variant="light">
                {allPassed ? 'PASS' : 'FAIL'}
              </Badge>
              {isRunning && <Loader size={10} />}
            </Group>
            <Group gap={4} wrap="wrap">
              {setResults.map((r) => (
                <Tooltip
                  key={r.test_case}
                  label={`${r.test_case}: ${r.passed ? 'PASS' : 'FAIL'}${r.error ? ` — ${r.error}` : ''}`}
                  withArrow
                  multiline
                  maw={320}
                >
                  <Badge
                    size="xs"
                    color={r.passed ? 'green' : 'red'}
                    variant={r.passed ? 'dot' : 'filled'}
                    style={{ fontFamily: 'monospace', cursor: 'default' }}
                  >
                    {r.test_case}
                  </Badge>
                </Tooltip>
              ))}
            </Group>
          </Box>
        )
      })}
    </Stack>
  )
}

// ---------------------------------------------------------------------------
// ValidatorItem
// ---------------------------------------------------------------------------

function ValidatorItem({
  validator,
  results,
  isRunning,
}: {
  validator: Validator
  results: ValidatorResult[] | null
  isRunning: boolean
}) {
  const hasFailed = results ? results.some((r) => !r.passed) : false

  return (
    <Accordion.Item value={validator.path}>
      <Accordion.Control>
        <Group justify="space-between" wrap="nowrap" pr="xs">
          <Group gap="xs" wrap="nowrap" style={{ minWidth: 0 }}>
            <Text size="sm" fw={500} truncate style={{ flexShrink: 0 }}>
              {validator.name}
            </Text>
            {validator.description && (
              <Text size="xs" c="dimmed" truncate style={{ opacity: 0.7 }}>
                — {validator.description}
              </Text>
            )}
          </Group>
          <Group gap={6} wrap="nowrap" style={{ flexShrink: 0 }}>
            {validator.checks && validator.checks.length > 0 && (
              <Group gap={4}>
                {validator.checks.map((set) => (
                  <Badge key={set} size="xs" variant="outline" color="blue">
                    {set}
                  </Badge>
                ))}
              </Group>
            )}
            {results && (
              <Badge size="xs" color={hasFailed ? 'red' : 'green'} variant="filled">
                {isRunning ? '…' : hasFailed ? 'FAIL' : 'PASS'}
              </Badge>
            )}
            {isRunning && !results && <Loader size={12} />}
          </Group>
        </Group>
      </Accordion.Control>
      <Accordion.Panel>
        <Box px="xs" py="sm">
          {validator.description && (
            <Text size="sm" c="dimmed" style={{ marginBottom: '10px', whiteSpace: 'pre-wrap' }}>
              {validator.description}
            </Text>
          )}
          <Text size="xs" c="dimmed" mb={6} tt="uppercase" fw={600}>
            Test results from most recent run
          </Text>
          <ValidatorResults results={results} isRunning={isRunning} />
        </Box>
      </Accordion.Panel>
    </Accordion.Item>
  )
}

// ---------------------------------------------------------------------------
// ValidatorsTab
// ---------------------------------------------------------------------------

export default function ValidatorsTab({ problem }: Props) {
  const [activeJobId, setActiveJobId] = useState<string | null>(null)
  const qc = useQueryClient()

  const { data: latestJob, isLoading } = useQuery({
    queryKey: ['validator-latest', problem.slug],
    queryFn: () => getLatestValidatorJob(problem.slug),
  })

  const { data: jobData } = useJobPoller(activeJobId, {
    onDone: (job: JobStatus) => {
      if (job.status === 'done') {
        notifications.show({ message: 'Validator run complete', color: 'green' })
      } else {
        notifications.show({ message: 'Validator run failed', color: 'red' })
      }
      setActiveJobId(null)
      qc.invalidateQueries({ queryKey: ['validator-latest', problem.slug] })
    },
    onPoll: () => {
      qc.invalidateQueries({ queryKey: ['validator-latest', problem.slug] })
    },
  })

  // Live job data overlays the persisted latest job while a run is active
  const currentJob = jobData ?? latestJob ?? null
  const jobIsRunning = currentJob?.status === 'running' || currentJob?.status === 'pending'
  const allResults: ValidatorResult[] =
    (currentJob?.result as { results?: ValidatorResult[] })?.results ?? []

  function getResultsForValidator(path: string): ValidatorResult[] | null {
    if (allResults.length === 0) return null
    const filtered = allResults.filter((r) => r.validator === path)
    return filtered.length > 0 ? filtered : null
  }

  // A validator is still "running" if the job is active and it hasn't produced results yet
  function isValidatorRunning(path: string): boolean {
    if (!jobIsRunning) return false
    return allResults.filter((r) => r.validator === path).length === 0
  }

  const { mutate: runAll, isPending: runAllPending } = useMutation({
    mutationFn: () => runValidators(problem.slug),
    onSuccess: (data) => setActiveJobId(data.job_ids[0]),
    onError: () =>
      notifications.show({ message: 'Failed to start validator run', color: 'red' }),
  })

  const validators = problem.validators.input

  if (validators.length === 0) {
    return (
      <Box p="xl">
        <Alert icon={<IconAlertTriangle size={16} />} color="gray" title="No validators">
          No input validator files found under validators/input/.
        </Alert>
      </Box>
    )
  }

  return (
    <Box p="xl">
      <Group mb="md" justify="space-between">
        <Button
          size="xs"
          leftSection={<IconPlayerPlay size={14} />}
          loading={runAllPending}
          onClick={() => runAll()}
        >
          Run All Validators
        </Button>
        {(isLoading || jobIsRunning) && (
          <Group gap="xs">
            <Loader size="xs" />
            <Text size="xs" c="dimmed">
              {isLoading ? 'Loading results…' : 'Job running…'}
            </Text>
          </Group>
        )}
      </Group>

      <Accordion variant="contained" radius="sm">
        {validators.map((validator) => (
          <ValidatorItem
            key={validator.path}
            validator={validator}
            results={getResultsForValidator(validator.path)}
            isRunning={isValidatorRunning(validator.path)}
          />
        ))}
      </Accordion>
    </Box>
  )
}
