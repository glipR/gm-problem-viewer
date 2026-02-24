import { Badge, Card, Group, Progress, Stack, Text, Tooltip } from '@mantine/core'
import type { Problem } from '../../types/problem'
import FacetIcons from './FacetIcons'

const STATE_COLORS: Record<string, string> = {
  draft: 'gray',
  'in-progress': 'blue',
  review: 'orange',
  archive: 'violet',
}

interface Props {
  problem: Problem
  onSelect?: (slug: string) => void
}

export default function StaticProblemCard({ problem, onSelect }: Props) {
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
        <Group justify="space-between" align="flex-start" wrap="nowrap">
          <Text size="xs" c="dimmed" style={{ fontFamily: 'monospace' }}>
            {problem.slug}
          </Text>
          <Group gap={4} wrap="nowrap">
            <Badge
              size="xs"
              variant="dot"
              color={STATE_COLORS[problem.config.state] ?? 'gray'}
            >
              {problem.config.state}
            </Badge>
            {problem.config.tags.map((tag) => (
              <Badge key={tag} size="xs" variant="light">
                {tag}
              </Badge>
            ))}
            {problem.config.difficulty != null && (
              <Badge size="xs" variant="filled" color="indigo">
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
        <Tooltip label="Run Review to see check progress" withArrow>
          <Progress value={0} size="xs" color="green" />
        </Tooltip>

        {/* Facet icons */}
        <FacetIcons problem={problem} />
      </Stack>
    </Card>
  )
}
