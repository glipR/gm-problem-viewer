import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Group,
  Text,
  Badge,
  Accordion,
  ActionIcon,
  Tooltip,
  Alert,
  Loader,
  Stack,
} from '@mantine/core'
import { IconPlayerPlay, IconAlertTriangle, IconBrandPython, IconBrandCpp, IconQuestionMark } from '@tabler/icons-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { notifications } from '@mantine/notifications'
import type {
  JobStatus,
  Problem,
  Solution,
  SolutionRunResult,
  Verdict,
} from '../../types/problem'
import { runSolutions, getMergedResults } from '../../api/problems'
import { useJobPoller } from '../../hooks/useJobPoller'

interface Props {
  problem: Problem
}

interface ActiveRun {
  jobId: string
  paths: string[]
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function languageIcon(language: string) {
  switch(language) {
    case 'python': return <IconBrandPython size={24} color='#4B8BBE'/>
    case 'cpp': return <IconBrandCpp size={24} color='#F77F00'/>
    default: return <IconQuestionMark size={24} color='#444444'/>
  }
}

function verdictColor(verdict: string): string {
  switch (verdict.toUpperCase()) {
    case 'AC':  return 'green'
    case 'WA':  return 'red'
    case 'TLE': return 'orange'
    case 'RTE':
    case 'RE':  return 'yellow'
    default:    return 'gray'
  }
}

function groupBySet(verdicts: Verdict[]): Map<string, Verdict[]> {
  const map = new Map<string, Verdict[]>()
  for (const v of verdicts) {
    const list = map.get(v.test_set) ?? []
    list.push(v)
    map.set(v.test_set, list)
  }
  return map
}

function setOverall(verdicts: Verdict[]): string {
  const nonAC = verdicts.find((v) => v.verdict !== 'AC')
  return nonAC ? nonAC.verdict : 'AC'
}

function groupByFolder(solutions: Solution[]): [string, Solution[]][] {
  const map = new Map<string, Solution[]>()
  for (const sol of solutions) {
    const parts = sol.path.split('/')
    const folder = parts.length > 1 ? parts[0] : ''
    const existing = map.get(folder) ?? []
    existing.push(sol)
    map.set(folder, existing)
  }
  return [...map.entries()].sort(([a], [b]) => a.localeCompare(b))
}

// ---------------------------------------------------------------------------
// ExpectationBadges
// ---------------------------------------------------------------------------

function ExpectationBadges({ expectation }: { expectation: Solution['expectation'] }) {
  if (typeof expectation === 'string') {
    return (
      <Badge size="xs" color={verdictColor(expectation)} variant="light">
        {expectation}
      </Badge>
    )
  }
  return (
    <Group gap={4} wrap="nowrap">
      {expectation.map((e) => {
        const [set, verdict] = Object.entries(e)[0]
        return (
          <Badge key={set} size="xs" color={verdictColor(verdict)} variant="light">
            {set}: {verdict}
          </Badge>
        )
      })}
    </Group>
  )
}

// ---------------------------------------------------------------------------
// SolutionResults — panel body showing per-set grouped verdicts
// ---------------------------------------------------------------------------

function SolutionResults({
  result,
  isRunning,
}: {
  result: SolutionRunResult | null
  isRunning: boolean
}) {
  if (!result || result.verdicts.length === 0) {
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
        No results yet — run this solution to see per-test verdicts grouped by test set.
      </Text>
    )
  }

  const bySet = groupBySet(result.verdicts)

