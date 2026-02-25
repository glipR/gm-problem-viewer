import { useState } from 'react'
import {
  Box,
  Group,
  Badge,
  Text,
  ActionIcon,
  Progress,
  Tooltip,
  Tabs,
  Center,
  Loader,
  Stack,
  Button,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import {
  IconArrowLeft,
  IconPlayerPlay,
  IconSearch,
  IconBrain,
  IconUpload,
} from '@tabler/icons-react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { getProblem, runProblem, reviewProblem, reviewProblemAI } from '../api/problems'
import FacetIcons from '../components/kanban/FacetIcons'
import StatementTab from '../components/detail/StatementTab'
import SolutionsTab from '../components/detail/SolutionsTab'
import TestsTab from '../components/detail/TestsTab'
import { ProgressOverlay, JobStepType } from '../components/detail/ProgressOverlay'
import { useReviewProgress } from '../hooks/useReviewProgress'

interface Props {
  slug: string
  onBack: () => void
}

const STATE_COLORS: Record<string, string> = {
  draft: 'gray',
  'in-progress': 'blue',
  review: 'yellow',
  complete: 'green',
}

export default function ProblemDetailPage({ slug, onBack }: Props) {
  const [runJobIds, setRunJobIds] = useState<[string, string, string] | null>(null)
  const [reviewJobId, setReviewJobId] = useState<string | null>(null)
  const { progress: reviewProgress, color: reviewColor, issues: reviewIssues, byCategory } = useReviewProgress(slug)

  const { data: problem, isLoading, isError } = useQuery({
    queryKey: ['problem', slug],
    queryFn: () => getProblem(slug),
  })

  const { mutate: run, isPending: runPending } = useMutation({
    mutationFn: () => runProblem(slug),
    onSuccess: (data) => {
      setRunJobIds(data.job_ids as [string, string, string])
    },
    onError: () => notifications.show({ message: 'Run not yet implemented', color: 'orange' }),
  })

  const { mutate: review, isPending: reviewPending } = useMutation({
    mutationFn: () => reviewProblem(slug),
    onSuccess: (data) => setReviewJobId(data.job_ids[0]),
    onError: () => notifications.show({ message: 'Review failed to start', color: 'red' }),
  })

  const { mutate: reviewAI, isPending: aiPending } = useMutation({
    mutationFn: () => reviewProblemAI(slug),
    onSuccess: () => notifications.show({ message: 'AI Review started', color: 'blue' }),
    onError: () =>
      notifications.show({ message: 'AI Review not yet implemented', color: 'orange' }),
  })

  if (isLoading) {
    return (
      <Center h="100vh">
        <Loader />
      </Center>
    )
  }

  if (isError || !problem) {
    return (
      <Center h="100vh">
        <Text c="red">Failed to load problem.</Text>
      </Center>
    )
  }

  const memMB = Math.round(problem.config.limits.memory / 1024)

  return (
    <Box style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                               */}
      {/* ------------------------------------------------------------------ */}
      <Box px="xl" pt="lg" pb={0}>
        <Stack gap="sm" pb="md">
          {/* Back + slug breadcrumb */}
          <Group gap="xs">
            <ActionIcon variant="subtle" color="gray" onClick={onBack} size="sm">
              <IconArrowLeft size={16} />
            </ActionIcon>
            <Text size="xs" c="dimmed" style={{ fontFamily: 'monospace' }}>
              {slug}
            </Text>
          </Group>

          {/* Title and basic info */}
          <Group gap={12} wrap="wrap">
            <Tooltip label={problem.config.state?.toUpperCase()}>
              <Badge circle size="md" color={STATE_COLORS[problem.config.state] ?? 'gray'}></Badge>
            </Tooltip>
            <Text size="xl" fw={700} lh={1.2}>
              {problem.config.name}
            </Text>
            <Badge
              size="sm"
              variant="outline"
              color={problem.config.type === 'interactive' ? 'violet' : 'blue'}
            >
              {problem.config.type}
            </Badge>
          </Group>

          {/* Badges row: difficulty, tags */}
          <Group justify="space-between" align="center">
            <Group gap={6} wrap="wrap">
              {problem.config.difficulty != null && (
                <Badge size="sm" variant="filled" color="indigo">
                  {problem.config.difficulty}
                </Badge>
              )}
              {problem.config.tags.map((tag) => (
                <Badge key={tag} size="sm" variant="light">
                  {tag}
                </Badge>
              ))}
            </Group>

            {/* Author + limits */}
            <Group gap="lg">
              <Text size="sm" c="dimmed">
                by{' '}
                <Text component="span" fw={500} c="inherit">
                  {problem.config.author}
                </Text>
              </Text>
              <Text size="sm" c="dimmed">
                {problem.config.limits.time}s / {memMB}MB
              </Text>
            </Group>
          </Group>

          {/* Facet icons + action buttons */}
          <Group justify="space-between" align="center">
            <Group gap="md">
              <FacetIcons problem={problem} byCategory={byCategory} />
            </Group>

            <Group gap="xs">
              <Button
                size="xs"
                leftSection={<IconPlayerPlay size={14} />}
                loading={runPending}
                onClick={() => run()}
              >
                Run
              </Button>
              <Button
                size="xs"
                variant="light"
                leftSection={<IconSearch size={14} />}
                loading={reviewPending}
                onClick={() => review()}
              >
                Review
              </Button>
              <Button
                size="xs"
                variant="light"
                color="violet"
                leftSection={<IconBrain size={14} />}
                loading={aiPending}
                onClick={() => reviewAI()}
              >
                AI Review
              </Button>
              <Button
                size="xs"
                variant="light"
                color="green"
                leftSection={<IconUpload size={14} />}
                onClick={() => notifications.show({ message: 'Export not yet implemented', color: 'orange' })}
              >
                Export
              </Button>
            </Group>
          </Group>
        </Stack>

        {/* Progress bar — this IS the bottom border of the header */}
        <Tooltip
          label={
            reviewIssues.length > 0
              ? <Stack gap={2}>{reviewIssues.map((issue, i) => <Text key={i} size="xs">• {issue}</Text>)}</Stack>
              : reviewProgress > 0 ? 'All checks passing' : 'Run Review to see which deterministic checks are passing'
          }
          withArrow
          position="bottom"
          multiline
          maw={320}
        >
          <Progress value={reviewProgress} size="sm" color={reviewColor} radius={0} />
        </Tooltip>
      </Box>

      {/* ------------------------------------------------------------------ */}
      {/* Tabs                                                                 */}
      {/* ------------------------------------------------------------------ */}
      <Tabs
        defaultValue="statement"
        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
      >
        <Tabs.List px="xl" style={{ borderBottom: '1px solid var(--mantine-color-gray-2)' }}>
          <Tabs.Tab value="statement">Statement</Tabs.Tab>
          <Tabs.Tab value="solutions">
            Solutions
            {problem.solutions.length > 0 && (
              <Text component="span" size="xs" c="dimmed" ml={4}>
                ({problem.solutions.length})
              </Text>
            )}
          </Tabs.Tab>
          <Tabs.Tab value="tests">
            Tests
            {problem.test_sets.length > 0 && (
              <Text component="span" size="xs" c="dimmed" ml={4}>
                ({problem.test_sets.length} sets)
              </Text>
            )}
          </Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="statement" style={{ flex: 1 }}>
          <StatementTab slug={slug} />
        </Tabs.Panel>

        <Tabs.Panel value="solutions" style={{ flex: 1 }}>
          <SolutionsTab problem={problem} />
        </Tabs.Panel>

        <Tabs.Panel value="tests" style={{ flex: 1 }}>
          <TestsTab problem={problem} />
        </Tabs.Panel>
      </Tabs>

      {runJobIds && (
        <ProgressOverlay
          key={runJobIds.join(',')}
          steps={[
            { jobId: runJobIds[0], type: JobStepType.GENERATE_TESTS },
            { jobId: runJobIds[1], type: JobStepType.RUN_VALIDATORS },
            { jobId: runJobIds[2], type: JobStepType.RUN_SOLUTION },
          ]}
          slug={slug}
          onDone={() => setRunJobIds(null)}
        />
      )}

      {reviewJobId && (
        <ProgressOverlay
          key={reviewJobId}
          steps={[{ jobId: reviewJobId, type: JobStepType.REVIEW_DETERMINISTIC }]}
          slug={slug}
          onDone={() => setReviewJobId(null)}
        />
      )}
    </Box>
  )
}
