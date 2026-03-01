import { Badge, Card, Group, Progress, Stack, Text, Tooltip, ActionIcon } from '@mantine/core'
import { IconUpload } from '@tabler/icons-react'
import { useDraggable } from '@dnd-kit/core'
import { CSS } from '@dnd-kit/utilities'
import type { Problem } from '../../types/problem'
import FacetIcons from './FacetIcons'
import { useReviewProgress } from '../../hooks/useReviewProgress'

interface Props {
  problem: Problem
  onSelect?: (slug: string) => void
}

export default function ProblemCard({ problem, onSelect }: Props) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: problem.slug,
  })
  const { progress, color, issues, byCategory } = useReviewProgress(problem.slug)

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.4 : 1,
    cursor: isDragging ? 'grabbing' : 'grab',
  }

  return (
    <Card
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      withBorder
      padding="sm"
      radius="md"
      shadow="xs"
      onClick={() => onSelect?.(problem.slug)}
    >
      <Stack gap={6}>
        {/* Top row: slug + contest badges + difficulty */}
        <Group justify="space-between" align="flex-start" wrap="nowrap" gap={4}>
          <Text size="xs" c="dimmed" style={{ fontFamily: 'monospace' }}>
            {problem.slug}
          </Text>
          {problem.config.contests?.map((c) => (
            <Badge key={c} size="xs" variant="light" color="grape">
              {c}
            </Badge>
          ))}
          <div style={{flexGrow: 1}} />
          {problem.config.difficulty != null && (
            <Badge size="xs" variant="filled" color="indigo">
              {problem.config.difficulty}
            </Badge>
          )}
        </Group>

        {/* Problem title + tag badges */}
        <Group gap={6} align="center" wrap="nowrap">
          <Text fw={600} size="sm" lineClamp={2} style={{ flexShrink: 1, minWidth: 0 }}>
            {problem.config.name}
          </Text>
          <div style={{flexGrow: 1}} />
          <Group gap={4} wrap="nowrap" style={{ flexShrink: 0 }}>
            {problem.config.tags.map((tag) => (
              <Badge key={tag} size="xs" variant="light">
                {tag}
              </Badge>
            ))}
          </Group>
        </Group>

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

        {/* Bottom row: facet icons + export */}
        <Group justify="space-between" align="center">
          <FacetIcons problem={problem} byCategory={byCategory} />
          <Tooltip label="Export">
            <ActionIcon
              size="sm"
              variant="subtle"
              color="gray"
              onPointerDown={(e) => e.stopPropagation()}
              onClick={(e) => {
                e.stopPropagation()
                // TODO: trigger export
              }}
            >
              <IconUpload size={14} />
            </ActionIcon>
          </Tooltip>
        </Group>
      </Stack>
    </Card>
  )
}