  return (
    <Stack gap={8}>
      {[...bySet.entries()].map(([setName, verdicts]) => {
        const overall = setOverall(verdicts)
        return (
          <Box key={setName}>
            <Group gap={6} mb={4} align="center">
              <Text size="xs" fw={600} style={{ fontFamily: 'monospace' }}>
                {setName}
              </Text>
              <Badge size="xs" color={verdictColor(overall)} variant="light">
                {overall}
              </Badge>
              {isRunning && <Loader size={10} />}
            </Group>
            <Group gap={4} wrap="wrap">
              {verdicts.map((v) => (
                <Tooltip
                  key={v.test_case}
                  label={`${v.test_case}: ${v.verdict}${v.comment ? ` — ${v.comment}` : ''}`}
                  withArrow
                >
                  <Badge
                    size="xs"
                    color={verdictColor(v.verdict)}
                    variant={v.verdict === 'AC' ? 'dot' : 'filled'}
                    style={{ fontFamily: 'monospace', cursor: 'default' }}
                  >
                    {v.test_case}
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
// SolutionItem
// ---------------------------------------------------------------------------

function SolutionItem({
  solution,
  slug,
  result,
  isRunning,
  onRunStarted,
}: {
  solution: Solution
  slug: string
  result: SolutionRunResult | null
  isRunning: boolean
  onRunStarted: (jobId: string, paths: string[]) => void
}) {
  const { mutate: run, isPending } = useMutation({
    mutationFn: () => runSolutions(slug, { solution_paths: [solution.path] }),
    onSuccess: (data) => {
      onRunStarted(data.job_ids[0], [solution.path])
    },
    onError: () =>
      notifications.show({ message: 'Failed to start solution run', color: 'red' }),
  })

  return (
    <Accordion.Item value={solution.path}>
      <Accordion.Control>
        <Group justify="space-between" wrap="nowrap" pr="xs">
          <Group gap="xs" wrap="nowrap" style={{ minWidth: 0 }}>
            <Group style={{flexShrink: 0}}>
              {solution.language && <>{languageIcon(solution.language)}</>}
            </Group>
            <Text size="sm" fw={500} truncate style={{flexShrink: 0}}>
              {solution.name}
            </Text>
            {solution.description && (
              <Text size="xs" c="dimmed" truncate style={{ opacity: 0.7 }}>
                — {solution.description}
              </Text>
            )}
          </Group>
          <Group gap={6} wrap="nowrap" style={{ flexShrink: 0 }} onClick={(e) => e.stopPropagation()}>
            <ExpectationBadges expectation={solution.expectation} />
            {result && (
              <Badge
                size="xs"
                color={verdictColor(result.overall)}
                variant="filled"
              >
                {isRunning ? '…' : result.overall}
              </Badge>
            )}
            {isRunning && !result && <Loader size={12} />}
            <Tooltip label={`Run ${solution.name}`}>
              <ActionIcon
                size="xs"
                variant="subtle"
                loading={isPending}
                disabled={isRunning}
                onClick={(e) => {
                  e.stopPropagation()
                  run()
                }}
              >
                <IconPlayerPlay size={12} />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Group>
      </Accordion.Control>
      <Accordion.Panel>
        <Box px="xs" py="sm">
          {solution.description && <Text size="sm" c="dimmed" style={{marginBottom: '10px', whiteSpace: "pre-wrap"}}>
            { solution.description }
          </Text> }
          <Text size="xs" c="dimmed" mb={6} tt="uppercase" fw={600}>
            Test results from most recent run
          </Text>
          <SolutionResults result={result} isRunning={isRunning} />
        </Box>
      </Accordion.Panel>
    </Accordion.Item>
  )
}

// ---------------------------------------------------------------------------
// SolutionsTab
// ---------------------------------------------------------------------------

export default function SolutionsTab({ problem }: Props) {
  const [activeRun, setActiveRun] = useState<ActiveRun | null>(null)
  const qc = useQueryClient()

  // Merged base results: latest group run + latest individual run per solution,
  // newest updated_at wins for any given solution path.
  const { data: mergedResults, isLoading: mergedLoading } = useQuery({
    queryKey: ['solution-merged-results', problem.slug],
    queryFn: () => getMergedResults(problem.slug),
  })

  // Poll the active job; on completion clear the live overlay and refresh merged results
  const { data: jobData } = useJobPoller(activeRun?.jobId ?? null, {
    onDone: (job: JobStatus) => {
      if (job.status === "done") {
        notifications.show({ message: 'Run complete', color: 'green' })
      } else {
        notifications.show({ message: 'Failed to run solutions', color: 'red' })
      }
      setActiveRun(null)
      qc.invalidateQueries({ queryKey: ['solution-merged-results', problem.slug] })
    },
    onPoll: () => {
      qc.invalidateQueries({ queryKey: ['solution-merged-results', problem.slug] })
    }
  })

  const jobStatus = jobData?.status
  const jobIsRunning = jobStatus === 'running' || jobStatus === 'pending'

  // Live job data overlays the merged base while a job is active
  function getResult(path: string): SolutionRunResult | null {
    return (
      mergedResults?.solutions.find((s) => s.solution_path === path) ??
      null
    )
  }

  function isSolutionRunning(path: string): boolean {
    return mergedResults?.solutions.find(s => s.solution_path === path)?.overall === 'PD'
  }

  function handleRunStarted(jobId: string, paths: string[]) {
    setActiveRun({ jobId, paths })
  }

  const { mutate: runAll, isPending: runAllPending } = useMutation({
    mutationFn: () =>
      runSolutions(problem.slug, {
        solution_paths: problem.solutions.map((s) => s.path),
      }),
    onSuccess: (data) => {
      handleRunStarted(data.job_ids[0], problem.solutions.map((s) => s.path))
    },
    onError: () =>
      notifications.show({ message: 'Failed to start solution run', color: 'red' }),
  })

  if (problem.solutions.length === 0) {
    return (
      <Box p="xl">
        <Alert icon={<IconAlertTriangle size={16} />} color="gray" title="No solutions">
          No solution files found under solutions/.
        </Alert>
      </Box>
    )
  }

  const groups = groupByFolder(problem.solutions)

  return (
    <Box p="xl">
      <Group mb="md" justify="space-between">
        <Button
          size="xs"
          leftSection={<IconPlayerPlay size={14} />}
          loading={runAllPending}
          onClick={() => runAll()}
        >
          Run All Solutions
        </Button>
        {(mergedLoading || jobIsRunning) && (
          <Group gap="xs">
            <Loader size="xs" />
            <Text size="xs" c="dimmed">
              {mergedLoading ? 'Loading results…' : 'Job running…'}
            </Text>
          </Group>
        )}
      </Group>

      {groups.map(([folder, solutions]) => (
        <Box key={folder || '__root__'} mb="md">
          <Text
            size="xs"
            fw={700}
            c="dimmed"
            tt="uppercase"
            mb={6}
            style={{ fontFamily: 'monospace', letterSpacing: '0.05em' }}
          >
            {folder ? `${folder}/` : 'solutions/'}
          </Text>
          <Accordion variant="contained" radius="sm">
            {solutions.map((sol) => (
              <SolutionItem
                key={sol.path}
                solution={sol}
                slug={problem.slug}
                result={getResult(sol.path)}
                isRunning={isSolutionRunning(sol.path)}
                onRunStarted={handleRunStarted}
              />
            ))}
          </Accordion>
        </Box>
      ))}
    </Box>
  )
}
