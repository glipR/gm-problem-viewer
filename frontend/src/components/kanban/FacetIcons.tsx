import { Group, Tooltip } from '@mantine/core'
import {
  IconFileText,
  IconCode,
  IconShield,
  IconDatabase,
} from '@tabler/icons-react'
import type { Problem } from '../../types/problem'

interface Props {
  problem: Problem
}

export default function FacetIcons({ problem }: Props) {
  const hasStatement = true // always assumed present
  const hasSolutions = problem.solutions.length > 0
  const hasValidators = problem.validators.input.length > 0
  const hasTests = problem.test_sets.length > 0

  const color = (present: boolean) => (present ? 'teal' : 'gray')

  return (
    <Group gap={6}>
      <Tooltip label="Statement">
        <IconFileText size={16} color={`var(--mantine-color-${color(hasStatement)}-6)`} />
      </Tooltip>
      <Tooltip label="Solutions">
        <IconCode size={16} color={`var(--mantine-color-${color(hasSolutions)}-6)`} />
      </Tooltip>
      <Tooltip label="Validators">
        <IconShield size={16} color={`var(--mantine-color-${color(hasValidators)}-6)`} />
      </Tooltip>
      <Tooltip label="Tests">
        <IconDatabase size={16} color={`var(--mantine-color-${color(hasTests)}-6)`} />
      </Tooltip>
    </Group>
  )
}
