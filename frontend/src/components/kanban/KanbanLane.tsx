import { Paper, Stack, Text, UnstyledButton } from '@mantine/core'
import { IconPlus } from '@tabler/icons-react'
import { useDroppable } from '@dnd-kit/core'
import type { Problem } from '../../types/problem'
import ProblemCard from './ProblemCard'

interface Props {
  id: string
  label: string
  problems: Problem[]
  onProblemClick: (slug: string) => void
  onCreateClick?: () => void
}

export default function KanbanLane({ id, label, problems, onProblemClick, onCreateClick }: Props) {
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
        {onCreateClick && (
          <UnstyledButton
            onClick={onCreateClick}
            style={{
              border: '2px dashed var(--mantine-color-gray-4)',
              borderRadius: 'var(--mantine-radius-md)',
              padding: 'var(--mantine-spacing-sm)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--mantine-color-gray-5)',
              cursor: 'pointer',
              transition: 'border-color 150ms ease, color 150ms ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--mantine-color-blue-4)'
              e.currentTarget.style.color = 'var(--mantine-color-blue-5)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--mantine-color-gray-4)'
              e.currentTarget.style.color = 'var(--mantine-color-gray-5)'
            }}
          >
            <IconPlus size={20} />
          </UnstyledButton>
        )}
      </Stack>
    </Paper>
  )
}
