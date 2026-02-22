import { Box, Button, Group, Text, Badge, Accordion, ActionIcon, Tooltip, Alert } from '@mantine/core'
import { IconPlayerPlay, IconAlertTriangle } from '@tabler/icons-react'
import { useMutation } from '@tanstack/react-query'
import { notifications } from '@mantine/notifications'
import type { Problem, Solution } from '../../types/problem'
import { runSolutions } from '../../api/problems'

interface Props {
  problem: Problem
}

function verdictColor(verdict: string): string {
  switch (verdict.toUpperCase()) {
    case 'AC': return 'green'
    case 'WA': return 'red'
    case 'TLE': return 'orange'
    case 'RE': return 'yellow'
    default: return 'gray'
  }
}

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

function SolutionItem({ solution, slug }: { solution: Solution; slug: string }) {
  const { mutate: run, isPending } = useMutation({
    mutationFn: () => runSolutions(slug, { solution_paths: [solution.path] }),
    onSuccess: () =>
      notifications.show({ message: `Running ${solution.name}…`, color: 'blue' }),
    onError: () =>
      notifications.show({ message: 'Solution running not yet implemented', color: 'orange' }),
  })

  const langColor = solution.language === 'cpp' ? 'orange' : 'blue'

  return (
    <Accordion.Item value={solution.path}>
      <Accordion.Control>
        <Group justify="space-between" wrap="nowrap" pr="xs">
          <Group gap="xs" wrap="nowrap" style={{ minWidth: 0 }}>
            {solution.language && (
              <Badge size="xs" variant="dot" color={langColor} style={{ flexShrink: 0 }}>
                {solution.language}
              </Badge>
            )}
            <Text size="sm" fw={500} truncate>
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
            <Tooltip label={`Run ${solution.name}`}>
              <ActionIcon
                size="xs"
                variant="subtle"
                loading={isPending}
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
          <Text size="xs" c="dimmed" mb={4} tt="uppercase" fw={600}>
            Test results from most recent run
          </Text>
          <Text size="xs" c="dimmed" fs="italic">
            No results yet — run this solution to see per-test verdicts grouped by test set.
          </Text>
        </Box>
      </Accordion.Panel>
    </Accordion.Item>
  )
}

export default function SolutionsTab({ problem }: Props) {
  const { mutate: runAll, isPending } = useMutation({
    mutationFn: () =>
      runSolutions(problem.slug, {
        solution_paths: problem.solutions.map((s) => s.path),
      }),
    onSuccess: () =>
      notifications.show({ message: 'Running all solutions…', color: 'blue' }),
    onError: () =>
      notifications.show({ message: 'Solution running not yet implemented', color: 'orange' }),
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
      <Group mb="md">
        <Button
          size="xs"
          leftSection={<IconPlayerPlay size={14} />}
          loading={isPending}
          onClick={() => runAll()}
        >
          Run All Solutions
        </Button>
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
              <SolutionItem key={sol.path} solution={sol} slug={problem.slug} />
            ))}
          </Accordion>
        </Box>
      ))}
    </Box>
  )
}
