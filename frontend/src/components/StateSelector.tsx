import { Badge, Menu } from '@mantine/core'
import type { ProblemState } from '../types/problem'
import { usePatchProblemState } from '../hooks/useProblems'

const STATES: { value: ProblemState; label: string; color: string }[] = [
  { value: 'draft', label: 'Draft', color: 'gray' },
  { value: 'in-progress', label: 'In Progress', color: 'blue' },
  { value: 'review', label: 'Review', color: 'orange' },
  { value: 'complete', label: 'Complete', color: 'green' },
  { value: 'archive', label: 'Archive', color: 'gray' },
]

export const STATE_COLORS: Record<string, string> = Object.fromEntries(
  STATES.map((s) => [s.value, s.color]),
)

interface Props {
  slug: string
  currentState: ProblemState
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
}

export default function StateSelector({ slug, currentState, size = 'xs' }: Props) {
  const { mutate: patchState } = usePatchProblemState()

  return (
    <Menu shadow="md" width={160} position="bottom-start" withinPortal>
      <Menu.Target>
        <Badge
          circle
          size={size}
          color={STATE_COLORS[currentState] ?? 'gray'}
          style={{ cursor: 'pointer' }}
          onClick={(e: React.MouseEvent) => e.stopPropagation()}
        />
      </Menu.Target>
      <Menu.Dropdown onClick={(e: React.MouseEvent) => e.stopPropagation()}>
        <Menu.Label>Change state</Menu.Label>
        {STATES.map((s) => (
          <Menu.Item
            key={s.value}
            leftSection={<Badge circle size="xs" color={s.color} />}
            disabled={s.value === currentState}
            onClick={() => patchState({ slug, state: s.value })}
          >
            {s.label}
          </Menu.Item>
        ))}
      </Menu.Dropdown>
    </Menu>
  )
}
