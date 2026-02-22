import { Paper, Stack, Text } from '@mantine/core'
import { useDroppable } from '@dnd-kit/core'
import type { Problem } from '../../types/problem'
import ProblemCard from './ProblemCard'

interface Props {
  id: string
  label: string
  problems: Problem[]
  onProblemClick: (slug: string) => void
}

export default function KanbanLane({ id, label, problems, onProblemClick }: Props) {
  const { setNodeRef, isOver } = useDroppable({ id })

  return (
    <Paper
      ref={setNodeRef}
      p="md"
      radius="md"
      style={{
        background: isOver
          ? 'var(--mantine-color-blue-0)'
          : 'var(--mantine-color-gray-0)',
        minHeight: 400,
        transition: 'background 150ms ease',
      }}
    >
      <Stack gap="sm">
        <Text fw={700} size="sm" tt="uppercase" c="dimmed">
          {label}
          <Text component="span" c="gray" fw={400} ml={6}>
            ({problems.length})
          </Text>
        </Text>
        {problems.map((p) => (
          <ProblemCard key={p.slug} problem={p} onSelect={onProblemClick} />
        ))}
      </Stack>
    </Paper>
  )
}
