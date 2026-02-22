import { Badge, Card, Group, Progress, Stack, Text, Tooltip, ActionIcon } from '@mantine/core'
import { IconUpload } from '@tabler/icons-react'
import { useDraggable } from '@dnd-kit/core'
import { CSS } from '@dnd-kit/utilities'
import type { Problem } from '../../types/problem'
import FacetIcons from './FacetIcons'

interface Props {
  problem: Problem
  onSelect?: (slug: string) => void
}

export default function ProblemCard({ problem, onSelect }: Props) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: problem.slug,
  })

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
        {/* Top row: slug + tags + difficulty */}
        <Group justify="space-between" align="flex-start" wrap="nowrap">
          <Text size="xs" c="dimmed" style={{ fontFamily: 'monospace' }}>
            {problem.slug}
          </Text>
          <Group gap={4} wrap="nowrap">
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

        {/* Bottom row: facet icons + export */}
        <Group justify="space-between" align="center">
          <FacetIcons problem={problem} />
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
