import { Card, Group, Progress, Stack, Text, Tooltip, Badge } from '@mantine/core'
import type { Problem } from '../../types/problem'
import FacetIcons from './FacetIcons'
import { useReviewProgress } from '../../hooks/useReviewProgress'
import StateSelector from '../StateSelector'

interface Props {
  problem: Problem
  onSelect?: (slug: string) => void
}

const staticOverflow = {
  label: {
    overflow: 'visible',
    textOverflow: 'clip',
    whiteSpace: 'nowrap'
  }
}

export default function StaticProblemCard({ problem, onSelect }: Props) {
  const { progress, color, issues, byCategory } = useReviewProgress(problem.slug)

  return (
    <Card
      withBorder
      padding="sm"
      radius="md"
      shadow="xs"
      style={{ cursor: 'pointer' }}
      onClick={() => onSelect?.(problem.slug)}
    >
      <Stack gap={6}>
        {/* Top row: slug + state badge + tags + difficulty */}
        <Group justify="space-between" align="flex-start" wrap="nowrap" gap={4}>
          <StateSelector slug={problem.slug} currentState={problem.config.state} size="xs" />
          <Text size="xs" c="dimmed" style={{ fontFamily: 'monospace' }}>
            {problem.slug}
          </Text>
          <div style={{flexGrow: 1 /* Spacer */}}></div>
          <Group gap={4} wrap="nowrap">
            {problem.config.tags.map((tag) => (
              <Badge key={tag} size="xs" variant="light">
                {tag}
              </Badge>
            ))}
            {problem.config.difficulty != null && (
              <Badge size="xs" variant="filled" color="indigo" styles={staticOverflow}>
                {problem.config.difficulty}
              </Badge>
            )}
          </Group>
        </Group>

        {/* Problem title */}
        <Text fw={600} size="sm" lineClamp={2}>
          {problem.config.name}
        </Text>

        {/* Progress bar */}
        <Tooltip
          label={
            issues.length > 0
              ? <Stack gap={1}>{issues.map((issue, i) => <Text key={i} size="xs">• {issue}</Text>)}</Stack>
              : progress > 0 ? 'All checks passing' : 'Run Review to see check progress'
          }
          withArrow
          multiline
          maw={280}
        >
          <Progress value={progress} size="xs" color={color} />
        </Tooltip>

        {/* Facet icons */}
        <FacetIcons problem={problem} byCategory={byCategory} />
      </Stack>
    </Card>
  )
}
